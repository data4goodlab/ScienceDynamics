from code.consts import *
from code.paper import Paper


def papers_no_citations_stats(include_self_citation):
    l = gl.load_sframe('/mnt/data/papers_sframe_minref_5.sframe')['Paper ID']
    d = {}
    count = 0
    for i in l:
        count += 1
        if count % 100000 == 0:
            print count
        p = Paper(i)
        if p.publish_year > 2010:
            continue
        if p.publish_year not in d:
            d[p.publish_year] = {}
        d[p.publish_year][i] = {}
        d[p.publish_year][i]['after_5'] = p.total_citation_number_years_after_publication(5, include_self_citation)
        if p.publish_year > 2005:
            continue

        d[p.publish_year][i]['after_10'] = p.total_citation_number_years_after_publication(10, include_self_citation)

def perecentage_of_no_cited_papers_by_year(papers_citation_by_years_stats_dict):
    h = {}
    for y in papers_citation_by_years_stats_dict.keys():
        h[y] =  {'no_citations_5': 0, 'with_citations_5':0}
        for d in papers_citation_by_years_stats_dict[y].values():
            if d['after_5'] > 5:
                h[y]['with_citations_5'] += 1
            else:
                h[y]['no_citations_5'] += 1
