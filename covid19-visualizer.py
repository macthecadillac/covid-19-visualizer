import urllib.request as request

import pandas as pd

from matplotlib.pyplot import figure
from matplotlib import rcParams

rcParams['font.family'] = 'Carlito'


def plot(suffix, df, xheader, yheader, xscale, yscale, locations, kwarg={}):
    print('\r Plotting {} vs {}...'.format(yheader, xheader), end='')

    fig = figure(figsize=(13, 9))
    ax = fig.add_subplot(111, xscale=xscale, yscale=yscale)

    for location in locations:
        if xheader == 'date':
            ys = df.loc[location].filter([yheader]).squeeze()
            # the first time we reset the indices, we reset the counter. We use
            # the second time to create our x series.
            series = ys[ys != 0].rolling(window=7).mean().reset_index(drop=True) \
                       .dropna() \
                       .squeeze()
        else:
            series = df.loc[location] \
                    .filter(items=[xheader, yheader]) \
                    .rolling(window=7, on=xheader).mean() \
                    .set_index([xheader], drop=True) \
                    .dropna() \
                    .squeeze()

        if not series.size == 0:
            ax.plot(series.index, series.values, **kwarg)
            *_, last = series.items()
            ax.annotate(location, last, fontsize=8)

    if xheader == 'date':
        xlabel = 'time since first infection (days)'.title()
    else:
        xlabel = xheader.replace('_', ' ')
    ylabel = yheader.replace('_', ' ')
    title = 'COVID-19 {} vs. {}'.format(ylabel, xlabel)

    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel.title(), fontsize=12)
    ax.set_ylabel(ylabel.title(), fontsize=12)
    ax.tick_params(labelsize=8, length=3.5, width=0.5)

    fig.savefig('{}-{}.png'.format(title, suffix))
    print('\r Done.                                        ', end='')


def retrieve_owid_dataset():
    url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
    fpath = 'owid-covid-data.csv'
    return retrive_dataset(url, fpath)


def retrieve_nytimes_dataset():
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    fpath = 'us-state-by-statecovid-data.csv'
    return retrive_dataset(url, fpath)


def retrive_dataset(url, fpath):
    print('\r Downloading dataset...', end='')
    request.urlretrieve(url, fpath)
    print('\r Done.', end='')
    return pd.read_csv(fpath, sep=',')


if __name__ == '__main__':
    # Plot a selection of countries
    countries = ['China', 'Singapore', 'South Korea', 'Japan',
                 'United States', 'United Kingdom', 'Ireland', 'France',
                 'Russia', 'Israel', 'Taiwan', 'India', 'Australia',
                 'New Zealand', 'Canada', 'Mexico', 'Italy']

    worldwide_data = retrieve_owid_dataset()
    worldwide_data.rename(columns={'total_cases': 'running total',
                                   'new_cases': 'daily_new_cases'},
                                   inplace=True)
    worldwide_data.set_index(['location', 'date'], inplace=True)

    plot('by country', worldwide_data,
         'date', 'running total', 'linear', 'log', countries,
         kwarg={'linestyle': ':', 'linewidth': 0.5})

    plot('by country', worldwide_data,
         'running total', 'daily_new_cases', 'log', 'log', countries,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by country', worldwide_data,
         'new_tests', 'daily_new_cases', 'log', 'log', countries,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by country', worldwide_data,
         'date', 'new_tests', 'linear', 'log', countries,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by country', worldwide_data,
         'running total', 'total_deaths', 'log', 'log', countries,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    # Plot US States
    us_data = retrieve_nytimes_dataset()

    states = ['California', 'Massachusetts', 'New York', 'Washington',
              'New Jersey', 'Oregon', 'Kansas', 'Texas', 'Georgia',
              'Florida', 'Arizona', 'Vermont', 'Hawaii', 'Montana',
              'Alaska', 'Idaho']

    data_by_state = []
    for state in states:
        df = us_data.set_index(['state', 'date']).loc[state].sort_values(by=['date'])
        df['location'] = state
        df['daily_new_cases'] = df['cases'].diff()
        data_by_state.append(df.reset_index().set_index(['location', 'date'], drop=True))

    us_data = pd.concat(data_by_state).rename(columns={'cases': 'running total'})

    plot('by US state', us_data,
         'running total', 'daily_new_cases', 'log', 'log', states,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by US state', us_data,
         'date', 'daily_new_cases', 'linear', 'linear', states,
         kwarg={'linestyle': ':', 'linewidth': 1})

    plot('by US state', us_data,
         'running total', 'deaths', 'log', 'log', states,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})
