import graphlab as gl
import graphlab.aggregate as agg

#working on papers with at most 5 citations
r_sf = gl.load_sframe('./PaperReferences.sframe')

r_sf = r_sf.groupby('Paper ID', {'Ref Count': agg.COUNT()}) #There are 30058322 in the list
r_sf.save('/data/sframes/PapersRefCount.sframe')
r_sf = r_sf[r_sf['Ref Count'] >= 5] # left with 22,083,058

p_sf = gl.load_sframe("./Papers.sframe/") #126,903,970 rows
p_sf = r_sf.join(p_sf) # 22,082,741
p_sf.save('./PapersMin5Ref.sframe')



p_sf = gl.load_sframe('./PapersMin5Ref.sframe')
a_sf = gl.load_sframe('./PaperAuthorAffiliations.sframe/') # 337000127
sf = p_sf[['Paper ID']].join(a_sf) # 86,561,861 rows
sf = sf.join(p_sf, on="Paper ID")
sf.groupby("Author ID", {'Papers Count': agg.COUNT_DISTINCT('Paper ID'),
            'start_year': agg.MIN('Paper publish year'), 'last_year': agg.MAX('Paper publish year'),
           'mean_ref_count': agg.AVG('Ref Count'), 'papers_list': agg.CONCAT('Paper ID'),
           'journals_list': agg.CONCAT('Journal ID mapped to venue name'),
            'conference_list': agg.CONCAT('Conference ID mapped to venue name'),
            'affilation_list': agg.CONCAT('Affiliation ID')
                         })



sf = gl.SFrame()
r = re.compile("\d{4}")
for i in l:
    try:
        y = r.findall(i)[0]
        x = gl.SFrame.read_csv("%s/%s" % (p,i))
        x['Year'] = y
        x['Total Docs'] = x['Total Docs. (%s)' % y ]
        x = x['Title', 'H index', 'SJR Best Quartile', 'SJR', 'Type', 'Rank', 'Year', 'Total Docs' ]
        sf = sf.append(x)
    except:
        continue