import turicreate as gl
from pymongo import MongoClient

from ScienceDynamics.fetchers.authors_fetcher import AuthorsFetcher
from ScienceDynamics.paper import Paper

#
# def create_venues_sframe(v1, v2):
#     client = MongoClient('mongodb://%s:%s@127.0.0.1' % ('myAdmin', 'ty501u!%'))
#     a = AuthorsFetcher(client)
#     sf = gl.load_sframe('/data/sframes/papers_features_2015.sframe')
#     v1_sf = sf[sf["Journal ID mapped to venue name"] == v1]
#     v2_sf = sf[sf["Journal ID mapped to venue name"] == v2]
#     set_size = min(len(v1_sf), len(v2_sf))
#     sf = v1_sf[:set_size].append(v2_sf[:set_size])
#     l = []
#     for r in sf:
#         l.append(Paper(r, a).get_paper_features([v1, v2]))
#     sf = gl.load_sframe(l)
#     sf = sf.unpack("X1", column_name_prefix='')
#     sf = sf.fillna('Keywords', [])
#     for feature in ['last_author_number_of_papers', 'first_author_number_of_papers', 'author_max_number_of_papers']:
#         sf = sf.fillna(feature, 0)
#
#     stop_keywords = {'nature', 'physical sciences'}
#     sf['Keywords'] = sf['Keywords'].apply(lambda l: [i for i in l if i.lower() not in stop_keywords])
#
#     return sf


def evaluate_single_feature_contribution(sf):
    # venue_id = '003B355D' #08364228 - Nature 003B355D - Science 077EDC2F -PNAS 0C101982 - PLOSONE 0BB9EF81- Scientific Reports
    train, test = sf.random_split(0.8)
    d = {}
    l = ['Authors Number', 'Ref Count',
         'author_max_number_of_papers', 'first_author_academic_birthday', 'first_author_number_of_papers',
         'get_authors_avg_academic_birthday', 'get_authors_median_academic_birthday',
         'last_author_academic_birthday', 'last_author_number_of_papers',
         ]
    l += [c for c in sf.column_names() if 'in_venue' in c]
    for i in l:
        model = gl.classifier.create(train, target='Venue ID', features=[i])
        classification = model.classify(test)
        d[i] = gl.evaluation.precision(test['Venue ID'], classification['class'])

    for i in ['Keywords', 'Title Bag of Words']:
        model = gl.classifier.boosted_trees_classifier.create(train, target='Venue ID', max_iterations=1000,
                                                              features=[i])
        classification = model.classify(test)
        d[i] = gl.evaluation.precision(test['Venue ID'], classification['class'])
    return d


if __name__ == "__main__":
    v1 = '0C101982'
    v2 = '0BB9EF81'
    import itertools

    d = {}
    l = ['08364228', '003B355D', '077EDC2F', '0C101982', '0BB9EF81']
    for v1, v2 in itertools.combinations(l, 2):
        sf = create_venues_sframe(v1, v2)
        d[(v1, v2)] = evaluate_single_feature_contribution(sf)
