import networkx as nx
import turicreate as tc
from functools import lru_cache


class FieldsHierarchyAnalyzer(object):
    def __init__(self, mag, min_confidence=0.8):
        self._mag = mag
        self._g = self.create_fields_of_study_graph(min_confidence)

    def is_field_in_level(self, field_id, level):
        return level in self._g.nodes[field_id]['levels']

    def get_field_levels(self, field_id):
        return self._g.nodes[field_id]['levels']

    def get_field_name(self, field_id):
        if not self._g.has_node(field_id):
            return None
        return self._g.nodes[field_id]['Name']

    @lru_cache(maxsize=1000000)
    def get_parents_field_of_study(self, field_id, parent_level):
        if not self._g.has_node(field_id):
            return set()

        levels = self.get_field_levels(field_id)
        if parent_level in levels:
            return {field_id}

        if not FieldsHierarchyAnalyzer.is_higher_level(levels, parent_level):
            return set()

        ids = set()
        for n in self._g.predecessors(field_id):
            ids |= self.get_parents_field_of_study(n, parent_level)

        return ids

    def create_fields_of_study_graph(self, min_confidence=0.8):
        g = nx.DiGraph()
        h_sf = self._mag.field_of_study_children
        f_sf = self._mag.fields_of_study[["FieldOfStudyId","DisplayName","Level"]]
        h_sf = h_sf.join(f_sf, on={'FieldOfStudyId': 'FieldOfStudyId'}, how='left')
        h_sf = h_sf.rename({'DisplayName': 'Parent field of study name', "Level":"PLevel"})
        h_sf = h_sf.join(f_sf, on={'ChildFieldOfStudyId': 'FieldOfStudyId'}, how='left')
        h_sf = h_sf.rename({'DisplayName': 'Child field of study name',"Level":"CLevel"})

        for r in h_sf:
            v = r['FieldOfStudyId']
            u = r['ChildFieldOfStudyId']
            g.add_edge(v, u)
            if 'levels' not in g.nodes[v]:
                g.nodes[v]['levels'] = set()
            l = int(r['PLevel'])
            g.nodes[v]['levels'].add(l)
            g.nodes[v]['Name'] = r['Parent field of study name']

            if 'levels' not in g.nodes[u]:
                g.nodes[u]['levels'] = set()
            l = int(r['CLevel'])
            g.nodes[u]['levels'].add(l)
            g.nodes[u]['Name'] = r['Child field of study name']

        return g

    @staticmethod
    def is_higher_level(levels_list, search_level):
        l = [i for i in list(levels_list) if i > search_level]
        return len(l) > 0
