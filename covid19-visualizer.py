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
            ys = df[df['location'] == location][yheader].squeeze()
            # the first time we reset the indices, we reset the counter. We use
            # the second time to create our x series.
            series = ys[ys != 0].rolling(window=7).mean().reset_index(drop=True) \
                       .reset_index() \
                       .rename(columns={'index': 'x', yheader: 'y'}) \
                       .dropna()
        else:
            series = df[df['location'] == location] \
                    .filter(items=[xheader, yheader]) \
                    .rolling(window=7, on=xheader).mean() \
                    .rename(columns={xheader: 'x', yheader: 'y'}) \
                    .dropna()

        if not series.size == 0:
            ax.plot(series['x'], series['y'], **kwarg)
            ax.annotate(location, series.iloc[-1, :], fontsize=8)

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
    worldwide_data.rename(columns={'total_cases': 'running total'},
                                   inplace=True)

    plot('by country', worldwide_data,
         'date', 'running total', 'linear', 'log', countries,
         kwarg={'linestyle': ':', 'linewidth': 0.5})

    plot('by country', worldwide_data,
         'running total', 'new_cases', 'log', 'log', countries,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by country', worldwide_data,
         'new_tests', 'new_cases', 'log', 'log', countries,
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
        df = us_data[us_data['state'] == state].sort_values(by=['date'])
        df['new_cases'] = df['cases'].diff()
        data_by_state.append(df)

    us_data = pd.concat(data_by_state) \
                .sort_values(by=['date', 'state']) \
                .reset_index() \
                .rename(columns={'cases': 'running total',
                                 'state': 'location'})

    plot('by US state', us_data,
         'running total', 'new_cases', 'log', 'log', states,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by US state', us_data,
         'date', 'new_cases', 'linear', 'linear', states,
         kwarg={'linestyle': ':', 'linewidth': 1})

    plot('by US state', us_data,
         'running total', 'deaths', 'log', 'log', states,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})
