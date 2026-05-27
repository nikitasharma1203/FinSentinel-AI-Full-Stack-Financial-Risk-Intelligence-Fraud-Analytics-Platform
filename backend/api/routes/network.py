"""Financial Network Intelligence — API Routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
import uuid
import networkx as nx

from database.connection import get_db
from models.orm_models import NetworkEdge, Transaction, Customer

router = APIRouter()


@router.get("/graph")
async def get_network_graph(
    min_risk: float = 0.0,
    suspicious_only: bool = False,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    """Return nodes and edges for the transaction network graph."""
    query = db.query(NetworkEdge).filter(NetworkEdge.risk_score >= min_risk)
    if suspicious_only:
        query = query.filter(NetworkEdge.is_suspicious == True)

    edges = query.order_by(desc(NetworkEdge.risk_score)).limit(limit).all()

    nodes_set = set()
    edge_list = []
    for e in edges:
        src = str(e.source_id)
        tgt = str(e.target_id)
        nodes_set.add((src, e.source_type))
        nodes_set.add((tgt, e.target_type))
        edge_list.append({
            "source": src,
            "target": tgt,
            "transaction_count": e.transaction_count,
            "total_amount": e.total_amount,
            "risk_score": e.risk_score,
            "is_suspicious": e.is_suspicious,
        })

    return {
        "nodes": [{"id": nid, "type": ntype} for nid, ntype in nodes_set],
        "edges": edge_list,
    }


@router.get("/centrality")
async def get_centrality_scores(limit: int = 20, db: Session = Depends(get_db)):
    """Compute degree centrality to find high-influence nodes."""
    edges = db.query(NetworkEdge).limit(500).all()

    G = nx.DiGraph()
    for e in edges:
        G.add_edge(str(e.source_id), str(e.target_id), weight=e.risk_score)

    if len(G.nodes) == 0:
        return []

    centrality = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, k=min(50, len(G.nodes)))

    scores = [
        {
            "node_id": node,
            "degree_centrality": round(centrality.get(node, 0), 4),
            "betweenness_centrality": round(betweenness.get(node, 0), 4),
            "combined_score": round(
                centrality.get(node, 0) * 0.5 + betweenness.get(node, 0) * 0.5, 4
            ),
        }
        for node in G.nodes
    ]
    scores.sort(key=lambda x: x["combined_score"], reverse=True)
    return scores[:limit]


@router.get("/clusters")
async def get_suspicious_clusters(db: Session = Depends(get_db)):
    """Detect fraud rings using community detection."""
    suspicious_edges = (
        db.query(NetworkEdge)
        .filter(NetworkEdge.is_suspicious == True)
        .limit(300)
        .all()
    )

    G = nx.Graph()
    for e in suspicious_edges:
        G.add_edge(str(e.source_id), str(e.target_id))

    if len(G.nodes) == 0:
        return {"clusters": [], "total_suspicious_nodes": 0}

    components = list(nx.connected_components(G))
    clusters = [
        {
            "cluster_id": i,
            "size": len(c),
            "nodes": list(c),
            "risk_level": "CRITICAL" if len(c) > 10 else "HIGH" if len(c) > 5 else "MEDIUM",
        }
        for i, c in enumerate(sorted(components, key=len, reverse=True))
        if len(c) > 1
    ]

    return {
        "clusters": clusters,
        "total_suspicious_nodes": len(G.nodes),
        "total_clusters": len(clusters),
    }


@router.get("/propagation/{node_id}")
async def get_risk_propagation(node_id: str, depth: int = 2, db: Session = Depends(get_db)):
    """Trace risk propagation from a given node."""
    edges = db.query(NetworkEdge).limit(500).all()

    G = nx.DiGraph()
    for e in edges:
        G.add_edge(
            str(e.source_id),
            str(e.target_id),
            risk=e.risk_score,
            amount=e.total_amount,
        )

    if node_id not in G:
        return {"node_id": node_id, "propagation": [], "affected_nodes": 0}

    reachable = nx.single_source_shortest_path(G, node_id, cutoff=depth)
    propagation = []
    for target, path in reachable.items():
        if target == node_id:
            continue
        edge_risks = []
        for i in range(len(path) - 1):
            data = G.get_edge_data(path[i], path[i + 1]) or {}
            edge_risks.append(data.get("risk", 0))
        propagation.append({
            "target_node": target,
            "path": path,
            "hops": len(path) - 1,
            "cumulative_risk": round(sum(edge_risks) / max(len(edge_risks), 1), 4),
        })

    propagation.sort(key=lambda x: x["cumulative_risk"], reverse=True)
    return {
        "node_id": node_id,
        "propagation": propagation[:50],
        "affected_nodes": len(propagation),
    }
