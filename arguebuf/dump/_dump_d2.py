import textwrap
import typing as t

from arguebuf.model import Graph
from arguebuf.model.edge import Edge
from arguebuf.model.node import AtomNode, SchemeNode, AbstractNode
from arguebuf.schemas.d2 import D2Graph, D2Edge, D2Node, D2Style


def dump_d2(
    graph: Graph,
    atom_label: t.Optional[t.Callable[[AtomNode], str]] = None,
    scheme_label: t.Optional[t.Callable[[SchemeNode], str]] = None,
    max_nodes: t.Optional[int] = None,
) -> t.Optional[D2Graph]:
    if len(graph.nodes) > (max_nodes or 1000):
        return None

    d2_graph = D2Graph(
        nodes=[],
        edges=[],
    )

    for node in graph._atom_nodes.values():
        _dump_node(
            node,
            d2_graph,
            major_claim=graph.major_claim == node,
            label_func=atom_label,
        )

    for node in graph._scheme_nodes.values():
        _dump_node(
            node,
            d2_graph,
            label_func=scheme_label,
            major_claim=False,
        )

    for edge in graph._edges.values():
        _dump_edge(edge, d2_graph)

    return d2_graph


def _dump_node(
    node: AbstractNode,
    g: D2Graph,
    major_claim: bool,
    label_func: t.Optional[t.Callable[[AbstractNode], str]] = None,
) -> None:
    label: str = label_func(node) if label_func else node.label
    label = label.replace("\n", "")
    if type(node) == AtomNode:
        color = node.color(major_claim)
    else:
        color = node.color(major_claim=False)

    nodeStyle: D2Style = D2Style(
        font_color=color.fg,
        stroke_width=2,
        bold=False,
        stroke=color.border,
        fill=color.bg,
    )

    g.nodes.append(
        D2Node(
            id=node.id,
            label=label,
            shape="rectangle",
            style=nodeStyle,
        )
    )


def _dump_edge(edge: Edge, g: D2Graph) -> None:
    """Submethod used to export Graph object g into D2 Graph format."""
    g.edges.append(D2Edge(from_id=edge.source.id, to_id=edge.target.id))
