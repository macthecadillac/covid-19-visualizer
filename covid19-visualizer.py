import urllib.request as request

import pandas as pd
import numpy as np

from matplotlib.pyplot import figure
from matplotlib import rcParams

rcParams['font.family'] = 'Carlito'


def plot(suffix, df, xheader, yheader, xscale, yscale, locations, kwarg={}):
    print('\r Plotting {} vs {}...'.format(yheader, xheader), end='')

    fig = figure(figsize=(13, 9))
    ax = fig.add_subplot(111, xscale=xscale, yscale=yscale)

    for location in locations:
        if xheader == 'date':
            ys = df.iloc[np.where(df.values == location)[0]][yheader].squeeze()
            nonzero_case_count = ys.nonzero()[0]
            if len(nonzero_case_count) == 0:
                continue

            ys = ys[ys.nonzero()[0][0]:].values.flatten()
            xs = np.arange(len(ys))
            series = pd.DataFrame(data=np.array([xs, ys]).T, columns=['x', 'y'])
            series.dropna(inplace=True)

            xs = series.values[6:, 0]
            if len(xs) == 0:
                ys = np.array([])
            else:
                ys = np.convolve(series.values[:, 1].flatten(),
                                 np.ones(7) / 7,
                                 mode='valid')
        else:
            series = df.iloc[np.where(df.values == location)[0]] \
                       .loc[:, [xheader, yheader]] \
                       .dropna()
            xs = series.values[6:, 0].flatten()
            if len(xs) == 0:
                ys = np.array([])
            else:
                ys = np.convolve(series.values[:, 1].flatten(),
                                 np.ones(7) / 7,
                                 mode='valid')

        if not len(xs) == 0:
            ax.plot(xs, ys, **kwarg)
            ax.annotate(location, (xs[-1], ys[-1]), fontsize=8)

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
    fpath = '/tmp/owid-covid-data.csv'
    return retrive_dataset(url, fpath)


def retrieve_nytimes_dataset():
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    fpath = '/tmp/us-state-by-statecovid-data.csv'
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
    worldwide_data.rename(columns={'total_cases': 'running total'}, inplace=True)
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
    us_state_data = retrieve_nytimes_dataset()
    # states = us_state_data['state'].unique().squeeze()

    states = ['California', 'Massachusetts', 'New York', 'Washington',
              'New Jersey', 'Oregon', 'Kansas', 'Texas', 'Georgia',
              'Florida', 'Arizona', 'Vermont', 'Hawaii', 'Montana',
              'Alaska', 'Idaho']

    data_by_state = []
    for state in states:
        df = us_state_data.loc[np.where(us_state_data.values == state)[0]] \
                .sort_values(by=['date'])
        padded = np.pad(df['cases'], (1, 0), 'constant', constant_values=(0,))
        df['new_cases'] = np.diff(padded)
        data_by_state.append(df)
    us_state_data = pd.concat(data_by_state).sort_values(by=['date', 'state'])
    us_state_data.rename(columns={'cases': 'running total'}, inplace=True)

    plot('by US state', us_state_data,
         'running total', 'new_cases', 'log', 'log', states,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})

    plot('by US state', us_state_data,
         'date', 'new_cases', 'linear', 'linear', states,
         kwarg={'linestyle': ':', 'linewidth': 1})

    plot('by US state', us_state_data,
         'running total', 'deaths', 'log', 'log', states,
         kwarg={'linewidth': 0, 'marker': 'o', 'markersize': 1})
