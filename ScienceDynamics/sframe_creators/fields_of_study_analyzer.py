from code.consts import *
from code.sframe_creators.fields_of_study_hieararchy_analyzer import FieldsHierarchyAnalyzer


class FieldsOfStduyAnalyzer(object):
    def __init__(self):
        self._fh = None

    def get_fields_of_study_dict(self, papers_features_sframe):
        d = {}

        for flevel in range(3):
            col_name = "Fields of study parent list (L%s)" % flevel
            for r in papers_features_sframe:
                p_id = r['Paper ID']
                f_list = r[col_name]
                if f_list is None or len(f_list) == 0:
                    continue
                for f in f_list:
                    if f not in d:
                        d[f] = {'name': self.fields_hierarchy_analyzer.get_field_name(f),
                                'levels': {flevel},
                                'papers_ids': []
                                }
                    d[f]['papers_ids'].append(p_id)
                    d[f]['levels'].add(flevel)
        return d

    @property
    def fields_hierarchy_analyzer(self):
        if self._fh is None:
            self._fh = FieldsHierarchyAnalyzer()
        return self._fh
