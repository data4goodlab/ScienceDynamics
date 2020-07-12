import pathlib
from turicreate import SFrame, load_sframe
from ScienceDynamics.datasets.utils import download_file, save_sframe
import turicreate.aggregate as agg
from tqdm import tqdm
from ScienceDynamics.sframe_creators.fields_of_study_hieararchy_analyzer import FieldsHierarchyAnalyzer
from ScienceDynamics.fetchers.wikipedia_fetcher import WikiLocationFetcher
from ScienceDynamics.datasets.configs import MAG_URL_DICT

import pandas as pd
import re
from array import array


class MicrosoftAcademicGraph(object):
    def __init__(self, dataset_dir=None, download=False):
        if dataset_dir is None:
            dataset_dir = DATASETS_BASE_DIR
        self._dataset_dir = pathlib.Path(dataset_dir)
        self._dataset_dir.mkdir(exist_ok=True)
        self._sframe_dir = self._dataset_dir / "sframes"
        self._sframe_dir.mkdir(exist_ok=True)
        if download:
            for i, url in enumerate(MAG_URL_DICT.values()):
                mag_file = self._dataset_dir / re.search(".*files\/(.*?)\?", url).group(1)
                if not pathlib.Path(mag_file).exists():
                    download_file(url, mag_file)
                    # with zipfile.ZipFile(mag_file, 'r') as f:
                    #     f.extractall(self._dataset_dir)

    @property
    @save_sframe(sframe="Papers.sframe")
    def papers(self):
        """
        Create the Papers SFrame object from.txt.gz files which contains information on each paper
        """
        cols = ["PaperId", "Rank", "Doi", "DocType", "PaperTitle", "OriginalTitle", "BookTitle", "Year", "Date",
                "Publisher", "JournalId", "ConferenceSeriesId", "ConferenceInstanceId", "Volume", "Issue", "FirstPage",
                "LastPage", "ReferenceCount", "CitationCount", "EstimatedCitation", "OriginalVenue", 
                "CreatedDate"]
        papers = SFrame.read_csv(str(self._dataset_dir / "Papers.txt.gz"),header=False, sep="\t")
        papers = papers.rename(dict(zip([f"X{i+1}" for i in range(len(cols))], cols)))
        papers["Year"] = papers["Year"].astype(int)
        return papers
    

    @property
    @save_sframe(sframe="Journals.sframe")
    def journals(self):
        """
        Create the Papers SFrame object from.txt.gz files which contains information on each paper
        """
        cols = ["JournalId", "Rank", "NormalizedName", "DisplayName", "Issn", "Publisher", "Webpage", "PaperCount", "CitationCount",
                "CreatedDate"]
        journals = SFrame(pd.read_csv(self._dataset_dir /"Journals.txt.gz", sep="\t",
                                          names=cols).replace({pd.NA: None}))
        return journals
    
    
    @property
    @save_sframe(sframe="Authors.sframe")
    def authors(self):
        """
        Creates authors names SFrames from.txt.gz files
        """
        authors = SFrame(pd.read_csv(self._dataset_dir /"Authors.txt.gz", sep="\t",
                                          names=["AuthorId", "Rank", "NormalizedName", "DisplayName",
                                                 "LastKnownAffiliationId", "PaperCount",
                                                 "CitationCount", "CreatedDate"]).replace({pd.NA: None}))
        authors['First name'] = authors['NormalizedName'].apply(lambda s: s.split()[0])
        authors['Last name'] = authors['NormalizedName'].apply(lambda s: s.split()[-1])
        return authors
    
        
    @property
    def author_names(self):
        """
        Creates authors names SFrames from.txt.gz files
        """
        return self.authors[["AuthorId", "NormalizedName"]]

    @property
    @save_sframe(sframe="PaperReferences.sframe")
    def references(self):
        """Creating the references SFrame from.txt.gz files"""
        references = SFrame.read_csv(str(self._dataset_dir / "PaperReferences.txt.gz"), header=False, delimiter="\t")
        references = references.rename({"X1": "PaperId", "X2": "PaperReferenceId"})
        return references

    @property
    @save_sframe(sframe="PaperReferencesCount.sframe")
    def reference_count(self):
        return self.references.groupby("PaperId", {"Ref Number": agg.COUNT()})

    @property
    @save_sframe(sframe="PaperFieldsOfStudy.sframe")
    def paper_fields_of_study(self):
        """
        Creating Keywords SFrame from.txt.gz files
        """
        cols = ["PaperId", "FieldOfStudyId", "Score"]
        papaers_field = SFrame.read_csv("~/mag/PaperFieldsOfStudy.txt.gz",header=False, sep="\t")
        return papaers_field.rename(dict(zip([f"X{i+1}" for i in range(len(cols))], cols)))

#         return keywords.rename({"X1": "PaperId", "X2": "Keyword name", "X3": "Field of study ID mapped to keyword"})

    # @property
    # @save_sframe(sframe="PaperKeywordsList.sframe")
    # def paper_keywords_list(self):
    #     """
    #     Creating Paper Keywords List SFrame
    #     """
    #     return self.paper_pields_of_study.groupby("PaperId", {"Field List": agg.CONCAT("Keyword name")})

    @property
    @save_sframe(sframe="FieldsOfStudy.sframe")
    def fields_of_study(self):
        """
        Creating Field of study SFrame from.txt.gz files
        """
        cols = ["FieldOfStudyId", "Rank", "NormalizedName", "DisplayName", "MainType", "Level", "PaperCount", "CitationCount", "CreatedDate"]
        fields_of_study = SFrame(pd.read_csv(self._dataset_dir / "FieldsOfStudy.txt.gz", sep="\t",
                                    names=cols).replace({pd.NA: None}))
        return fields_of_study
    
    @property
    @save_sframe(sframe="PaperResources.sframe")
    def paper_resources(self):
        """
        Creating Field of study SFrame from.txt.gz files
        ResourceType. 1 = Project, 2 = Data, 4 = Code
        """
        cols = ["PaperId", "ResourceType", "ResourceUrl", "SourceUrl", "RelationshipType"]
        return SFrame(pd.read_csv(self._dataset_dir / "PaperResources.txt.gz", sep="\t",
                                    names=cols).replace({pd.NA: None}))


    @property
    @save_sframe(sframe="PaperAuthorAffiliations.sframe")
    def paper_author_affiliations(self):
        """
        Creating authors affiliation SFrame from.txt.gz files
        :return:
        """
        cols = ["PaperId", "AuthorId", "AffiliationId", "AuthorSequenceNumber", "OriginalAuthor", "OriginalAffiliation"]
        paper_author_affiliations = SFrame(pd.read_csv(self._dataset_dir / "PaperAuthorAffiliations.txt.gz", sep="\t",
                                             names=cols).replace({pd.NA: None}))

        return paper_author_affiliations
    
    @property
    @save_sframe(sframe="Affiliations.sframe")
    def affiliations(self):
        """
        Creating authors affiliation SFrame from.txt.gz files
        :return:
        """
        cols = ["AffiliationId", "Rank", "NormalizedName", "DisplayName", "GridId", "OfficialPage", "WikiPage", "PaperCount", "CitationCount", "CreatedDate"]
        affiliations = SFrame(pd.read_csv(self._dataset_dir / "Affiliations.txt.gz", sep="\t",
                                             names=cols).replace({pd.NA: None}))

        return affiliations


    def add_geo_data_to_affiliations(self, max_workers=2):
        """
        Creating authors affiliation SFrame from.txt.gz files
        :return:
        """
        fields = ["AffiliationId", "Rank", "NormalizedName", "DisplayName", "GridId", "OfficialPage", "WikiPage", "PaperCount", "CitationCount", "CreatedDate"]
        wl = WikiLocationFetcher(self.affiliations[fields], max_workers)
        wl.add_location_data()
        wl.aff.save(f"{self._sframe_dir}/Affiliations.sframe")
        
        
    @property
    @save_sframe(sframe="PapersOrderedAuthorsList.sframe")
    def papers_authors_lists(self):
        """
        Create SFrame in which each row contains PaperId and a sorted list of the paper's authors
        """

        authors_sf = self.paper_author_affiliations["PaperId", "AuthorId", "AuthorSequenceNumber"]
        authors_sf['Author_Seq'] = authors_sf.apply(lambda r: [r["AuthorId"], r["AuthorSequenceNumber"]])
        g = authors_sf.groupby("PaperId", {"Authors List": agg.CONCAT('Author_Seq')})
        g['Authors List Sorted'] = g["Authors List"].apply(lambda l: sorted(l, key=lambda i: i[1]))
        g['Authors List Sorted'] = g['Authors List Sorted'].apply(lambda l: [i[0] for i in l])
        g = g.remove_column("Authors List")
        g = g["PaperId", 'Authors List Sorted']
        g['Authors Number'] = g['Authors List Sorted'].apply(lambda l: len(l))
        return g

    @property
    @save_sframe(sframe="FieldOfStudyChildren.sframe")
    def field_of_study_children(self):
        """
        Creates field of study hierarchy sframe from.txt.gz files
        """
        h_sf = SFrame.read_csv(str(self._dataset_dir / "FieldOfStudyChildren.txt.gz"), header=False, delimiter="\t")
        return h_sf.rename({"X1": "FieldOfStudyId", "X2": "ChildFieldOfStudyId"})

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
            sf = sf.groupby('PaperId', {'Ref Count': agg.COUNT()})  # There are 30058322 in the list
            sf = sf[sf['Ref Count'] >= min_ref_num]  # left with 22,083,058
            sf.__materialize__()
        p_sf = self.papers
        sf = p_sf.join(sf)
        if start_year is not None:
            sf = sf[sf['Year'] >= start_year]
        if end_year is not None:
            sf = sf[sf['Year'] <= end_year]
        sf.__materialize__()

        if not tmp_papers_sf_path.is_dir():
            sf.save(str(tmp_papers_sf_path))

        return sf
    
    @property
    @save_sframe(sframe="PaperFieldsOfStudy.sframe")
    def papers_fields_of_study(self):
        """Creating the references SFrame from.txt.gz files"""
        fos = SFrame.read_csv(str(self._dataset_dir / "PapersFieldsOfStudy.txt.gz"), header=False, delimiter="\t")
        return references.rename({"X1": "PaperId", "X2": "FieldOfStudyId", "X3": "Score"})

    
    @save_sframe(sframe="PapersFieldsOfStudyLevel.sframe")
    def papers_fields_of_study_level(self, flevels=(0, 1, 2, 3)):
        """
        Create SFrame with each paper fields of study by hierarchical levels
        :param flevels: list of levels, for each level add the papers fields of study in this level
        """
        k_sf = self.paper_fields_of_study
#         FieldOfStudyId
        g = k_sf.groupby('PaperId', {'Field of study list': agg.CONCAT("FieldOfStudyId")})
        fh = FieldsHierarchyAnalyzer(self)
    
        # add fields of study names from ID
        names = []
        for l in tqdm(g['Field of study list']):
            names.append([fh.get_field_name(i) for i in l])
        g['Field of study list names'] = names
    
        for flevel in flevels:
            parent_list = []
            for paper_field_of_study_list in tqdm(g['Field of study list']):
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
        ref_sf = ref_sf.join(p_sf, on='PaperId', how="left")
        ref_sf = ref_sf.join(p_sf, on={'PaperReferenceId': 'PaperId'}, how="left")
        ref_sf = ref_sf.fillna('Authors List Sorted.1', array('d'))
        ref_sf = ref_sf.fillna('Authors List Sorted', array('d'))
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

        sf = self.papers["PaperId", "Year"]
        sf = ref_sf.join(sf, on="PaperId")
        g = sf.groupby(["PaperReferenceId", "Year"], {"Citation Number": agg.COUNT()})
        g = g.rename({"Year": "Year", "PaperReferenceId": "PaperId"})
        g['Citation by Year'] = g.apply(lambda r: (r["Year"], r["Citation Number"]))
        h = g.groupby('PaperId', {'Citation by Years': agg.CONCAT('Citation by Year')})
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
        return r_sf.join(r_sf2, on="PaperId")

    @property
    @save_sframe(sframe="PaperUrls.sframe")
    def urls(self):

        """
        Creating URLs SFrame from.txt.gz files
        """
        cols = ["PaperId", "SourceType", "SourceUrl", "LanguageCode"]
        urls = SFrame(pd.read_csv(self._dataset_dir / "PaperUrls.txt.gz", sep="\t",
                                    names=cols).replace({pd.NA: None}))
        return urls.groupby("PaperId", {"Urls": agg.CONCAT("SourceUrl")})

    @property
    @save_sframe(sframe="ExtendedPapers.sframe")
    def extended_papers(self):
        """
        Created extended papers SFrame which contains various papers features, such as
        paper citation numbers, authors list, urls, etc.
        :return:
        """
        sf = self.papers
        sframe_list = (self.reference_count, self.papers_citation_number_by_year, self.papers_authors_lists,
                        self.urls, self.papers_fields_of_study_level())
        # self.paper_keywords_list, self.papers_fields_of_study()
        for t in tqdm(sframe_list):
            sf = sf.join(t, how="left", on="PaperId")
        return sf.fillna("Ref Number", 0)

    def _create_field_of_study_paper_ids(self, level):
        """
        Create SFrame in which each row contains a field of study and it's matching list of PaperIds
        :param level: field of study level
        :return: SFrame with the fields of study in the input level papers ids
        :rtype: SFrame
        """

        col = 'Fields of study parent list (L%s)' % level
        sf = self.extended_papers
        new_col_name = "Field ID"
        sf = sf[sf[col] != None]
        sf = sf.stack(col, new_column_name=new_col_name)
        g = sf.groupby(new_col_name, {'PaperIds': agg.CONCAT("PaperId")})
        g[new_col_name] = g[new_col_name].astype(int)
        f_sf = self.fields_of_study
        g = g.join(f_sf, on={new_col_name: "FieldOfStudyId"})
        g['Number of Paper'] = g['PaperIds'].apply(lambda l: len(l))
        g['Level'] = level
        return g.rename({new_col_name: "Field of study ID"})

    @save_sframe(sframe="FieldsOfStudyPapersIds.sframe")
    def fields_of_study_papers_ids(self, levels=(1, 2, 3)):
        """
        Creates SFrames with each Fields of study PaperIds
        :param levels: list of fields of study level

        """

        sf = SFrame()
        for level in tqdm(levels):
            sf = sf.append(self._create_field_of_study_paper_ids(level))
        return sf
