from pydantic import Field

from lionagi.utils.call_utils import l_call
from lionagi.schema.base_schema import BaseNode
from .relationship import Relationship



class Structure(BaseNode):
    nodes: dict = Field(default={})
    relationships: dict = Field(default={})
    node_relationships: dict = Field(default={})

    def add_node(self, node: BaseNode):
        self.nodes[node.id_] = node
        self.node_relationships[node.id_] = {'in': {}, 'out': {}}

    def add_relationship(self, relationships: Relationship):
        if relationships.source_node_id not in self.node_relationships.keys():
            raise ValueError(f'node {relationships.source_node_id} is not found.')
        if relationships.target_node_id not in self.node_relationships.keys():
            raise ValueError(f'node {relationships.target_node_id} is not found.')

        self.relationships[relationships.id_] = relationships
        self.node_relationships[relationships.source_node_id]['out'][relationships.id_] = relationships.target_node_id
        self.node_relationships[relationships.target_node_id]['in'][relationships.id_] = relationships.source_node_id

    def get_node_relationships(self, node: BaseNode = None, out_edge=True):
        if node is None:
            return list(self.relationships.values())

        if node.id_ not in self.nodes.keys():
            raise KeyError(f'node {node.id_} is not found')

        if out_edge:
            relationship_ids = list(self.node_relationships[node.id_]['out'].keys())
            relationships = l_call(relationship_ids, lambda i: self.relationships[i])
            return relationships
        else:
            relationship_ids = list(self.node_relationships[node.id_]['in'].keys())
            relationships = l_call(relationship_ids, lambda i: self.relationships[i])
            return relationships

    def remove_node(self, node: BaseNode):
        if node.id_ not in self.nodes.keys():
            raise KeyError(f'node {node.id_} is not found')

        out_relationship = self.node_relationships[node.id_]['out']
        for relationship_id, node_id in out_relationship.items():
            self.node_relationships[node_id]['in'].pop(relationship_id)
            self.relationships.pop(relationship_id)

        in_relationship = self.node_relationships[node.id_]['in']
        for relationship_id, node_id in in_relationship.items():
            self.node_relationships[node_id]['out'].pop(relationship_id)
            self.relationships.pop(relationship_id)

        self.node_relationships.pop(node.id_)
        return self.nodes.pop(node.id_)

    def remove_relationship(self, relationship: Relationship):
        if relationship.id_ not in self.relationships.keys():
            raise KeyError(f'relationship {relationship.id_} is not found')

        self.node_relationships[relationship.source_node_id]['out'].pop(relationship.id_)
        self.node_relationships[relationship.target_node_id]['in'].pop(relationship.id_)

        return self.relationships.pop(relationship.id_)

    def node_exists(self, node: BaseNode):
        if node.id_ in self.nodes.keys():
            return True
        else:
            return False

    def relationship_exists(self, relationship: Relationship):
        if relationship.id_ in self.relationships.keys():
            return True
        else:
            return False
        