import pandas as pd
import numpy as np
import scipy as sp
import scipy.interpolate
import matplotlib.pyplot as plt
import seaborn as sbn
from os import listdir
from os.path import isfile, join

PATH_DAILY_REPORTS = 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'

def log_interp1d(xx, yy, kind='linear'):
    logx = np.log10(xx)
    logy = np.log10(yy)
    # lin_interp = sp.interpolate.interp1d(logx, logy, kind=kind, bounds_error=False, fill_value="extrapolate")
    # log_interp = lambda zz: np.power(10.0, lin_interp(np.log10(zz)))
    lin_interp = sp.interpolate.interp1d(xx, logy, kind=kind, bounds_error=False, fill_value="extrapolate")
    log_interp = lambda zz: np.power(10.0, lin_interp(zz))
    return log_interp

def log_extrapol(xx, yy):
    logy = np.log10(yy)
    m, t = np.polyfit(xx, logy, 1)
    # print(10**m)
    log_interp = lambda zz: np.power(10, m*zz + t)
    return log_interp

def moving_average(data, window_size):
    n = len(data)
    avg = np.zeros(n)
    div = np.arange(n)
    div[0] = 1
    div[window_size:] = window_size
    for i in range(window_size):
        avg[window_size-1:] += data[i:n-window_size+i+1]
    avg /= div
    return avg

def get_report_list(path_name):
    files = [f for f in listdir(path_name) if isfile(join(path_name, f))]
    reports = []
    dates = []
    for f in files:
        if f[-4:] == '.csv':
            reports.append(f)
    return reports

def get_date_list(report_list):
    dates = []
    for i, r in enumerate(report_list):
        date = r.split('.')[0]
        day = date[3:5]
        mon = date[0:2]
        yea = date[6:10]
        dates.append('{}-{}-{}'.format(yea, mon, day))
    return dates

def get_data(path_name, no_provinces=True):
    # Get a file list of daily reports
    report_names = get_report_list(path_name)
    dates = get_date_list(report_names)

    # Create merged dataframe
    data = []
    for d, rn in zip(dates, report_names):
        # print(d)
        # Read report
        report = pd.read_csv(path_name+rn, delimiter=',')

        # United Kingdom is UK
        report.loc[report['Country/Region'] == 'United Kingdom', 'Country/Region'] = 'UK'

        # Mainland China is China
        report.loc[report['Country/Region'] == 'Mainland China', 'Country/Region'] = 'China'

        # Korea, South is South Korea
        report.loc[report['Country/Region'] == 'Korea, South', 'Country/Region'] = 'South Korea'

        # Sum over all provinces that belong to a country/region
        for c in report['Country/Region'].unique():
            provinces = report[report['Country/Region']==c]['Province/State'].unique()
            if any(pd.isna(provinces)):
                # There is one entry for the whole country without a specific province
                pass
            else:
                # There is no entry for the entire country, we have to sum over all provinces
                report = report.append(pd.DataFrame(
                    {'Country/Region': c,
                     'Province/State': np.nan,
                     'Confirmed': report[report['Country/Region']==c]['Confirmed'].sum(),
                     'Deaths': report[report['Country/Region']==c]['Deaths'].sum(),
                     'Recovered': report[report['Country/Region']==c]['Recovered'].sum(),
                    }, index=[0]),
                    ignore_index=False)

        # Remove the provice data
        if no_provinces:
            report = report[pd.isna(report['Province/State'])]

        # Add date and append
        report['Date'] = [d for i in range(len(report))]
        data.append(report)

    # Concatenate to one dataframe
    data = pd.concat(data)
    data.Date = pd.to_datetime(data.Date)
    data = data.sort_values('Date')
    return data


def get_spread_rate_by_country(country, data):
    data_country = data[data['Country/Region'] == country]
    # Make sure, it's sorted
    data_country = data_country.sort_values('Date')
    confirmed = np.array(data_country.Confirmed)
    date = np.array(data_country.Date)
    infections = confirmed[1:] - confirmed[:-1]
    rate = infections/confirmed[:-1]
    date = date[:-1]
    ts = pd.DataFrame()
    ts['Rate'] = rate
    ts['Date'] = date
    ts['Date'] = pd.to_datetime(date)
    return ts

def get_new_infections_by_country(country, data):
    data_country = data[data['Country/Region'] == country]
    # Make sure, it's sorted
    data_country = data_country.sort_values('Date')
    confirmed = np.array(data_country.Confirmed)
    date = np.array(data_country.Date)
    infections = confirmed[1:] - confirmed[:-1]
    date = date[:-1]
    ts = pd.DataFrame()
    ts['New Infections'] = infections
    ts['Date'] = date
    ts['Date'] = pd.to_datetime(date)
    return ts

def get_confirmed_by_country(country, data):
    data_country = data[data['Country/Region'] == country]
    # Make sure, it's sorted
    data_country = data_country.sort_values('Date')
    confirmed = np.array(data_country.Confirmed)
    date = np.array(data_country.Date)
    # infections = confirmed[1:] - confirmed[:-1]
    # rate = infections/confirmed[:-1]
    # date = date[:-1]
    ts = pd.DataFrame()
    ts['Confirmed'] = confirmed
    ts['Date'] = date
    ts['Date'] = pd.to_datetime(date)
    return ts

def get_deaths_by_country(country, data):
    data_country = data[data['Country/Region'] == country]
    # Make sure, it's sorted
    data_country = data_country.sort_values('Date')
    deaths = np.array(data_country.Deaths)
    date = np.array(data_country.Date)
    # infections = confirmed[1:] - confirmed[:-1]
    # rate = infections/confirmed[:-1]
    # date = date[:-1]
    ts = pd.DataFrame()
    ts['Deaths'] = deaths
    ts['Date'] = date
    ts['Date'] = pd.to_datetime(date)
    return ts


def plot_spread_rate(data, country_list, avg=5, date_lim=None):
    fig = plt.figure()
    ax = fig.add_subplot()

    for c in country_list:
        ts = get_spread_rate_by_country(c, data)

        # Derive date limits if none are given
        if date_lim is None:
            date_lim = [np.min(ts.Date), np.max(ts.Date)]

        # Derive averaged time series
        rate = np.array(ts.Rate)*100
        rate_avg = moving_average(rate, avg)

        if len(country_list) == 1:
            pl, = ax.plot(ts.Date, rate_avg, color='black', alpha=.3)
        else:
            pl, = ax.plot(ts.Date, rate_avg, alpha=.3)
        ax.plot(ts.Date, rate, color=pl.get_color(), alpha=0.9, label=c)

    ax.tick_params(axis='x', rotation=60)
    ax.set_xlim(date_lim)
    ax.set_ylim([0, 100])
    if len(country_list) == 1:
        c = [x for x in country_list.keys()]
        fname = '{}_rate.png'.format(c[0].replace(' ', '_').lower())
    else:
        fname = '{}_rate.png'.format('countries')
    ax.set_ylabel('daily spread rate (and its {} days average) [%]'.format(avg))
    ax.legend()
    plt.savefig('png/'+fname, bbox_inches='tight')
    plt.close()

def plot_new_infected(data, country_list, avg=5, date_lim=None, scale='log', forecast=21, ext_base=7):
    fig = plt.figure()
    ax = fig.add_subplot()

    for c in country_list.keys():
        ts = get_new_infections_by_country(c, data)

        nr_inhabitants = country_list[c][0]
        icus_per_capita = country_list[c][1]

        # 6% of Covid-19 patients require ICU treatment for one week on average
        icu_rate = 0.06
        icu_time = 7  # days
        icu_limit = icus_per_capita/icu_rate/icu_time

        # Derive date limits if none are given
        if date_lim is None:
            date_lim = [np.min(ts.Date), np.max(ts.Date) + pd.Timedelta(forecast, unit='d')]

        infected = np.array(ts["New Infections"])/nr_inhabitants

        # Extrapolate based on the last 7 days
        _f = log_extrapol(np.arange(ext_base), infected[-ext_base:])
        f = lambda d: _f(d.days)
        # print(max(ts.Date) - pd.Timedelta(ext_base, unit='d'))
        ext_range = pd.date_range(max(ts.Date) - pd.Timedelta(ext_base, unit='d'),
                                  max(ts.Date) + pd.Timedelta(forecast, unit='d'))

        if len(country_list) == 1:
            pl, = ax.plot(ts.Date, infected, color='black', alpha=.9, label=c)
        else:
            pl, = ax.plot(ts.Date, infected, alpha=.9, label=c)
        ax.plot(ext_range,
                f(ext_range - max(ts.Date) + pd.Timedelta(ext_base-1, unit='d')),
                '-',
                color=pl.get_color(),
                alpha=.3)
        ax.plot(date_lim, 2*[icu_limit], '--', color=pl.get_color(), alpha=.9)

    ax.tick_params(axis='x', rotation=60)
    ax.set_xlim(date_lim)
    # ax.set_ylim([1e-8, 1e-1])
    ax.grid(True)
    if scale == 'log':
        ax.set_yscale('log')
    if len(country_list) == 1:
        ax.set_ylabel('new infections per capita ({})'.format(country_list[0]))
        fname = '{}_new_infections.png'.format(country_list[0].replace(' ', '_').lower())
    else:
        ax.set_ylabel('new infections per capita')
        fname = '{}_new_infections.png'.format('countries')
        ax.legend()
    plt.savefig('png/'+fname, bbox_inches='tight')
    plt.close()

def plot_confirmed(data, country_list, avg=5, date_lim=None, scale='log', forecast=21, ext_base=7):
    fig = plt.figure()
    ax = fig.add_subplot()

    for c in country_list.keys():
        ts = get_confirmed_by_country(c, data)

        nr_inhabitants = country_list[c][0]
        icus_per_capita = country_list[c][1]

        # 80% default occupation, 6% of Covid-19 patients require ICU treatment
        icu_rate = 0.06
        icu_limit = icus_per_capita/icu_rate

        # Derive date limits if none are given
        if date_lim is None:
            date_lim = [np.min(ts.Date), np.max(ts.Date) + pd.Timedelta(forecast, unit='d')]

        confirmed = np.array(ts.Confirmed)/nr_inhabitants

        # Extrapolate based on the last 7 days
        # _f = log_interp1d(np.arange(ext_base)[::ext_base-1], confirmed[-ext_base:][::ext_base-1])
        _f = log_extrapol(np.arange(ext_base), confirmed[-ext_base:])
        f = lambda d: _f(d.days)
        # print(max(ts.Date) - pd.Timedelta(ext_base, unit='d'))
        ext_range = pd.date_range(max(ts.Date) - pd.Timedelta(ext_base, unit='d'),
                                  max(ts.Date) + pd.Timedelta(forecast, unit='d'))

        if len(country_list) == 1:
            pl, = ax.plot(ts.Date, confirmed, color='black', alpha=.9, label=c)
        else:
            pl, = ax.plot(ts.Date, confirmed, alpha=.9, label=c)
        ax.plot(ext_range,
                f(ext_range - max(ts.Date) + pd.Timedelta(ext_base-1, unit='d')),
                '-',
                color=pl.get_color(),
                alpha=.3)
        ax.plot(date_lim, 2*[icu_limit], '--', color=pl.get_color(), alpha=.9)

    ax.tick_params(axis='x', rotation=60)
    ax.set_xlim(date_lim)
    ax.set_ylim([1e-8, 1e-1])
    ax.grid(True)
    if scale == 'log':
        ax.set_yscale('log')
    if len(country_list) == 1:
        ax.set_ylabel('confirmed cases per capita ({})'.format(country_list[0]))
        fname = '{}_confirmed.png'.format(country_list[0].replace(' ', '_').lower())
    else:
        ax.set_ylabel('confirmed cases per capita')
        fname = '{}_confirmed.png'.format('countries')
        ax.legend()
    plt.savefig('png/'+fname, bbox_inches='tight')
    plt.close()

def plot_estimated_from_delay(data, country_list, avg=5, date_lim=None, scale='log', forecast=21, ext_base=7):
    fig = plt.figure()
    ax = fig.add_subplot()

    for c in country_list.keys():
        ts = get_confirmed_by_country(c, data)

        nr_inhabitants = country_list[c][0]
        icus_per_capita = country_list[c][1]

        # 80% default occupation, 6% of Covid-19 patients require ICU treatment
        icu_rate = 0.06
        icu_limit = icus_per_capita/icu_rate

        # Derive date limits if none are given
        if date_lim is None:
            date_lim = [np.min(ts.Date), np.max(ts.Date)]

        # Derive averaged time series
        confirmed = np.array(ts.Confirmed)

        # 5 days incubation + 2 days test delay
        estimated = confirmed/nr_inhabitants*1.33**7

        # Extrapolate based on the last 7 days
        # _f = log_extrapol(np.arange(ext_base)[::ext_base-1], estimated[-ext_base:][::ext_base-1])
        _f = log_extrapol(np.arange(ext_base), estimated[-ext_base:])
        f = lambda d: _f(d.days)
        ext_range = pd.date_range(max(ts.Date) - pd.Timedelta(ext_base, unit='d'),
                                  max(ts.Date) + pd.Timedelta(forecast, unit='d'))

        if len(country_list) == 1:
            pl, = ax.plot(ts.Date, estimated, color='black', alpha=.9, label=c)
        else:
            pl, = ax.plot(ts.Date, estimated, alpha=.9, label=c)
        ax.plot(ext_range,
                f(ext_range - max(ts.Date) + pd.Timedelta(ext_base-1, unit='d')),
                '-',
                color=pl.get_color(),
                alpha=.3)
        ax.plot(date_lim, 2*[icu_limit], '--', color=pl.get_color(), alpha=.9)

    ax.tick_params(axis='x', rotation=60)
    ax.set_xlim(date_lim)
    ax.set_ylim([1e-7, 1e-1])
    ax.grid(True)
    if scale == 'log':
        ax.set_yscale('log')
    if len(country_list) == 1:
        ax.set_ylabel('estimated cases per capita based on delay ({})'.format(country_list[0]))
        fname = '{}_estimated_delay.png'.format(country_list[0].replace(' ', '_').lower())
    else:
        ax.set_ylabel('estimated cases per capita based on delay')
        fname = '{}_estimated_delay.png'.format('countries')
        ax.legend()
    plt.savefig('png/'+fname, bbox_inches='tight')
    plt.close()

def plot_estimated_from_deaths(data, country_list, avg=5, date_lim=None, scale='log', forecast=21, ext_base=7):
    fig = plt.figure()
    ax = fig.add_subplot()

    for c in country_list.keys():
        ts = get_deaths_by_country(c, data)

        nr_inhabitants = country_list[c][0]
        icus_per_capita = country_list[c][1]

        # 80% default occupation, 6% of Covid-19 patients require ICU treatment
        icu_rate = 0.06
        icu_limit = icus_per_capita/icu_rate

        # Derive date limits if none are given
        if date_lim is None:
            date_lim = [np.min(ts.Date), np.max(ts.Date)]

        # Derive averaged time series
        deaths = np.array(ts.Deaths)

        # 5 days incubation + 2 days test delay
        death_rate = 0.002
        estimated = deaths/death_rate/nr_inhabitants

        # Extrapolate based on the last 7 days
        # _f = log_extrapol(np.arange(ext_base)[::ext_base-1], estimated[-ext_base:][::ext_base-1])
        _f = log_extrapol(np.arange(ext_base), estimated[-ext_base:])
        f = lambda d: _f(d.days)
        ext_range = pd.date_range(max(ts.Date) - pd.Timedelta(ext_base, unit='d'),
                                  max(ts.Date) + pd.Timedelta(forecast, unit='d'))

        if len(country_list) == 1:
            pl, = ax.plot(ts.Date, estimated, color='black', alpha=.9, label=c)
        else:
            pl, = ax.plot(ts.Date, estimated, alpha=.9, label=c)
        ax.plot(ext_range,
                f(ext_range - max(ts.Date) + pd.Timedelta(ext_base-1, unit='d')),
                '-',
                color=pl.get_color(),
                alpha=.3)
        ax.plot(date_lim, 2*[icu_limit], '--', color=pl.get_color(), alpha=.9)

    ax.tick_params(axis='x', rotation=60)
    ax.set_xlim(date_lim)
    ax.set_ylim([1e-6, 1e-1])
    ax.grid(True)
    if scale == 'log':
        ax.set_yscale('log')
    if len(country_list) == 1:
        ax.set_ylabel('estimated cases per capita based on {}% death rate ({})'.format(100*death_rate, country_list[0]))
        fname = '{}_estimated_deaths.png'.format(country_list[0].replace(' ', '_').lower())
    else:
        ax.set_ylabel('estimated cases per capita based on {}% death rate'.format(100*death_rate))
        fname = '{}_estimated_deaths.png'.format('countries')
        ax.legend()
    plt.savefig('png/'+fname, bbox_inches='tight')
    plt.close()

def plot_deaths(data, country_list, avg=5, date_lim=None, scale='log'):
    fig = plt.figure()
    ax = fig.add_subplot()

    for c in country_list.keys():
        ts = get_deaths_by_country(c, data)

        nr_inhabitants = country_list[c][0]

        # Derive date limits if none are given
        if date_lim is None:
            date_lim = [np.min(ts.Date), np.max(ts.Date)]

        # Derive averaged time series
        deaths = np.array(ts.Deaths)

        if len(country_list) == 1:
            pl, = ax.plot(ts.Date, deaths/nr_inhabitants, color='black', alpha=.9, label=c)
        else:
            pl, = ax.plot(ts.Date, deaths/nr_inhabitants, alpha=.9, label=c)

    ax.tick_params(axis='x', rotation=60)
    ax.set_xlim(date_lim)
    ax.set_ylim([1e-9, 1e-1])
    if scale == 'log':
        ax.set_yscale('log')
    if len(country_list) == 1:
        ax.set_ylabel('deaths per capita ({})'.format(country_list[0]))
        fname = '{}_deaths.png'.format(country_list[0].replace(' ', '_').lower())
    else:
        ax.set_ylabel('deaths per capita')
        fname = '{}_deaths.png'.format('countries')
        ax.legend()
    plt.savefig('png/'+fname, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    # sbn.set_palette("Set1", 8, .75)
    # Load or generate data set
    try:
        data = pd.read_csv('data.csv')
    except FileNotFoundError:
        data = get_data(PATH_DAILY_REPORTS)
        data.to_csv('data.csv')
    print("Last data is from {}".format(np.max(data['Date'])))
    extrapolation_base = 6
    forecast = 21
    date_lim = pd.to_datetime([pd.Timestamp('2020-02-15'), pd.Timestamp(np.max(np.array(data.Date))) + pd.Timedelta(forecast, unit='d')])

    # https://link.springer.com/article/10.1007/s00134-012-2627-8
    # https://link.springer.com/article/10.1007/s00134-015-4165-7
    # https://en.wikipedia.org/wiki/List_of_countries_by_hospital_beds#Numbers
    country_list = {'Germany': [82.79e6, 29.2/100000],
                    'US': [327.2e6, 34.2/100000],
                    'Italy': [60.48e6, 12.5/100000],
                    'France': [66.99e6, 11.6/100000],
                    'Spain': [46.66e6, 9.7/100000],
                    'UK': [66.44e6, 6.6/100000],
                    'Switzerland': [8.57e6, 11.0/100000],
                    'Austria': [8.822e6, 21.8/100000],
                    # 'Sweden': [10.12e6, 5.8/100000],
                    # 'Denmark': [5.603e6, 6.7/100000],
                    # 'Norway': [5.368e6, 8.0/100000],
                    'South Korea': [51.47e6, 10.6/100000],
                    'Japan': [126.8e6, 4.5/100000]
                    # 'China': [1386e6, 3.6/100000],
                    }

    # Derive the COVID ICU capacities assuming a minimum of 3.5 ICUs per 100000
    # for regular hospital cases and all other ICUs available for corona
    # patients. This is an arbitrary number that seems somehow reasonable to me
    # given that some contries can maintain a good-ish health system with only
    # 4.5 ICUs per 100000 (e.g. Japan, Portugal)
    for c in country_list.keys():
        country_list[c][1] -= 3.5/100000

    sbn.set_style("whitegrid")
    sbn.set_palette(sbn.color_palette(palette="colorblind", n_colors=len(country_list), desat=1))

    # Cases
    plot_new_infected(data, country_list, avg=5, date_lim=date_lim, forecast=forecast, ext_base=extrapolation_base)
    plot_confirmed(data, country_list, avg=5, date_lim=date_lim, forecast=forecast, ext_base=extrapolation_base)
    plot_estimated_from_deaths(data, country_list, avg=5, date_lim=date_lim, forecast=forecast, ext_base=extrapolation_base)
    # plot_estimated_from_delay(data, country_list, avg=5, date_lim=date_lim, forecast=forecast, ext_base=extrapolation_base)
    # plot_deaths(data, country_list, avg=5, date_lim=date_lim)

    # Rates
    date_lim = pd.to_datetime([pd.Timestamp('2020-02-15'), pd.Timestamp(np.max(np.array(data.Date)))])
    country_list_rates = { c: country_list[c] for c in ['Germany',
                                                        'US',
                                                        'South Korea',
                                                        'Italy',
                                                        ]}
    plot_spread_rate(data, country_list_rates, avg=3, date_lim=date_lim)
