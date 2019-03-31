from code.venue import *
from collections import *

v_id = "03B932AA"

va = VenueAnalyzer(v_id, VenueType.journal)
yes_l = va._papers_analyzer.get_papers_in_which_authors_published_in_venue()
no_l = va._papers_analyzer.get_papers_in_which_authors_not_published_in_venue()

pc_y = PaperCollections(papers_list=yes_l)
pc_n = PaperCollections(papers_list=no_l)

for i in range(2000,2015):
        l.append(max(pc_n.get_papers_citations(i)) > max(pc_y.get_papers_citations(i)))

Counter(l)