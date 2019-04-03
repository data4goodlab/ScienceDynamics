import pathlib
from turicreate import SFrame, load_sframe
from ScienceDynamics.datasets.configs import MAG_URL
from ScienceDynamics.datasets.utils import download_file, save_sframe
import turicreate.aggregate as agg

from ScienceDynamics.sframe_creators.fields_of_study_hieararchy_analyzer import FieldsHierarchyAnalyzer

import zipfile


class MicrosoftAcademicGraph(object):
    def __init__(self, dataset_zip=None):
        self._dataset_dir = pathlib.Path(dataset_zip).parent
        self._dataset_dir.mkdir(exist_ok=True)
        self._sframe_dir = self._dataset_dir / "sframes"
        self._sframe_dir.mkdir(exist_ok=True)
        if not pathlib.Path(dataset_zip).exists():
            download_file(MAG_URL, pathlib.Path(dataset_zip))
            with zipfile.ZipFile(pathlib.Path(dataset_zip), 'r') as f:
                f.extractall(self._dataset_dir)

    @property
    @save_sframe(sframe="Papers.sframe")
    def papers(self):
        """
        Create the Papers SFrame object from txt files which contains information on each paper
        """
        papers = SFrame.read_csv(str(self._dataset_dir / "Papers.txt"), header=False, delimiter="\t")

        papers = papers.rename({"X1": "Paper ID", "X2": "Original paper title", "X3": "Normalized paper title",
                                "X4": "Paper publish year", "X5": "Paper publish date",
                                "X6": "Paper Document Object Identifier (DOI)",
                                "X7": "", "X8": "Normalized venue name", "X9": "Journal ID mapped to venue name",
                                "X10": "Conference ID mapped to venue name", "X11": "Paper rank"})
        papers["Paper publish year"] = papers["Paper publish year"].astype(int)
        return papers

    @property
    @save_sframe(sframe="PaperReferences.sframe")
    def references(self):
        """Creating the references SFrame from txt files"""
        references = SFrame.read_csv(str(self._dataset_dir / "PaperReferences.txt"), header=False, delimiter="\t")
        references = references.rename({"X1": "Paper ID", "X2": "PapOriginal venue name reference ID"})
        return references

    @property
    @save_sframe(sframe="PaperReferencesCount.sframe")
    def reference_count(self):
        return self.references.groupby("Paper ID", {"Ref Number": agg.COUNT()})

    @property
    @save_sframe(sframe="PaperReferencesCount.sframe")
    def keywords(self):
        """
        Creating Keywords SFrame from txt files
        """
        keywords = SFrame.read_csv(str(self._dataset_dir / "PaperKeywords.txt"), header=False, delimiter="\t")
        return keywords.rename({"X1": "Paper ID", "X2": "Keyword name", "X3": "Field of study ID mapped to keyword"})

    @property
    @save_sframe(sframe="PaperKeywordsList.sframe")
    def paper_keywords_list(self):
        """
        Creating Paper Keywords List SFrame
        """
        return self.keywords.groupby("Paper ID", {"Keywords List": agg.CONCAT("Keyword name")})

    @property
    @save_sframe(sframe="FieldsOfStudy.sframe")
    def fields_of_study(self):
        """
        Creating Field of study SFrame from txt files
        """
        fields_of_study = SFrame.read_csv(str(self._dataset_dir / "FieldsOfStudy.txt"), header=False, delimiter="\t")
        return fields_of_study.rename({"X1": "Field of study ID", "X2": "Field of study name"})

    @property
    @save_sframe(sframe="PaperAuthorAffiliations.sframe")
    def paper_author_affiliations(self):
        """
        Creating authors affiliation SFrame from txt files
        :return:
        """
        paper_author_affiliations = SFrame.read_csv(str(self._dataset_dir / "PaperAuthorAffiliations.txt"),
                                                    header=False, delimiter="\t")
        return paper_author_affiliations.rename(
            {"X1": "Paper ID", "X2": "Author ID", "X3": "Affiliation ID", "X4": "Original affiliation name",
             "X5": "Normalized affiliation name", "X6": "Author sequence number"})

    @property
    @save_sframe(sframe="PapersOrderedAuthorsList.sframe")
    def papers_authors_lists(self):
        """
        Create SFrame in which each row contains paper id and a sorted list of the paper's authors
        """

        authors_sf = self.paper_author_affiliations["Paper ID", "Author ID", "Author sequence number"]
        authors_sf['Author_Seq'] = authors_sf.apply(lambda r: [r["Author ID"], r["Author sequence number"]])
        g = authors_sf.groupby("Paper ID", {"Authors List": agg.CONCAT('Author_Seq')})
        g['Authors List Sorted'] = g["Authors List"].apply(lambda l: sorted(l, key=lambda i: i[1]))
        g['Authors List Sorted'] = g['Authors List Sorted'].apply(lambda l: [i[0] for i in l])
        g = g.remove_column("Authors List")
        g = g["Paper ID", 'Authors List Sorted']
        g['Authors Number'] = g['Authors List Sorted'].apply(lambda l: len(l))
        return g

    @property
    @save_sframe(sframe="FieldOfStudyHierarchy.sframe")
    def field_of_study_hierarchy(self):
        """
        Creates field of study hierarchy sframe from txt files
        """
        h_sf = SFrame.read_csv(str(self._dataset_dir / "FieldOfStudyHierarchy.txt"), header=False, delimiter="\t")
        return h_sf.rename({"X1": "Child field of study ID", "X2": "Child field of study level",
                            "X3": "Parent field of study ID", "X4": "Parent field of study level",
                            "X5": "Confidence"})

    def _get_tmp_papers_sframe_path(self, min_ref_num, start_year, end_year):
        """
        Get Papers SFrame path according to years and references number filters
        :param min_ref_num: paper's minimal references number
        :param start_year: start year
        :param end_year: end year
        :return: a path to the Papers SFrame which contains papers with the above filter
        :rtype: PosixPath
        """
        return self._dataset_dir / f"papers_sframe_minref_{min_ref_num}_{start_year}_{end_year}"

    def get_papers_sframe(self, min_ref_num=None, start_year=None, end_year=None):
        """
        Return SFrame with Papers data according to the input filter variables
        :param min_ref_num:  paper's minimal references number
        :param start_year: start year (only include paper that were published after start year)
        :param end_year: end year (only include paper that were published before end year)
        :return: SFrame with paper data
        :rtype: SFrame
        :note: after the SFrame is created it is saved to the TMP_DIR to future use
        """
        sf = self.references
        tmp_papers_sf_path = self._get_tmp_papers_sframe_path(min_ref_num, start_year, end_year)
        if tmp_papers_sf_path.is_dir():
            return load_sframe(str(tmp_papers_sf_path))

        if min_ref_num is not None:
            sf = sf.groupby('Paper ID', {'Ref Count': agg.COUNT()})  # There are 30058322 in the list
            sf = sf[sf['Ref Count'] >= min_ref_num]  # left with 22,083,058
            sf.__materialize__()
        p_sf = self.papers
        sf = p_sf.join(sf)
        if start_year is not None:
            sf = sf[sf['Paper publish year'] >= start_year]
        if end_year is not None:
            sf = sf[sf['Paper publish year'] <= end_year]
        sf.__materialize__()

        if not tmp_papers_sf_path.is_dir():
            sf.save(str(tmp_papers_sf_path))

        return sf

    @property
    @save_sframe(sframe="AuthorNames.sframe")
    def author_names(self):
        """
        Creates authors names SFrames from txt files
        """
        author_names = SFrame.read_csv(str(self._dataset_dir / "AuthorNames.txt"), header=False, delimiter="\t")
        author_names = author_names.rename({'X1': 'Author ID', 'X2': 'Author name'})
        author_names['First name'] = author_names['Author name'].apply(lambda s: s.split()[0])
        author_names['Last name'] = author_names['Author name'].apply(lambda s: s.split()[-1])
        return author_names

    @save_sframe(sframe="PapersFieldsOfStudy.sframe")
    def papers_fields_of_study(self, flevels=(0, 1, 2, 3)):
        """
        Create SFrame with each paper fields of study by hierarchical levels
        :param flevels: list of levels, for each level add the papers fields of study in this level
        """

        k_sf = self.keywords
        g = k_sf.groupby('Paper ID', {'Field of study list': agg.CONCAT("Field of study ID mapped to keyword")})
        fh = FieldsHierarchyAnalyzer()

        # add fields of study names from ID
        names = []
        for l in g['Field of study list']:
            names.append([fh.get_field_name(i) for i in l])
        g['Field of study list names'] = names

        for flevel in flevels:
            parent_list = []
            for paper_field_of_study_list in g['Field of study list']:
                parent_list.append(
                    list(set.union(
                        *[fh.get_parents_field_of_study(field, flevel) for field in paper_field_of_study_list])))
            g[f'Fields of study parent list (L{flevel})'] = parent_list

            names = []
            for paper_field_of_study_parents_list in g[f'Fields of study parent list (L{flevel})']:
                names.append(
                    [fh.get_field_name(field_of_study) for field_of_study in paper_field_of_study_parents_list])
            g[f'Fields of study parent list names (L{flevel})'] = names
        return g

    @property
    @save_sframe(sframe="ExtendedPaperReferences.sframe")
    def extended_references(self):
        """
        Create SFrame with references data with additional column that state if the reference is self-citation
        """

        ref_sf = self.references
        p_sf = self.papers_authors_lists
        ref_sf = ref_sf.join(p_sf, on='Paper ID', how="left")
        ref_sf = ref_sf.join(p_sf, on={'Paper reference ID': 'Paper ID'}, how="left")
        ref_sf = ref_sf.fillna('Authors List Sorted.1', [])
        ref_sf = ref_sf.fillna('Authors List Sorted', [])
        ref_sf.__materialize__()
        ref_sf['self citation'] = ref_sf.apply(
            lambda r: len(set(r['Authors List Sorted.1']) & set(r['Authors List Sorted'])))
        ref_sf.__materialize__()
        return ref_sf.remove_columns(['Authors List Sorted.1', 'Authors List Sorted'])

    def _get_total_citation_by_year(self, year_citation, max_year=2015):
        """
        Calculate the total citation by year
        :param year_citation:  list of (year, citation) tuple
        :param max_year: the maximal year
        :return: dict with the total number of citation in each year
        """
        min_year = int(min([y for y, c in year_citation]))
        total_citations_dict = {}
        for i in range(min_year, int(max_year + 1)):
            total_citations_dict[str(i)] = sum([v for y, v in year_citation if y <= i])
        return total_citations_dict

    def _papers_citations_number_by_year(self, without_self_citation=True):
        """
        Get papers total number of citation in each year
        :param without_self_citation: if True calculate only non-self citations, other calculate with self-citations
        :return: SFrame with a column that contains citations_dict by year
        """
        ref_sf = self.extended_references
        if without_self_citation:
            ref_sf = ref_sf[ref_sf['self citation'] == 0]

        sf = self.papers["Paper ID", "Paper publish year"]
        sf = ref_sf.join(sf, on="Paper ID")
        g = sf.groupby(["Paper reference ID", "Paper publish year"], {"Citation Number": agg.COUNT()})
        g = g.rename({"Paper publish year": "Year", "Paper reference ID": "Paper ID"})
        g['Citation by Year'] = g.apply(lambda r: (r["Year"], r["Citation Number"]))
        h = g.groupby('Paper ID', {'Citation by Years': agg.CONCAT('Citation by Year')})
        if without_self_citation:
            h['Total Citations by Year without Self Citations'] = h['Citation by Years'].apply(
                lambda l: self._get_total_citation_by_year(l))
        else:
            h['Total Citations by Year'] = h['Citation by Years'].apply(lambda l: self._get_total_citation_by_year(l))
        return h.remove_column("Citation by Years")

    @property
    @save_sframe(sframe="PapersCitationByYear.sframe")
    def papers_citation_number_by_year(self):
        """
        Create SFrame with each paper's citation numbers by year dict
        (one dict with self-citations and the other without)
        """

        r_sf = self._papers_citations_number_by_year(False)
        r_sf2 = self._papers_citations_number_by_year(True)
        return r_sf.join(r_sf2, on="Paper ID")

    @property
    @save_sframe(sframe="PaperUrls.sframe")
    def urls(self):

        """
        Creating URLs SFrame from txt files
        """
        sf = SFrame.read_csv(str(self._dataset_dir / "PaperUrls.txt"), header=False, delimiter="\t")
        sf = sf.rename({"X1": "Paper ID", "X2": "Url"})
        return sf.groupby("Paper ID", {"Urls": agg.CONCAT("Url")})

    @property
    @save_sframe(sframe="ExtendedPapers.sframe")
    def extended_papers(self):
        """
        Created extended papers SFrame which contains various papers features, such as
        paper citation numbers, authors list, urls, etc.
        :return:
        """
        sf = self.papers
        sframe_list = [self.reference_count, self.papers_citation_number_by_year, self.papers_authors_lists,
                       self.paper_keywords_list, self.papers_fields_of_study(), self.urls]

        for s in sframe_list:
            t = load_sframe(s)
            sf = sf.join(t, how="left", on="Paper ID")
        return sf.fillna("Ref Number", 0)

    def _create_field_of_study_paper_ids(self, level):
        """
        Create SFrame in which each row contains a field of study and it's matching list of paper ids
        :param level: field of study level
        :return: SFrame with the fields of study in the input level papers ids
        :rtype: SFrame
        """

        col = 'Fields of study parent list (L%s)' % level
        sf = self.extended_papers
        new_col_name = "Field ID"
        sf = sf.stack(col, new_column_name=new_col_name)
        sf = sf[sf[col] != None]
        g = sf.groupby(new_col_name, {'Paper IDs': agg.CONCAT("Paper ID")})
        f_sf = self.fields_of_study
        g = g.join(f_sf, on={new_col_name: "Field of study ID"})
        g['Number of Paper'] = g['Paper IDs'].apply(lambda l: len(l))
        g['Level'] = level
        return g.rename({new_col_name: "Field of study ID"})

    @save_sframe(sframe="FieldsOfStudyPapersIds.sframe")
    def fields_of_study_papers_ids_sframes(self, levels=(1, 2, 3)):
        """
        Creates SFrames with each Fields of study paper ids
        :param levels: list of fields of study level

        """

        sf = SFrame()
        for level in levels:
            sf = sf.append(self._create_field_of_study_paper_ids(level))
        return sf
