from __future__ import annotations

from copy import deepcopy
from typing import Any

_ALLOWED_KINDS = {"start", "stage", "gate", "tool", "approval", "stop"}
_NODE_KEYS = {"id", "kind", "label", "x", "y", "tool"}
_EDGE_KEYS = {"from", "to"}
_SIZE_BY_KIND = {
    "start": (180, 96),
    "stage": (210, 96),
    "gate": (180, 120),
    "tool": (210, 72),
    "approval": (180, 120),
    "stop": (180, 96),
}


class MapValidationError(ValueError):
    """The payload does not match the neutral process-map contract."""


def validate_map(process_map: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(process_map, dict) or set(process_map) != {"nodes", "edges"}:
        raise MapValidationError("map must contain exactly nodes and edges")
    nodes = process_map["nodes"]
    edges = process_map["edges"]
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise MapValidationError("nodes and edges must be arrays")

    ids: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict) or not set(node).issubset(_NODE_KEYS):
            raise MapValidationError("each node must use only id, kind, label, x, y, and optional tool")
        required = {"id", "kind", "label", "x", "y"}
        if not required.issubset(node):
            raise MapValidationError(f"node missing fields: {sorted(required - set(node))}")
        node_id = node["id"]
        if not isinstance(node_id, str) or not node_id or node_id in ids:
            raise MapValidationError(f"node id must be unique and non-empty: {node_id!r}")
        ids.add(node_id)
        if node["kind"] not in _ALLOWED_KINDS:
            raise MapValidationError(f"node {node_id} has unknown kind: {node['kind']!r}")
        if not isinstance(node["label"], str) or not node["label"]:
            raise MapValidationError(f"node {node_id} label must be non-empty")
        if any(not isinstance(node[key], (int, float)) or isinstance(node[key], bool) for key in ("x", "y")):
            raise MapValidationError(f"node {node_id} x and y must be numbers")
        if "tool" in node and (not isinstance(node["tool"], str) or not node["tool"]):
            raise MapValidationError(f"node {node_id} tool must be a non-empty string")

    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != _EDGE_KEYS:
            raise MapValidationError("each edge must contain exactly from and to")
        if edge["from"] not in ids or edge["to"] not in ids:
            raise MapValidationError(f"edge endpoint missing: {edge!r}")
    return deepcopy(process_map)


def node_to_shape(
    node: dict[str, Any],
    *,
    frame_id: str = "frame:map",
    offset_x: float = 0,
    offset_y: float = 0,
) -> dict[str, Any]:
    width, height = _SIZE_BY_KIND[node["kind"]]
    shape = {
        "id": f"{frame_id}:node:{node['id']}",
        "node_id": node["id"],
        "frame_id": frame_id,
        "kind": node["kind"],
        "label": node["label"],
        "x": node["x"] + offset_x,
        "y": node["y"] + offset_y,
        "map_x": node["x"],
        "map_y": node["y"],
        "w": width,
        "h": height,
    }
    if "tool" in node:
        shape["tool"] = node["tool"]
    return shape


def map_to_shapes(
    process_map: dict[str, Any],
    *,
    frame_id: str = "frame:map",
    origin_x: float = 0,
    origin_y: float = 0,
    parent_frame: str | None = None,
    title: str = "PROCESS MAP",
) -> dict[str, Any]:
    neutral = validate_map(process_map)
    min_x = min((node["x"] for node in neutral["nodes"]), default=0)
    min_y = min((node["y"] for node in neutral["nodes"]), default=0)
    max_x = max((node["x"] + _SIZE_BY_KIND[node["kind"]][0] for node in neutral["nodes"]), default=800)
    max_y = max((node["y"] + _SIZE_BY_KIND[node["kind"]][1] for node in neutral["nodes"]), default=500)
    offset_x = origin_x - min_x + 80
    offset_y = origin_y - min_y + 100
    frame = {
        "id": frame_id,
        "kind": "frame",
        "label": title,
        "x": origin_x,
        "y": origin_y,
        "w": max_x - min_x + 160,
        "h": max_y - min_y + 200,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "parent_frame": parent_frame,
    }
    return {
        "version": 1,
        "revision": 0,
        "shapes": [
            frame,
            *(node_to_shape(node, frame_id=frame_id, offset_x=offset_x, offset_y=offset_y) for node in neutral["nodes"]),
        ],
        "connections": [
            {**edge, "frame_id": frame_id}
            for edge in deepcopy(neutral["edges"])
        ],
        "focused_ids": [],
        "active_frame_id": frame_id,
    }


def shapes_to_map(canvas_state: dict[str, Any], frame_id: str | None = None) -> dict[str, Any]:
    shapes = canvas_state.get("shapes")
    connections = canvas_state.get("connections")
    if not isinstance(shapes, list) or not isinstance(connections, list):
        raise MapValidationError("canvas state must contain shapes and connections arrays")
    selected_frame = frame_id or canvas_state.get("active_frame_id")
    nodes: list[dict[str, Any]] = []
    ids: set[str] = set()
    for shape in shapes:
        if not isinstance(shape, dict) or shape.get("kind") not in _ALLOWED_KINDS:
            continue
        if selected_frame and shape.get("frame_id") != selected_frame:
            continue
        node_id = shape.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            raise MapValidationError("canvas shape is missing node_id")
        node = {
            "id": node_id,
            "kind": shape["kind"],
            "label": shape.get("label"),
            "x": shape.get("map_x", shape.get("x")),
            "y": shape.get("map_y", shape.get("y")),
        }
        if "tool" in shape:
            node["tool"] = shape["tool"]
        nodes.append(node)
        ids.add(node_id)
    edges = [
        {"from": edge.get("from"), "to": edge.get("to")}
        for edge in connections
        if isinstance(edge, dict)
        and (not selected_frame or edge.get("frame_id") == selected_frame)
        and edge.get("from") in ids
        and edge.get("to") in ids
    ]
    return validate_map({"nodes": nodes, "edges": edges})
