import networkx as nx
import turicreate as tc
from repoze.lru import lru_cache
from configs import *

class FieldsHierarchyAnalyzer(object):
    def __init__(self, min_confidence=0.8):
        self._g = FieldsHierarchyAnalyzer.create_fields_of_study_graph(min_confidence)


    def is_field_in_level(self, field_id, level):
        return level in self._g.node[field_id]['levels']

    def get_field_levels(self, field_id):
        return self._g.node[field_id]['levels']



    def get_field_name(self, field_id):
        if not self._g.has_node(field_id):
            return None
        return self._g.node[field_id]['Name']

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

    @staticmethod
    def create_fields_of_study_graph( min_confidence=0.8):
        g = nx.DiGraph()
        h_sf = tc.load_sframe(FIELDS_OF_STUDY_HIERARCHY_SFRAME)
        h_sf = h_sf[h_sf['Confidence'] >= min_confidence]
        f_sf = tc.load_sframe(FIELDS_OF_STUDY_SFRAME)
        h_sf = h_sf.join(f_sf, on={'Child field of study ID':'Field of study ID'}, how='left')
        h_sf = h_sf.rename({'Field of study name':'Child field of study name'})
        h_sf = h_sf.join(f_sf, on={'Parent field of study ID':'Field of study ID'}, how='left')
        h_sf = h_sf.rename({'Field of study name':'Parent field of study name'})
        for r in h_sf:
            v = r['Parent field of study ID']
            u = r['Child field of study ID']
            g.add_edge(v, u)
            if 'levels' not in g.node[v]:
                g.node[v]['levels'] = set()
            l = int(r['Parent field of study level'].replace("L", ""))
            g.node[v]['levels'].add(l)
            g.node[v]['Name'] = r['Parent field of study name']

            if 'levels' not in g.node[u]:
                g.node[u]['levels'] = set()
            l = int(r['Child field of study level'].replace("L", ""))
            g.node[u]['levels'].add(l)
            g.node[u]['Name'] = r['Child field of study name']

        return g

    @staticmethod
    def is_higher_level(levels_list, search_level):
        l = [i for i in list(levels_list) if i > search_level]
        return len(l) > 0
