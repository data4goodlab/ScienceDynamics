import sys

from ScienceDynamics.config.configs import PAPER_REFERENCES_SFRAME, PAPER_REFERENCES_TXT, PAPER_REFERENCES_COUNT_SFRAME, \
    PAPERS_SFRAME, PAPERS_TXT, PAPER_URLS_SFRAME, PAPER_URLS_TXT, PAPER_KEYWORDS_SFRAME, PAPER_KEYWORDS_TXT, \
    PAPER_KEYWORDS_LIST_SFRAME, FIELDS_OF_STUDY_SFRAME, FIELDS_OF_STUDY_TXT, PAPER_AUTHOR_AFFILIATIONS_SFRAME, \
    PAPER_AUTHOR_AFFILIATIONS_TXT, PAPERS_ORDERED_AUTHORS_LIST_SFRAME, FIELDS_OF_STUDY_HIERARCHY_TXT, \
    FIELDS_OF_STUDY_HIERARCHY_SFRAME, TMP_DIR, AUTHORS_NAMES_TXT, AUTHOR_NAMES_SFRAME, PAPERS_FIELDS_OF_STUDY_SFRAME, \
    KEYWORDS_SFRAME, EXTENDED_PAPER_REFERENCES_SFRAME, PAPERS_CITATIONS_BYYEAR_SFRAME, EXTENDED_PAPERS_SFRAME, \
    FIELD_OF_STUDY_PAPERS_ID_SFRAME
from ScienceDynamics.config.log_config import logger
from ScienceDynamics.sframe_creators.fields_of_study_hieararchy_analyzer import FieldsHierarchyAnalyzer

import turicreate as tc
import turicreate.aggregate as agg
import os

sys.path.extend([".."])

"""
The code creates all the SFrame objects from the MAG KDD Cup 2016 Dataset
"""


def create_references_sframe():
    """Creating the references SFrame from txt files"""
    logger.info("Creating References SFrame")
    if os.path.isdir(PAPER_REFERENCES_SFRAME):
        return
    sf = tc.SFrame.read_csv(PAPER_REFERENCES_TXT, header=False, delimiter="\t")
    sf = sf.rename({"X1": "Paper ID", "X2": "PapOriginal venue nameer reference ID"})
    sf.save(PAPER_REFERENCES_SFRAME)


def create_references_count_sframe():
    """Creating SFrame with the number of references in each paper"""
    logger.info("Creating References Count SFrame")
    if os.path.isdir(PAPER_REFERENCES_COUNT_SFRAME):
        return
    r_sf = tc.load_sframe(PAPER_REFERENCES_SFRAME)
    sf = r_sf.groupby("Paper ID", {"Ref Number": agg.COUNT()})
    sf.save(PAPER_REFERENCES_COUNT_SFRAME)


def create_papers_sframe():
    """
    Create the Papers SFrame object from txt files which contains information on each paper
    """
    logger.info("Creating Papers SFrame")
    if os.path.isdir(PAPERS_SFRAME):
        return
    sf = tc.SFrame.read_csv(PAPERS_TXT, header=False, delimiter="\t")

    sf = sf.rename({"X1": "Paper ID", "X2": "Original paper title", "X3": "Normalized paper title",
                    "X4": "Paper publish year", "X5": "Paper publish date",
                    "X6": "Paper Document Object Identifier (DOI)",
                    "X7": "", "X8": "Normalized venue name", "X9": "Journal ID mapped to venue name",
                    "X10": "Conference ID mapped to venue name", "X11": "Paper rank"})
    sf["Paper publish year"] = sf["Paper publish year"].astype(int)
    sf.save(PAPERS_SFRAME)


def create_urls_sframe():
    """
    Creating URLs SFrame from txt files
    """
    logger.info("Creating urls SFrame")
    if os.path.isdir(PAPER_URLS_SFRAME):
        return
    sf = tc.SFrame.read_csv(PAPER_URLS_TXT, header=False, delimiter="\t")
    sf = sf.rename({"X1": "Paper ID", "X2": "Url"})
    g = sf.groupby("Paper ID", {"Urls": agg.CONCAT("Url")})
    g.save(PAPER_URLS_SFRAME)


def create_keywords_sframe():
    """
    Creating Keywords SFrame from txt files
    """
    logger.info("Creating Keywords SFrame")
    if os.path.isdir(PAPER_KEYWORDS_SFRAME):
        return
    sf = tc.SFrame.read_csv(PAPER_KEYWORDS_TXT, header=False, delimiter="\t")
    sf = sf.rename({"X1": "Paper ID", "X2": "Keyword name", "X3": "Field of study ID mapped to keyword"})
    sf.save(PAPER_KEYWORDS_SFRAME)


def create_paper_keywords_list_sframe():
    """
    Creating Paper Keywords List SFrame
    """
    logger.info("Creating Papers' Keywords List SFrame")
    if os.path.isdir(PAPER_KEYWORDS_LIST_SFRAME):
        return

    sf = tc.load_sframe(PAPER_KEYWORDS_SFRAME)
    g = sf.groupby("Paper ID", {"Keywords List": agg.CONCAT("Keyword name")})
    g.save(PAPER_KEYWORDS_LIST_SFRAME)


def create_fields_of_study_sframe():
    """
    Creating Field of study SFrame from txt files
    """
    logger.info("Creating Fields of Study SFrame")
    if os.path.isdir(FIELDS_OF_STUDY_SFRAME):
        return
    sf = tc.SFrame.read_csv(FIELDS_OF_STUDY_TXT, header=False, delimiter="\t")
    sf = sf.rename({"X1": "Field of study ID", "X2": "Field of study name"})
    sf.save(FIELDS_OF_STUDY_SFRAME)


def create_paper_author_affiliations_sframe():
    """
    Creating authors affilation SFrame from txt files
    :return:
    """
    logger.info("Creating Author Affilliations SFrame")
    if os.path.isdir(PAPER_AUTHOR_AFFILIATIONS_SFRAME):
        return
    sf = tc.SFrame.read_csv(PAPER_AUTHOR_AFFILIATIONS_TXT, header=False, delimiter="\t")
    sf = sf.rename({"X1": "Paper ID", "X2": "Author ID", "X3": "Affiliation ID", "X4": "Original affiliation name",
                    "X5": "Normalized affiliation name", "X6": "Author sequence number"})
    sf.save(PAPER_AUTHOR_AFFILIATIONS_SFRAME)


def create_papers_authors_lists_sframe():
    """
    Create SFrame in which each row contains paper id and a sorted list of the paper's authors
    """
    logger.info("Creating Authors Lists SFrame")
    if os.path.isdir(PAPERS_ORDERED_AUTHORS_LIST_SFRAME):
        return
    authors_sf = tc.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)
    authors_sf = authors_sf["Paper ID", "Author ID", "Author sequence number"]
    authors_sf['Author_Seq'] = authors_sf.apply(lambda r: [r["Author ID"], r["Author sequence number"]])
    g = authors_sf.groupby("Paper ID", {"Authors List": agg.CONCAT('Author_Seq')})
    g['Authors List Sorted'] = g["Authors List"].apply(lambda l: sorted(l, key=lambda i: i[1]))
    g['Authors List Sorted'] = g['Authors List Sorted'].apply(lambda l: [i[0] for i in l])
    g = g.remove_column("Authors List")
    g = g["Paper ID", 'Authors List Sorted']
    g['Authors Number'] = g['Authors List Sorted'].apply(lambda l: len(l))
    g.save(PAPERS_ORDERED_AUTHORS_LIST_SFRAME)


def create_field_of_study_hierarchy_sframe():
    """
    Creates field of study hierarchy sframe from txt files
    """
    logger.info("Creating Field of Study Hierarchy SFrame")
    if os.path.isdir(FIELDS_OF_STUDY_HIERARCHY_SFRAME):
        return
    h_sf = tc.SFrame.read_csv(FIELDS_OF_STUDY_HIERARCHY_TXT, header=False, delimiter="\t")
    h_sf = h_sf.rename({"X1": "Child field of study ID", "X2": "Child field of study level",
                        "X3": "Parent field of study ID", "X4": "Parent field of study level",
                        "X5": "Confidence"})
    h_sf.save(FIELDS_OF_STUDY_HIERARCHY_SFRAME)


def _get_tmp_papers_sframe_path(min_ref_num, start_year, end_year):
    """
    Get Papers SFrame path according to years and references number filters
    :param min_ref_num: paper's minimal references number
    :param start_year: start year
    :param end_year: end year
    :return: a path to the Papers SFrame which contains papers with the above filter
    :rtype: str
    """
    return f"{TMP_DIR}/papers_sframe_minref_{min_ref_num}_{start_year}_{end_year}"


def get_papers_sframe(min_ref_num=None, start_year=None, end_year=None):
    """
    Return SFrame with Papers data accoring to the input filter variables
    :param min_ref_num:  paper's minimal references number
    :param start_year: start year (only include paper that were published after start year)
    :param end_year: end year (only include paper that were published before end year)
    :return: SFrame with paper data
    :rtype: tc.SFrame
    :note: after the SFrame is created it is saved to the TMP_DIR to future use
    """
    sf = tc.load_sframe(PAPER_REFERENCES_SFRAME)
    tmp_papers_sf_path = _get_tmp_papers_sframe_path(min_ref_num, start_year, end_year)
    if os.path.isdir(tmp_papers_sf_path):
        return tc.load_sframe(tmp_papers_sf_path)

    if min_ref_num is not None:
        logger.info(f"Getting papers ids with at least refrences {min_ref_num}")
        sf = sf.groupby('Paper ID', {'Ref Count': agg.COUNT()})  # There are 30058322 in the list
        sf = sf[sf['Ref Count'] >= min_ref_num]  # left with 22,083,058
        sf.__materialize__()
    p_sf = tc.load_sframe(PAPERS_SFRAME)
    sf = p_sf.join(sf)
    if start_year is not None:
        logger.info("Getting papers with from %s " % start_year)
        sf = sf[sf['Paper publish year'] >= start_year]
    if end_year is not None:
        logger.info("Getting papers with util %s " % end_year)
        sf = sf[sf['Paper publish year'] <= end_year]
    sf.__materialize__()

    if not os.path.isdir(tmp_papers_sf_path):
        sf.save(tmp_papers_sf_path)

    return sf


def create_authors_names_sframe():
    """
    Creates authors names SFrames from txt files
    """
    logger.info("Creating Authors Names SFrame")
    if os.path.isdir(AUTHORS_NAMES_TXT):
        return
    a_sf = tc.SFrame.read_csv(AUTHORS_NAMES_TXT, header=False, delimiter="\t")
    a_sf = a_sf.rename({'X1': 'Author ID', 'X2': 'Author name'})
    a_sf['First name'] = a_sf['Author name'].apply(lambda s: s.split()[0])
    a_sf['Last name'] = a_sf['Author name'].apply(lambda s: s.split()[-1])
    a_sf.save(AUTHOR_NAMES_SFRAME)


def create_papers_fields_of_study(flevels=(0, 1, 2, 3)):
    """
    Create SFrame with each paper fields of study by hierarchical levels
    :param flevels: list of levels, for each level add the papers fields of study in this level
    """
    logger.info("Creating Papers Fields of Study SFrame")
    if os.path.isdir(PAPERS_FIELDS_OF_STUDY_SFRAME):
        return
    k_sf = tc.load_sframe(KEYWORDS_SFRAME)
    g = k_sf.groupby('Paper ID', {'Field of study list': agg.CONCAT("Field of study ID mapped to keyword")})
    fh = FieldsHierarchyAnalyzer()

    # add fileds of study names from ID
    names = []
    for l in g['Field of study list']:
        names.append([fh.get_field_name(i) for i in l])
    g['Field of study list names'] = names

    for flevel in flevels:
        logger.info("Adding papers fields of study level %s" % flevel)
        parent_list = []
        for paper_field_of_study_list in g['Field of study list']:
            parent_list.append(
                list(set.union(*[fh.get_parents_field_of_study(field, flevel) for field in paper_field_of_study_list])))
        g['Fields of study parent list (L%s)' % flevel] = parent_list

        names = []
        for paper_field_of_study_parents_list in g['Fields of study parent list (L%s)' % flevel]:
            names.append([fh.get_field_name(field_of_study) for field_of_study in paper_field_of_study_parents_list])
        g['Fields of study parent list names (L%s)' % flevel] = names
    g.save(PAPERS_FIELDS_OF_STUDY_SFRAME)


def create_extended_references_sframe():
    """
    Create SFrame with references data with additional column that state if the reference is self-citation
    """
    logger.info("Creating Extended References  SFrame")
    if os.path.isdir(EXTENDED_PAPER_REFERENCES_SFRAME):
        return
    ref_sf = tc.load_sframe(PAPER_REFERENCES_SFRAME)
    p_sf = tc.load_sframe(PAPERS_ORDERED_AUTHORS_LIST_SFRAME)
    ref_sf = ref_sf.join(p_sf, on='Paper ID', how="left")
    ref_sf = ref_sf.join(p_sf, on={'Paper reference ID': 'Paper ID'}, how="left")
    ref_sf = ref_sf.fillna('Authors List Sorted.1', [])
    ref_sf = ref_sf.fillna('Authors List Sorted', [])
    ref_sf.__materialize__()
    ref_sf['self citation'] = ref_sf.apply(
        lambda r: len(set(r['Authors List Sorted.1']) & set(r['Authors List Sorted'])))
    ref_sf.__materialize__()
    ref_sf = ref_sf.remove_columns(['Authors List Sorted.1', 'Authors List Sorted'])

    ref_sf.save(EXTENDED_PAPER_REFERENCES_SFRAME)


def _get_total_citation_by_year(l, max_year=2015):
    """
    Calculate the total citation by year
    :param l:  list of (year, citation) tuple
    :param max_year: the maximal year
    :return: dict with the totatl number of citation in each year
    """
    min_year = int(min([y for y, v in l]))
    total_citations_dict = {}
    for i in range(min_year, int(max_year + 1)):
        total_citations_dict[str(i)] = sum([v for y, v in l if y <= i])
    return total_citations_dict


def _papers_citations_number_by_year_sframe(without_self_citation=True):
    """
    Get papers total number of citation in each year
    :param without_self_citation: if True calculate only non-self citations, other calculate with self-citations
    :return: SFrame with a column that contains citations_dict by year
    """
    logger.info("Creating Paper Citations by Year (without_self_citation=%s)" % without_self_citation)
    ref_sf = tc.load_sframe(EXTENDED_PAPER_REFERENCES_SFRAME)
    if without_self_citation:
        ref_sf = ref_sf[ref_sf['self citation'] == 0]

    sf = tc.load_sframe(PAPERS_SFRAME)["Paper ID", "Paper publish year"]
    sf = ref_sf.join(sf, on="Paper ID")
    g = sf.groupby(["Paper reference ID", "Paper publish year"], {"Citation Number": agg.COUNT()})
    g = g.rename({"Paper publish year": "Year", "Paper reference ID": "Paper ID"})
    g['Citation by Year'] = g.apply(lambda r: (r["Year"], r["Citation Number"]))
    h = g.groupby('Paper ID', {'Citation by Years': tc.aggregate.CONCAT('Citation by Year')})
    if without_self_citation:
        h['Total Citations by Year without Self Citations'] = h['Citation by Years'].apply(
            lambda l: _get_total_citation_by_year(l))
    else:
        h['Total Citations by Year'] = h['Citation by Years'].apply(lambda l: _get_total_citation_by_year(l))
    h = h.remove_column("Citation by Years")
    return h


def create_papers_citation_number_by_year_sframe():
    """
    Create SFrame with each paper's citation numbers by year dict (one dict with self-citations and the other without)
    """
    if os.path.isdir(PAPERS_CITATIONS_BYYEAR_SFRAME):
        return
    r_sf = _papers_citations_number_by_year_sframe(False)
    r_sf2 = _papers_citations_number_by_year_sframe(True)
    sf = r_sf.join(r_sf2, on="Paper ID")
    sf.save(PAPERS_CITATIONS_BYYEAR_SFRAME)


def create_extended_papers_sframe():
    """
    Created extended papers SFrame which contains various papers features, such as paper citation numbers, authors list, urls,.. etc
    :return:
    """
    logger.info("Creating Extended Papers SFrame")
    if os.path.isdir(EXTENDED_PAPERS_SFRAME):
        return
    sf = tc.load_sframe(PAPERS_SFRAME)

    sframes_list = [PAPER_REFERENCES_COUNT_SFRAME, PAPERS_CITATIONS_BYYEAR_SFRAME, PAPERS_ORDERED_AUTHORS_LIST_SFRAME,
                    PAPER_KEYWORDS_LIST_SFRAME, PAPERS_FIELDS_OF_STUDY_SFRAME, PAPER_URLS_SFRAME]

    for s in sframes_list:
        t = tc.load_sframe(s)
        sf = sf.join(t, how="left", on="Paper ID")
        sf.save(EXTENDED_PAPERS_SFRAME)
    sf = sf.fillna("Ref Number", 0)
    sf.save(EXTENDED_PAPERS_SFRAME)


def _create_field_of_study_paper_ids_sframe(level):
    """
    Create SFrame in which each row contains a field of study and it's matching list of paper ids
    :param level: field of study level
    :return: SFrame with the fields of stuyd in the input level papers ids
    :rtype: tc.SFrame
    """
    logger.info("Creating fields os study paper ids SFrame level - %s " % level)

    col = 'Fields of study parent list (L%s)' % level
    sf = tc.load_sframe(EXTENDED_PAPERS_SFRAME)
    new_col_name = "Field ID"
    sf = sf.stack(col, new_column_name=new_col_name)
    sf = sf[sf[col] != None]
    g = sf.groupby(new_col_name, {'Paper IDs': agg.CONCAT("Paper ID")})
    f_sf = tc.load_sframe(FIELDS_OF_STUDY_SFRAME)
    g = g.join(f_sf, on={new_col_name: "Field of study ID"})
    g['Number of Paper'] = g['Paper IDs'].apply(lambda l: len(l))
    g['Level'] = level
    g = g.rename({new_col_name: "Field of study ID"})
    return g


def create_fields_of_study_papers_ids_sframes(levels=(1, 2, 3)):
    """
    Creates SFrames with each Fields of study paper ids
    :param levels: list of fields of study level

    """
    if os.path.isdir(FIELD_OF_STUDY_PAPERS_ID_SFRAME):
        return

    sf = tc.SFrame()
    for level in levels:
        sf = sf.append(_create_field_of_study_paper_ids_sframe(level))
    sf.save(FIELD_OF_STUDY_PAPERS_ID_SFRAME)
    return sf


def create_all_sframes():
    """
    Creates all SFrame from txt files
    """
    create_papers_sframe()

    create_references_sframe()
    create_references_count_sframe()

    create_paper_author_affiliations_sframe()
    create_papers_authors_lists_sframe()

    create_keywords_sframe()
    create_paper_keywords_list_sframe()
    create_field_of_study_hierarchy_sframe()
    create_fields_of_study_sframe()
    create_papers_fields_of_study()

    create_references_sframe()
    create_extended_references_sframe()

    create_extended_papers_sframe()
    create_fields_of_study_papers_ids_sframes()
