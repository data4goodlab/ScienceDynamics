import wptools
from collections import defaultdict
import re 
import wikipedia
import geonamescache
import concurrent
import reverse_geocode
import tldextract
from geonamescache.mappers import country
from tqdm import tqdm
import wikipedia


def get_wikidata(term, c=0):
    try:
        p = wptools.page(term, silent=True).get_wikidata()
        return p.data["wikidata"]
    except LookupError:
        if not c:
            page_name = wikipedia.page(page_name).original_title
            return get_wikidata(page_name, c+1)
    return None


def get_wikidata_from_url(wp):
    try:
        page_name = wp.split("wiki/")[1]
        return get_wikidata(page_name)
    except:
        return None
    

def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i + n]
        
def get_wikidata_from_url_parallel(wiki_pages, max_workers=2, fields=None):
    res = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for wd in tqdm(executor.map(get_wikidata_from_url, wiki_pages), total=len(wiki_pages)):
            if fields is None:
                res.append(wd)
            else:
                if wd:
                    wikidata = defaultdict(str,wd)
                    res.append( {k: wikidata[k] for k in fields})
                else:
                    res.append(None)
        return res


def get_wikipedia_cordinates(wp):
    try:
        page_name = wp.split("wiki/")[1]
        p = wikipedia.page(page_name)
        return p.coordinates
    except:
        pass
    return None

def get_wikipedia_cordinates_parallel(wiki_pages, max_workers = 2):
    res = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for i, e in tqdm(enumerate(executor.map(get_wikipedia_cordinates, wiki_pages)), total=len(wiki_pages)):
            if e is not None:
                res.append(e)
            else:
                res.append({})

    return res

    

class WikiLocationFetcher(object):
    
    def __init__(self, mag_affilations, max_worker=2):
        self.aff = mag_affilations
        self.gc = geonamescache.GeonamesCache()
        cities = self.gc.get_cities()
        countries = self.gc.get_countries()
        self.cities = {v['name'] for k, v in cities.items()}
        self.countries = {v['name'] for k, v in countries.items()}
        self._max_workers = max_worker
        self.mapper = country(from_key='iso', to_key='name')




    def normalize_wiki_location_data(self):
        features = ["coordinate location (P625)", "country (P17)","located at street address (P6375)", "located in the administrative territorial entity (P131)", 'headquarters location (P159)', 'location (P276)']
        res =  get_wikidata_from_url_parallel(self.aff['WikiPage'], self._max_workers, features)
        self.aff["geo"] = res
        self.aff = self.aff.unpack("geo", column_name_prefix="")
        self.aff = self.aff.rename({"country (P17)": "Country", "headquarters location (P159)": "Headquarters Location", 'located at street address (P6375)': "Street Address", "location (P276)":"Location", 'located in the administrative territorial entity (P131)':"Administrative Territorial Entity"})
        cord = [{"latitude": l['coordinate location (P625)']["latitude"], "longitude": l['coordinate location (P625)']["longitude"] } if (l and 'coordinate location (P625)' in l and l['coordinate location (P625)']!="" and type(l['coordinate location (P625)']) ==dict) else {"latitude":"", "longitude":""}  for l in res ]
        self.aff['coordinate location (P625)'] = cord
        self.aff = self.aff.unpack('coordinate location (P625)', column_name_prefix="")
        self.aff["Country"] = self.aff["Country"].apply(lambda x: x.split("(")[0])

    def extract_data_from_location(self):
        self.aff["Location"] = self.aff["Location"].apply(lambda x: x.split("(")[0].strip())
        self.aff["City_Temp"] = self.aff["Location"].apply(lambda x: x if x in self.cities else "")
        self.aff["Country_Temp"] = self.aff["Location"].apply(lambda x: x if x in self.countries else "")
        self.aff["City"] = self.aff.apply(lambda x: x["City"] if x["City"]!="" else x["City_Temp"] )
        self.aff["Country"] = self.aff.apply(lambda x: x["Country"] if x["Country"]!="" else x["Country_Temp"] )
        self.aff["City"] = self.aff.apply(lambda x: x["City_Temp"] if x["City"]!= x["City_Temp"] and  x["City_Temp"]!="" else x["City"])
        self.aff= self.aff.remove_columns(["Country_Temp","City_Temp"])


    def extract_data_from_address(self):
        self.aff["Temp"] = self.aff["Street Address"].apply(lambda x: x.split(","))
        self.aff["City_Temp"] = self.aff["Temp"].apply(lambda x: [c for c in x if c.strip() in self.cities])
        self.aff["City_Temp"] = self.aff["City_Temp"].apply(lambda x: x[0] if len(x) else "")
        self.aff["City"] = self.aff.apply(lambda x: x["City"] if x["City"]!="" else x["City_Temp"] )

        self.aff["Country_Temp"] = self.aff["Temp"].apply(lambda x: [c for c in x if c.strip() in self.countries])
        self.aff["Country_Temp"] = self.aff["Country_Temp"].apply(lambda x: x[0] if len(x) else "")
        self.aff["Country"] = self.aff.apply(lambda x: x["Country"] if x["Country"]!="" else x["Country_Temp"] )
        self.aff= self.aff.remove_columns(["Country_Temp","City_Temp"])


    def extract_data_from_cord(self):
        temp = []
        for x in self.aff:
            if x["latitude"]:
                temp.append(reverse_geocode.search([(x["latitude"], x["longitude"])])[0])
            else:
                temp.append({})
        self.aff["Temp"] = temp
        self.aff["Country"] = self.aff.apply(lambda x: x["Country"] if x["Country"]!="" and x["Country"] is not None else x["Temp"]["country"] if  x["Temp"]!={} and 'country' in x["Temp"]  else "" )
        self.aff["City"] = self.aff.apply(lambda x: x["Temp"]["city"] if  x["Temp"]!={} and 'country' in x["Temp"]  else "" )
        self.aff= self.aff.remove_columns(["Temp"])

    def extract_data_from_atw(self):
        self.aff["Temp"] =self.aff["Administrative Territorial Entity"].apply(lambda x: x.split("(")[0].strip())
        self.aff["Temp"]  =self.aff["Temp"].apply(lambda x: x if x in self.cities else "")
        self.aff["City"] = self.aff.apply(lambda x: x["City"] if x["City"]!="" else x["Temp"] )
        self.aff= self.aff.remove_columns(["Temp"])


    def extract_data_from_headquarters(self):
        self.aff["Temp"] =self.aff["Headquarters Location"].apply(lambda x: x.split("(")[0].strip())
        self.aff["Temp"]  =self.aff["Temp"].apply(lambda x: x if x in self.cities else "")
        self.aff["City"] = self.aff.apply(lambda x: x["City"] if x["City"]!="" else x["Temp"] )
        self.aff= self.aff.remove_columns(["Temp"])


    def extract_country_from_city(self):
        self.aff["Country_Temp"] = self.aff.apply(lambda x: self.gc.get_cities_by_name(x["City"]) if x["City"] and not x["Country"] else [] )
        self.aff["Country_Temp"] = self.aff["Country_Temp"].apply(lambda x: [l.popitem()[1] for l in x] )
        self.aff["Country"] = self.aff.apply(lambda x: x["Country"] if x["Country"]!=""  else self.mapper(x["Country_Temp"][0]["countrycode"]) if len(x["Country_Temp"])==1 else "" )
        self.aff= self.aff.remove_columns(["Country_Temp"])

        

    def extract_wiki_cordinates(self):
        wiki_pages = self.aff[(self.aff["latitude"]== None) | (self.aff["latitude"]=="")][['AffiliationId','WikiPage']]
        
        cords = get_wikipedia_cordinates_parallel(wiki_pages['WikiPage'], self._max_workers)
        res_geo = [reverse_geocode.search([line])[0]  if line!={} else {} for line in cords]
        cords = [[str(line[0]), str(line[1])] if line!={} else [] for line in cords ]
        wiki_pages["geo"] = res_geo
        wiki_pages["geo2"] = cords

        self.aff = self.aff.join(wiki_pages)
        self.aff = self.aff.fillna('geo', {})
        self.aff["Country"] = self.aff.apply(lambda x: x["Country"] if x["Country"]!="" and x["Country"] is not None else x["geo"]["country"] if  x["geo"]!={} and 'country' in x["geo"]  else "" )
        self.aff["City"] = self.aff.apply(lambda x: x["City"] if x["City"]!="" and x["City"] is not None else x["geo"]["city"] if  x["geo"]!={} and 'city' in x["geo"]  else "" )

        self.aff["latitude"] = self.aff.apply(lambda x: x["geo2"][0] if( x["latitude"]=="" or x["latitude"] is None) and x["geo2"] else x["latitude"])
        self.aff["longitude"] = self.aff.apply(lambda x: x["geo2"][1] if( x["longitude"]=="" or x["longitude"] is None) and x["geo2"] else x["longitude"])

        self.aff= self.aff.remove_columns(["geo", "geo2"])



    def extract_country_from_url(self):
        self.aff["Country_Web"] = self.aff["OfficialPage"].apply(lambda x: self.mapper( tldextract.extract(x).suffix.split(".")[-1].upper()))
        self.aff["Country"] = self.aff.apply(lambda x: x["Country"] if x["Country"]!="" else x["Country_Web"] if  x["Country_Web"] is not None  else "" )
        self.aff[self.aff["Country"].apply(lambda x: 1 if "china" in x.lower() else 0)]
        self.aff= self.aff.remove_columns(["Country_Web"])


    def standrtize_names(self):
        country_norm = [("United States","United States of America"),("China" ,"People's Republic of China"),("China" ,"Hong Kong"),("Japan" ,"Empire of Japan"),("Iran","Iran, Islamic Republic of"),("Netherlands" ,'Kingdom of the Netherlands'),("State of Palestine",'Palestinian Territory'),
         ("State of Palestine",'Palestinian territories'),("United States", "Illinois"),("Mexico", 'State of Mexico'),("Russia", 'Russian Empire'),("United States", 'Virgin Islands, U.S.'),("Russia", 'Russian Empire'),("Germany" ,'German Reich'),("Germany",'Weimar Republic'),
        ("Taiwan","Republic of China")]
        country_norm = { orig:rename for rename, orig in country_norm}
        self.aff["Country"] = self.aff["Country"].apply(lambda x: x.strip().strip("[").strip('"'))
        self.aff["City"] = self.aff["City"].apply(lambda x: x.strip().strip("[").strip('"'))

        self.aff["Country"] = self.aff["Country"].apply(lambda x: country_norm[x] if x in country_norm else x)

        
    def add_location_data(self):
        self.normalize_wiki_location_data()
        self.extract_data_from_cord()
        self.extract_data_from_location()
        self.extract_data_from_atw()
        self.extract_data_from_headquarters()
        self.extract_data_from_address()
        self.extract_country_from_city()
        self.extract_wiki_cordinates()
        self.extract_country_from_url()
        self.standrtize_names()
        
        self.aff = self.aff.remove_columns(["Temp","Location","Administrative Territorial Entity", "Street Address","Headquarters Location"])
        for col in self.aff.column_names():
            self.aff[col] = self.aff[col].apply(lambda x: None if x=="" else x)
