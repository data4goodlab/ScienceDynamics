import turicreate as tc
import turicreate.aggregate as agg


# data from http://www.ssa.gov/oact/babynames/names.zip
# and from wikitree
def create_ground_truth_names(baby_names_path, wikitree_users_path, ratio=0.9):
    """
    Createing SFrame with statistics on first name gender probability using data from WikiTree and SSA
    :param baby_names_path: the file to SSA baby names files
    :param wikitree_users_path: link to file with WikiTree names
    :param ratio: the ratio that above it the name gender is considered male
    :return: SFrame with data regarding first name gender
    :rtype: tc.SFrame
    :note: first names data files can be downloaded from  http://www.ssa.gov/oact/babynames/names.zip and
            https://www.wikitree.com/wiki/Help:Database_Dumps
    """
    sf = tc.SFrame.read_csv("%s/*.txt" % baby_names_path, header=False)
    sf = sf.rename({'X1':'First Name', 'X2':'Gender', 'X3': 'Count'})


    w_sf = tc.SFrame.read_csv(wikitree_users_path, delimiter="\t", header=True)
    w_sf = w_sf[['Preferred Name','Gender']]
    w_sf = w_sf.rename({'Preferred Name': 'First Name'})
    w_sf = w_sf[w_sf['Gender'] != 0]
    w_sf['First Name'] = w_sf['First Name'].apply(lambda n: n.split()[0] if len(n) > 0 else '')
    w_sf = w_sf[w_sf['First Name'] != '' ]
    w_sf['Gender'] = w_sf['Gender'].apply(lambda g: 'M' if g == 1 else 'F')
    w_sf = w_sf.groupby(['First Name', 'Gender'], {'Count': agg.COUNT()})

    sf = sf.append(w_sf)
    sf['First Name'] = sf['First Name'].apply(lambda n: n.lower())
    g = sf.groupby(['First Name', 'Gender'], agg.SUM('Count'))



    g['stat'] = g.apply(lambda r: (r['Gender'], r['Sum of Count']))
    sf = g.groupby('First Name', {'Stats': agg.CONCAT('stat') })
    sf['Total Births'] = sf['Stats'].apply(lambda l: sum([i[1] for i in l]))
    sf['Total Males'] = sf['Stats'].apply(lambda l: sum([i[1] for i in l if i[0] == 'M']))
    sf['Percentage Males'] = sf.apply(lambda r: float(r['Total Males'])/r['Total Births'])
    sf = sf[sf['Total Births'] >= 5]
    def get_name_gender(p):
        if p >= ratio:
            return 'Male'
        if p<= (1-ratio):
            return 'Female'
        return 'Unisex'

    sf['Gender'] = sf['Percentage Males'].apply(lambda p: get_name_gender(p))
    sf = sf.remove_column('Stats')

    return sf