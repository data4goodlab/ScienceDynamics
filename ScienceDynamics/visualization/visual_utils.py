import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def filter_sframe_by_years(sf, start_year, end_year):
    """
    Filter the sframe row to include only rows between the start & end years
    :param sf: SFrame which include "Year" column
    :param start_year:  start year
    :param end_year: end year
    :return: return SFrame with row with "Year" column between the start & end year
    :rtype: tc.SFrame
    """
    if start_year is not None:
        sf = sf[sf['Year'] >= start_year]
    if end_year is not None:
        sf = sf[sf['Year'] <= end_year]
    return sf


def draw_feature_yearly_func_value(sf, col_name, var_name, start_year, end_year, func_name="agg.AVG", title=None):
    """
    Return a Altair chart of the input feature between the start & end year using Turicreate aggregation function
    :param sf: SFrame object
    :param col_name: column name
    :param var_name: the new aggregate varilable name (this also will be the chart's Y-axis
    :param start_year: start year
    :param end_year: end year
    :param func_name: Turicreate aggregation function name, such as agg.AVG, agg,MAX, and etc
    :param title: chart title
    :return: chart with the with the yearly aggregated values of the input column
    :rtyoe: alt.Chart
    """
    sf = filter_sframe_by_years(sf, start_year, end_year)
    g = sf.groupby("Year", {var_name: eval("%s('%s')" % (func_name, col_name))})
    g = g.sort("Year")
    df = g.to_dataframe()
    if title is not None:
        chart = alt.Chart(df, title=title)
    else:
        chart = alt.Chart(df)
    chart = chart.mark_line().encode(
        alt.X('Year:Q', axis=alt.Axis(format='d'), scale=alt.Scale(zero=False)),
        alt.Y('%s:Q' % var_name, scale=alt.Scale(zero=False)),

    )
    return chart


def draw_features_yearly_chart(sf, y_col, start_year, end_year, title=None):
    """
    Returns a chart with the yearly values between start and end input years
    :param sf: SFrame object
    :param y_col: the name of the column with the Y values
    :param start_year: start year
    :param end_year:  end year
    :param title:  chart title
    :return: chart with the yearly values of the SFrame columns that will be used as categories
    :rtype: alt.CHart
    """
    sf = filter_sframe_by_years(sf, start_year, end_year)
    df = sf.to_dataframe()
    df = df.fillna(0)
    df = df.sort_values(by=["Year"])
    if title is not None:
        chart = alt.Chart(df, title=title)
    else:
        chart = alt.Chart(df)
    chart = chart.mark_line().encode(
        alt.X('Year:Q', axis=alt.Axis(format='d'), scale=alt.Scale(zero=False)),
        alt.Y('%s:Q' % y_col, scale=alt.Scale(zero=False)),

    )

    return chart


def draw_features_yearly_chart_multi_lines(sf, var_name, value_name, start_year, end_year, title=None):
    """
    Returns a chart with the yearly values between start and end input years, where the column names are the chart
    categories  and the column values are the graph values in each category
    :param sf: SFrame object
    :param var_name: The name of categories column (will also be use in the chart legend)
    :param value_name: The name of the new values column (will also be used as Y-axis lable)
    :param start_year: start year
    :param end_year:  end year
    :param title:  chart title
    :return: chart with the yearly values of the SFrame columns that will be used as categories
    :rtype: alt.CHart
    """
    sf = filter_sframe_by_years(sf, start_year, end_year)
    df = sf.to_dataframe()
    df = df.fillna(0)
    df = pd.melt(df, id_vars=["Year"],
                 var_name=var_name, value_name=value_name)
    df = df.sort_values(by=['Year'])
    if title is not None:
        chart = alt.Chart(df, title=title)
    else:
        chart = alt.Chart(df)

    chart = chart.mark_line().encode(
        alt.X('Year:Q', axis=alt.Axis(format='d'), scale=alt.Scale(zero=False)),
        alt.Y('%s:Q' % value_name, scale=alt.Scale(zero=False)),
        color=var_name
    )
    return chart


def draw_features_decade_dist(sf, var_name, start_year, end_year, col_warp=4, sharex=False, sharey=False):
    """
    Return chart using seaborn package that draw the SFrame input var name distribution over the decades
    :param sharey:
    :param sf: input sframe
    :param var_name: input varname
    :param start_year: start year
    :param end_year: end year
    :param col_warp: number of columns in each row
    :param sharex: if True share X-axis otherwise each subplot will have it's own X-axis
    :param sharex: if True share Y-axis otherwise each subplot will have it's own Y-axis
    :return: chart with subplots which each subplot contains the var_name distrubtion in specific decade
    """
    sf = filter_sframe_by_years(sf, start_year, end_year)
    sf["Decade"] = sf["Year"].apply(lambda y: y - y % 10)
    df = sf["Decade", var_name].to_dataframe()

    df = df.sort_values(by=['Decade'])
    g = sns.FacetGrid(df, col="Decade", col_wrap=col_warp, aspect=3, sharex=sharex, sharey=sharey)
    g = g.map(sns.distplot, var_name)
    return g


def draw_layered_hist(sf, feature_col_name, decades_list, start_year, end_year, xlim=None, xlabel=None, ylabel=None):
    n = len(decades_list)
    sf = filter_sframe_by_years(sf, start_year, end_year)
    s = set(decades_list)
    sf["Decade"] = sf["Year"].apply(lambda y: y - y % 10)
    sf = sf["Decade", feature_col_name]
    df = sf[sf['Decade'].apply(lambda decade: decade in s)].to_dataframe()
    colors = sns.color_palette("hls", n)

    for i in range(n):
        d = decades_list[i]
        c = colors[i]
        sns.distplot(df[df["Decade"] == d][feature_col_name], color=c, label="%ss" % d)
    plt.legend()
    if xlim is not None:
        plt.xlim(*xlim)
    if xlabel is not None:
        plt.xlabel(xlabel)

    if ylabel is not None:
        plt.ylabel(ylabel)
