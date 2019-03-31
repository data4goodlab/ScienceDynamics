import turicreate as gl
import turicreate.aggregate as agg
import numpy as np
import json

from ScienceDynamics.configs import VenueType
from ScienceDynamics.papers_collection_analyer import PapersCollection
from ScienceDynamics.venue import Venue


def create_papers_per_year_figure_data():
    sf = gl.load_sframe('papers_sframe_minref_5.sframe')
    g = sf.groupby('Paper publish year', {'Papers Number with at least 5 Refs': agg.COUNT()})
    sf = gl.load_sframe('papers_per_year_count.sframe')
    sf = sf.join(g, how="left", on="Paper publish year")
    sf.rename({'Paper publish year': 'Year', 'Count': 'Published Papers'})
    sf = sf.sort('Year')
    sf.save('/Users/michael/Dropbox/academia_eco_system_anlayzer/code/article/data/papers_per_year.csv', format='csv')


def create_authors_per_year_figure_data():
    sf = gl.load_sframe('authors_features.sframe/')
    g = sf.groupby('start_year', {'New Authors': agg.COUNT()})
    g = g.sort('start_year')
    g.save('new_authors_per_year.csv', format="csv")


def create_refrences_figure_data():
    sf = gl.load_sframe('/mnt/data/PaperReferences.sframe/')
    g = sf.groupby('Paper ID', {'Ref Num': agg.COUNT_DISTINCT('Paper reference ID')})
    sf = gl.load_sframe('/mnt/data/Papers.sframe/')[["Paper ID", 'Paper publish year']]
    x = sf.join(g, how="left")
    x = x.fillna('Ref Num', 0)
    y = x.groupby('Paper publish year', agg.CONCAT('Ref Num'))
    y['Median Ref Num'] = y['List of Ref Num'].apply(lambda l: np.median(l))  # the media is zero
    z = x[x['Ref Num'] >= 5].groupby('Paper publish year', agg.CONCAT('Ref Num'))
    z['Median Ref Num'] = z['List of Ref Num'].apply(lambda l: np.median(l))
    z['Avg Ref Num'] = z['List of Ref Num'].apply(lambda l: np.average(l))


def self_citations_figure_data():
    psf = gl.load_sframe('papers_features.sframe/')
    psf = psf['Paper ID', 'Authors List Sorted']
    rsf = gl.load_sframe('PaperReferences.sframe/')
    rsf = rsf.join(psf, on="Paper ID")
    rsf = rsf.join(psf, on={"Paper reference ID": "Paper ID"})
    rsf = rsf.fillna('Authors List Sorted', [])
    rsf = rsf.fillna('Authors List Sorted.1', [])
    rsf.__materialize__()
    rsf['is_self_citations'] = rsf.apply(
        lambda l: len(set(l['Authors List Sorted']) & set(l['Authors List Sorted.1'])) > 0)
    g = rsf.groupby("Paper ID", {'total_self_citations': agg.SUM('is_self_citations')})
    psf = gl.load_sframe('papers_sframe_minref_5.sframe')['Paper ID', 'Paper publish year']
    x = psf.join(g, how="left")
    y = x.groupby("Paper publish year", {"self_citations_list": agg.CONCAT("total_self_citations")})
    y['papers_with_self_citation_num'] = y['self_citations_list'].apply(lambda l: sum([1 for i in l if i > 0]))
    y['papers_num'] = y['self_citations_list'].apply(lambda l: len(l))
    y['papers_with_self_citations_percentage'] = y.apply(
        lambda r: r['papers_with_self_citation_num'] / float(r['papers_num']) if r['papers_num'] > 0 else 0)
    y['papers_num', "Paper publish year", "papers_with_self_citations_percentage"].save('self_citation_percentage.csv',
                                                                                        format="csv")


def keywords_figures_data():
    sf = gl.load_sframe('papers_features.sframe/')
    sf = sf.fillna('Keywords List', [])
    sf['Keywords Number'] = sf['Keywords List'].apply(lambda l: len(l))
    sf = sf["Paper ID", 'Paper publish year', 'Keywords Number']
    g = sf.groupby('Paper publish year', {"Total Number of Papers": agg.COUNT(),
                                          "Papers Keywords Number List": agg.CONCAT('Keywords Number')})
    g['Number of Papers with Keywords'] = g["Papers Keywords Number List"].apply(lambda l: sum([1 for i in l if i > 0]))
    g['Average Number of Keywords'] = g["Papers Keywords Number List"].apply(lambda l: np.average(l))
    g['Median Number of Keywords'] = g["Papers Keywords Number List"].apply(lambda l: np.median(l))
    g['Percent of Papers with Keywords'] = g.apply(
        lambda r: r['Number of Papers with Keywords'] / float(r["Total Number of Papers"]))

    x = g[
        'Paper publish year', 'Percent of Papers with Keywords', 'Average Number of Keywords', 'Number of Papers with Keywords', 'Median Number of Keywords']
    y = x.sort('Paper publish year', ascending=False)


def cross_domain_figure_data():
    l = []
    for i in [0, 1]:
        sf = gl.load_sframe('papers_features.sframe')
        sf = sf.fillna('Fields of study parent list (L%s)' % i, [])
        sf = sf[sf['Fields of study parent list (L%s)' % i] != []]
        sf.__materialize__()
        sf['L%s Fields Number' % i] = sf['Fields of study parent list (L%s)' % i].apply(lambda l: len(l))
        g = sf.groupby('Paper publish year',
                       {"Total Number of Papers": agg.COUNT(),
                        "L%s Fields Number List" % i: agg.CONCAT('L%s Fields Number' % i)})
        g['Average Number of L%s' % i] = g["L%s Fields Number List" % i].apply(lambda l: np.average(l))
        g['Median Number of L%s' % i] = g["L%s Fields Number List" % i].apply(lambda l: np.median(l))

        l.append(g['Paper publish year', 'Average Number of L%s' % i, 'Median Number of L%s' % i])

    y = l[0].join(l[1])
    y = y.sort('Paper publish year', ascending=False)
    y.save('/home/michael/article_results/papers_cross_domains.csv', format="csv")


def get_citation_after_years(r, years, include_self_citations):
    pyear = r['Paper publish year']
    if pyear + years > 2014:
        return None
    yrs = str(pyear + years)
    if include_self_citations:
        if r['Total Citations by Year'] is None:
            return 0
        if yrs in r['Total Citations by Year']:
            return r['Total Citations by Year'][yrs]
    else:
        if r['Total Citations by Year without Self Citations'] is None:
            return 0
        if yrs in r['Total Citations by Year without Self Citations']:
            return r['Total Citations by Year without Self Citations'][yrs]
    return 0


def total_citation_after_years_years(y=3):
    sf = gl.load_sframe('papers_features.sframe')
    sf['after_%s' % y] = sf.apply(lambda r: get_citation_after_years(r, y, True))
    sf['after_%s_no_self_citations' % y] = sf.apply(lambda r: get_citation_after_years(r, y, False))

    x = sf["Paper ID", "after_%s" % y, 'after_%s_no_self_citations' % y, 'Paper publish year']
    z = x[x['Paper publish year'] <= 2014 - y]
    g = z.groupby('Paper publish year', {'total_citations_list': agg.CONCAT('after_%s' % y),
                                         'total_citations_list_no_self_citations': agg.CONCAT(
                                             'after_%s_no_self_citations' % y)})
    g['total_papers'] = g['total_citations_list'].apply(lambda l: len(l))
    g['papers_with_zero_after_%s' % y] = g['total_citations_list'].apply(lambda l: len([i for i in l if i == 0]))
    g['papers_with_zero_after_%s_no_self_citations' % y] = g['total_citations_list_no_self_citations'].apply(
        lambda l: len([i for i in l if i == 0]))
    g['zero_citation_percentage_%s' % y] = g.apply(
        lambda r: r['papers_with_zero_after_%s' % y] / float(r['total_papers']))
    g['zero_citation_percentage_no_self_%s' % y] = g.apply(
        lambda r: r['papers_with_zero_after_%s_no_self_citations' % y] / float(r['total_papers']))
    x = g.sort('Paper publish year', ascending=False)
    x['Paper publish year', 'zero_citation_percentage_%s' % y, 'zero_citation_percentage_no_self_%s' % y].save(
        '/home/michael/article_results/papers_no_citations_after%s.csv' % y, format="csv")


def citations_figure_data(after_years=(1, 3, 5, 10)):
    sf_list = [gl.SFrame.read_csv('/home/michael/article_results/papers_no_citations_after%s.csv' % y) for y in
               after_years]
    sf = sf_list[0]
    for i in range(1, len(sf_list)):
        sf = sf.join(sf_list[i], how="left")
    sf.save("/home/michael/article_results/papers_no_citations_all.csv")


def get_authors_per_paper_number_figure_data():
    sf = gl.load_sframe('PaperAuthorAffiliations.sframe/')
    g = sf.groupby("Paper ID", agg.CONCAT("Author ID"))
    g['List of Author ID'] = g['List of Author ID'].apply(
        lambda l: list(set(l)))  # double checking no authors count twice
    g['Authors Number'] = g['List of Author ID'].apply(lambda l: len(l))
    g.__materialize__()
    psf = gl.load_sframe('Papers.sframe')['Paper ID', 'Paper publish year']
    psf = psf.join(g, how="left")
    g2 = psf.groupby('Paper publish year', {'Authors Number List': agg.CONCAT('Authors Number')})
    g2['Average Authors Number'] = g2['Authors Number List'].apply(lambda l: np.average(l))
    g2['Median Authors Number'] = g2['Authors Number List'].apply(lambda l: np.median(l))
    psf2 = gl.load_sframe('papers_sframe_minref_5.sframe')
    psf2 = psf2[['Paper ID']].join(psf, how="left")
    g3 = psf2.groupby('Paper publish year', {'Authors Number List': agg.CONCAT('Authors Number')})
    g3['Average Authors Number with At least 5 Ref'] = g3['Authors Number List'].apply(lambda l: np.average(l))
    g3['Median Authors Number with At least 5 Ref'] = g3['Authors Number List'].apply(lambda l: np.median(l))

    y = g2['Paper publish year', 'Average Authors Number', 'Median Authors Number']
    z = g3[
        'Paper publish year', 'Average Authors Number with At least 5 Ref', 'Median Authors Number with At least 5 Ref']
    y = y.join(z)
    y = y.sort('Paper publish year', ascending=False)

    y.save('/home/michael/arfticle_results/avg_med_new_authors.csv', format="csv")


def get_number_of_publications_list_after_years(y, l):
    total_publication_list = []
    for d in l:
        for k, v in d.iteritems():
            if k <= y:
                total_publication_list.append(v)
    return total_publication_list


def get_average_number_of_publication_a_year(start_year, end_year, total_publications):
    return total_publications / float(end_year - start_year + 1)


def get_authors_publications_by_year_data():
    asf = gl.load_sframe('PaperAuthorAffiliations.sframe/')['Paper ID', 'Author ID']
    psf = gl.load_sframe('Papers.sframe')['Paper ID', 'Paper publish year']
    a_sf = asf.join(psf)
    g = a_sf.groupby(['Author ID', 'Paper publish year'], {'paper_ids': agg.CONCAT('Paper ID')})
    g['publication_by_year'] = g.apply(lambda r: (r['Paper publish year'], r['paper_ids']))
    g2 = g.groupby('Author ID', {"all_publications_by_year": agg.CONCAT('publication_by_year')})
    g2['all_publications_dict'] = g2['all_publications_by_year'].apply(lambda l: dict(l))
    g2['total_publications'] = g2['all_publications_dict'].apply(lambda d: sum([len(v) for v in d.values()]))
    g3 = g2[g2['total_publications'] >= 3]['Author ID', 'all_publications_dict']
    # for 5 years 10143245 authors
    g3['start_year'] = g3['all_publications_dict'].apply(lambda d: min(d.keys()))
    g3['end_year'] = g3['all_publications_dict'].apply(lambda d: max(d.keys()))
    g3['normalized_publications_dict'] = g3.apply(
        lambda r: {(k - r['start_year']): len(v) for k, v in r['all_publications_dict'].iteritems()})

    g4 = g3.groupby('start_year', {'publications_dicts_list': agg.CONCAT('normalized_publications_dict')})
    selected_years = range(1950, 2015, 5)
    g4 = g4[g4['start_year'].apply(lambda y: y in selected_years)]
    for i in range(0, 51, 1):
        print(i)
        g4['%s' % i] = g4.apply(
            lambda r: np.average(get_number_of_publications_list_after_years(i, r['publications_dicts_list'])) if (r[
                                                                                                                       'start_year'] + i) <= 2014 else None)
        g4.__materialize__()

    g4.remove_column('publications_dicts_list')
    g4.save('/home/michael/article_results/authors_average_total_publications_by_start_year.csv', format="csv")

    g3['Publications Yearly Rate'] = g3.apply(
        lambda r: get_average_number_of_publication_a_year(r['start_year'], r['end_year'],
                                                           sum(r['normalized_publications_dict'].values())))
    g5 = g3.groupby('start_year', {'Authors Yearly Publications Rate List': agg.CONCAT('Publications Yearly Rate')})
    g5['Average Authors Yearly Publication Rate'] = g5['Authors Yearly Publications Rate List'].apply(
        lambda l: np.average(l))
    g5['Median Authors Yearly Publication Rate'] = g5['Authors Yearly Publications Rate List'].apply(
        lambda l: np.median(l))
    g5.remove_column('Authors Yearly Publications Rate')
    g5 = g5.sort('start_year', ascending=False)
    g5.save('/home/michael/article_results/authors_average_median_yearly_publication_rate.csv', format="csv")


def get_gender_percentage(d):
    if 'Female' not in d:
        d['Female'] = 0
    if 'Male' not in d:
        d['Male'] = 0
    if d['Male'] + d['Female'] == 0:
        return None
    return d['Female'] / float(d['Male'] + d['Female'])


def get_gender_top_papers_rank_over_time():
    psf = gl.load_sframe('papers_sframe_minref_5.sframe/')['Paper publish year', 'Paper ID', 'Paper rank']
    psf = psf.sort(['Paper publish year', 'Paper rank'])
    psf['Paper ID and Rank'] = psf.apply(lambda r: (r['Paper ID'], r['Paper rank']))
    g = psf.groupby('Paper publish year', {'Paper ID and Rank List': agg.CONCAT('Paper ID and Rank')})
    f = lambda l: sorted(l, key=lambda k: k[1])
    g['Paper ID and Rank List 100'] = g['Paper ID and Rank List'].apply(lambda l: f(l)[:100])
    g.__materialize__()
    g = g.sort('Paper publish year')
    g['Papers Ids'] = g['Paper ID and Rank List 100'].apply(lambda l: [i[0] for i in l])
    g['All Authors Gender Stats'] = g['Paper publish year', 'Papers Ids'].apply(
        lambda r: dict(PapersCollection(papers_ids=r['Papers Ids']).authors_gender_stats(r['Paper publish year'])))
    g['First Authors Gender Stats'] = g['Paper publish year', 'Papers Ids'].apply(lambda r: dict(
        PapersCollection(papers_ids=r['Papers Ids']).first_authors_gender_stats(r['Paper publish year'])))
    g['Last Authors Gender Stats'] = g['Paper publish year', 'Papers Ids'].apply(
        lambda r: dict(PapersCollection(papers_ids=r['Papers Ids']).last_authors_gender_stats(r['Paper publish year'])))
    g2 = g['Paper publish year', 'All Authors Gender Stats', 'First Authors Gender Stats', 'Last Authors Gender Stats']
    g2['All Authors Female Percentage'] = g2['All Authors Gender Stats'].apply(lambda d: get_gender_percentage(d))
    g2['First Authors Female Percentage'] = g2['First Authors Gender Stats'].apply(lambda d: get_gender_percentage(d))
    g2['Last Authors Female Percentage'] = g2['Last Authors Gender Stats'].apply(lambda d: get_gender_percentage(d))
    g2[
        'Paper publish year', 'All Authors Female Percentage', 'First Authors Female Percentage', 'Last Authors Female Percentage'].save(
        '/home/michael/article_results/gender_stat.csv')


# Need to work on this
def get_gender_top_papers_rank_over_time_female_author_probability():
    psf = gl.load_sframe('papers_sframe_minref_5.sframe/')['Paper publish year', 'Paper ID', 'Paper rank']
    psf = psf.sort(['Paper publish year', 'Paper rank'])
    psf['Paper ID and Rank'] = psf.apply(lambda r: (r['Paper ID'], r['Paper rank']))
    g = psf.groupby('Paper publish year', {'Paper ID and Rank List': agg.CONCAT('Paper ID and Rank')})
    f = lambda l: sorted(l, key=lambda k: k[1])
    g['Paper ID and Rank List 100'] = g['Paper ID and Rank List'].apply(lambda l: f(l)[:100])
    g.__materialize__()
    g = g.sort('Paper publish year')
    g['Papers Ids'] = g['Paper ID and Rank List 100'].apply(lambda l: [i[0] for i in l])

    names_sf = gl.load_sframe("/mnt/data/first_name_gender.sframe")
    female_name_prob_dict = {r["First Name"]: 1 - r["Percentage Males"] for r in names_sf}

    g['All Authors Gender Stats'] = g['Paper publish year', 'Papers Ids'].apply(
        lambda r: dict(PapersCollection(papers_ids=r['Papers Ids']).authors_gender_stats(r['Paper publish year'])))
    g['First Authors Gender Stats'] = g['Paper publish year', 'Papers Ids'].apply(lambda r: dict(
        PapersCollection(papers_ids=r['Papers Ids']).first_authors_gender_stats(r['Paper publish year'])))
    g['Last Authors Gender Stats'] = g['Paper publish year', 'Papers Ids'].apply(
        lambda r: dict(PapersCollection(papers_ids=r['Papers Ids']).last_authors_gender_stats(r['Paper publish year'])))
    g2 = g['Paper publish year', 'All Authors Gender Stats', 'First Authors Gender Stats', 'Last Authors Gender Stats']
    g2['All Authors Female Percentage'] = g2['All Authors Gender Stats'].apply(lambda d: get_gender_percentage(d))
    g2['First Authors Female Percentage'] = g2['First Authors Gender Stats'].apply(lambda d: get_gender_percentage(d))
    g2['Last Authors Female Percentage'] = g2['Last Authors Gender Stats'].apply(lambda d: get_gender_percentage(d))
    g2[
        'Paper publish year', 'All Authors Female Percentage', 'First Authors Female Percentage', 'Last Authors Female Percentage'].save(
        '/home/michael/article_results/gender_stat.csv')


def get_journals_stat():
    sf = gl.load_sframe("../../data/sjr.sframe")
    g = sf.groupby('Year', agg.COUNT())
    g = g.sort('Year')
    g.save('data/journal_numbers.csv', format="csv")
    g2 = sf.groupby(['Year', 'SJR Best Quartile'], {"Total Papers": agg.SUM('Total Docs.')})
    g2.save('data/journal_quartiles.csv', format="csv")
    g1['Quartile Papers Number'] = g2.apply(lambda r: (r["SJR Best Quartile"], r["Total Papers"]))
    g3 = g2.groupby('Year', {'Quartiles': agg.CONCAT('Quartile Papers Number')})
    g3.save('data/journal_quartiles.sframe')


def journal_returning_authors_get_data(outdir="/home/michael/article_results/selected_journals_features"):
    d = Venue.get_journals_dict()
    journals_list = ["Nature", "Science", "The New England Journal of Medicine", "The Lancet",
                     "Chemical Society Reviews", "Journal of the American Chemical Society",
                     "Cell", "Advanced Materials",
                     "Proceedings of the National Academy of Sciences of the United States of America",
                     "Chemical Reviews", "Scientific Reports", "PLOS ONE"]

    for j in journals_list:
        v = Venue(d[j], j, VenueType.journal)
        features_dict = {str(k): v for k, v in v.features_dict.iteritems()}
        features_dict["type"] = "journal"
        json.dump(features_dict, open(f"{outdir}/{j}.json", "w"))
