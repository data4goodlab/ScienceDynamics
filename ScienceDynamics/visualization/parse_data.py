import math

def json2nvd3(j):
    d = {}
    for k, v in j.iteritems():
        if k == 'keywords':
            d[k] = keywords_clean(v)
        elif 'gender' in k:
            d[k] = genderdata2nvd3(v)
        else:
            d[k] = data2nvd3(v)
    return d

def data2nvd3(d):
    d = {int(k): v for k, v in d.iteritems() if (isinstance(v, float) or isinstance(v, int) ) and not math.isnan(v)}
    keys = d.keys()
    keys.sort()
    l = []
    for k in keys:
        l.append({'x':k, 'y': d[k]})

    return l

def genderdata2nvd3(d):
    d = {int(k): v for k, v in d.iteritems()  }
    keys = d.keys()
    keys.sort()
    l = []
    for k in keys:
        gender_dict = d[k]
        if "Female" not in gender_dict and "Male" not in gender_dict:
            continue
        if "Female" not in gender_dict:
            gender_dict["Female"] = 0
        if "Male" not in gender_dict:
            gender_dict["Male"] = 0

        y = float(gender_dict["Female"])/(gender_dict["Female"] + gender_dict["Male"])
        l.append({'x':k, 'y': y})
    return l

def keywords_clean(d):
    clean_dict = {}
    for k,v in d.iteritems():
        if v == {}:
            continue
        clean_dict[int(k)] = v
    return clean_dict