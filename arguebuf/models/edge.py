from __future__ import absolute_import, annotations

import typing as t

import graphviz as gv
import networkx as nx
import pendulum
from arg_services.graph.v1 import graph_pb2
from arguebuf.models import Userdata
from arguebuf.models.metadata import Metadata
from arguebuf.models.node import Node
from arguebuf.schema import aif, ova, sadface
from arguebuf.services import dt, utils
import xml.etree.ElementTree as ET


class Edge:
    """Edge in AIF format. Connection from one Node object to another Node object."""

    __slots__ = (
        "_id",
        "_source",
        "_target",
        "metadata",
        "userdata",
    )

    _id: str
    _source: Node
    _target: Node
    metadata: Metadata
    userdata: Userdata

    def __init__(
        self,
        source: Node,
        target: Node,
        metadata: t.Optional[Metadata] = None,
        userdata: t.Optional[Userdata] = None,
        id: t.Optional[str] = None,
    ):
        # if isinstance(source, AtomNode) and isinstance(target, AtomNode):
        #     raise ValueError("Cannot create an edge between two atom nodes.")

        self._id = id or utils.uuid()
        self._source = source
        self._target = target
        self.metadata = metadata or Metadata()
        self.userdata = userdata or {}

        self.__post_init__()

    def __post_init__(self):
        pass

    def __repr__(self):
        return utils.class_repr(
            self,
            [str(self._id), f"{self._source.__repr__()}->{self._target.__repr__()}",],
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def source(self) -> Node:
        """Gives the 'From'-Node."""
        return self._source

    @property
    def target(self) -> Node:
        """Gives the 'To'-Node."""
        return self._target

    @classmethod
    def from_sadface(
        cls, obj: sadface.Edge, nodes: t.Mapping[str, Node],
    ) -> t.Optional[Edge]:
        """Generate Edge object from SADFace Edge format."""
        source_id = obj.get("source_id")
        target_id = obj.get("target_id")

        if source_id in nodes and target_id in nodes:
            return cls(id=obj["id"], source=nodes[source_id], target=nodes[target_id],)

        return None

    @classmethod
    def from_ova(cls, obj: ova.Edge, nodes: t.Mapping[str, Node],) -> t.Optional[Edge]:
        """Generate Edge object from OVA Edge format."""
        source_id = str(obj["from"]["id"])
        target_id = str(obj["to"]["id"])
        date = dt.from_format(obj.get("date"), ova.DATE_FORMAT) or pendulum.now()

        if source_id in nodes and target_id in nodes:
            return cls(
                id=utils.uuid(),
                source=nodes[source_id],
                target=nodes[target_id],
                metadata=Metadata(date, date),
            )

        return None

    @classmethod
    def from_aif(cls, obj: aif.Edge, nodes: t.Mapping[str, Node],) -> t.Optional[Edge]:
        """Generate Edge object from AIF Edge format."""
        source_id = obj.get("fromID")
        target_id = obj.get("toID")

        if source_id in nodes and target_id in nodes:
            return cls(
                id=obj["edgeID"], source=nodes[source_id], target=nodes[target_id],
            )

        return None

    def to_aif(self) -> aif.Edge:
        """Export Edge object into AIF Edge format."""
        return {
            "edgeID": str(self.id),
            "fromID": str(self.source.id),
            "toID": str(self.target.id),
            "formEdgeID": None,
        }

    @classmethod
    def from_protobuf(
        cls, id: str, obj: graph_pb2.Edge, nodes: t.Mapping[str, Node],
    ) -> Edge:
        """Generate Edge object from PROTOBUF Edge format."""
        return cls(
            nodes[obj.source],
            nodes[obj.target],
            Metadata.from_protobuf(obj.metadata),
            dict(obj.userdata.items()),
            id=id,
        )

    def to_protobuf(self) -> graph_pb2.Edge:
        """Export Edge object into PROTOBUF Edge format."""
        obj = graph_pb2.Edge(
            source=self._source.id,
            target=self._target.id,
            metadata=self.metadata.to_protobuf(),
        )
        obj.userdata.update(self.userdata)

        return obj

    def to_nx(
        self,
        g: nx.DiGraph,
        attrs: t.Optional[t.MutableMapping[str, t.Callable[[Edge], t.Any]]] = None,
    ) -> None:
        """Submethod used to export Graph object g into NX Graph format."""

        if attrs is None:
            attrs = {}

        g.add_edge(
            self.source.id,
            self.target.id,
            **{key: func(self) for key, func in attrs.items()},
        )

    def to_gv(self, g: gv.Digraph) -> None:
        """Submethod used to export Graph object g into GV Graph format."""
        g.edge(
            self.source._id, self.target._id,
        )
