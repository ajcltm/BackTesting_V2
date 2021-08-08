import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import types
from yahoo_fin.stock_info import *
import pandas_datareader.data as pdr
import yfinance as yf
from BackTestAlgo import *
from Order import *
from DataQuery import *
from Record import *
from AlphaBeta import *
from Preprocessing import *

def my_init(context):
    data = pd.read_csv('C:/Users/ajcltm/PycharmProjects/BackTesting/data/stock_price_data_KOSPI.csv')
    tickers = data['symbol'].unique().tolist()
    context.symbols = tickers
    # universe를 symbols로 정의(반드시 지정해야함)

    context.price = 'Adj Close'
    # price로 사용할 칼럼 인덱스 이름을 알려줘야함(open, high, close 등의 인덱스를 price로 활용 가능함)
    # 여기서 지정한 인덱스는 포트폴리오를 평가할 때 기본적으로 사용하는 지표임

    context.capital_base = 50000000
    # 투자원금을 설정함. 지정하지 않으면 기본값을 사용함

    # context.market_benchmark = 'SP500'
    # 지정하면 win_rate 계산 시에 비교, 지정 안하면 절대수익(0%와 비교)으로 계산

    context.i = 0


def handle_data(context, data):
    context.i += 1
    print('\n')
    print(data.current_time)

    if context.i == 1:
        p1 = pd.read_csv('C:/Users/ajcltm/Desktop/p1.csv', index_col=0)
        tickers = p1.tickers.apply(lambda x: '{:06d}'.format(x))
        s = {'ticker': [], 'price': []}
        f = {'ticker': [], 'price': []}
        for ticker in tickers:
            try:
                price = data.current_data('{}.KS'.format(ticker), 'Adj Close')
                s['ticker'].append('{}.KS'.format(ticker))
                s['price'].append(price)
            except:
                f['ticker'].append(ticker)
                f['price'].append(0)
        quantity = list(map(lambda x: int((50000000 / len(s['price'])) / x), s['price']))
        print(len(quantity))
        order(context, s['ticker'], s['price'], quantity)

if __name__ == '__main__':

    data = pd.read_csv('C:/Users/ajcltm/PycharmProjects/BackTesting/data/stock_price_data_KOSPI_fixed.csv')
    data = data.reset_index(drop=True)
    data = data.sort_values(by='date')
    data['date'] = pd.to_datetime(data['date'])
    data = data.loc[data['date'] > datetime.datetime(2020, 5, 24)]

    yf.pdr_override()

    start_date = '25-05-2020'
    end_date = '18-07-2021'

    start = datetime.datetime.strptime(start_date, '%d-%m-%Y')
    end = datetime.datetime.strptime(end_date, '%d-%m-%Y')

    temp_data = pdr.get_data_yahoo('^KS11', data_source='yahoo', start=start, end=end)

    temp_data['date'] = temp_data.index
    temp_data = temp_data.reset_index(drop=True)
    temp_data = temp_data.rename(columns={'Adj Close': 'price'})
    temp_data['benchmark'] = 'kospi_200'
    benchmark = temp_data

    tester = BackTester(initialize=my_init, tradingAlgo=handle_data)

    result = tester.run(data, benchmark)

    pd.set_option('display.max.columns', 50)
    pd.set_option('display.max_rows', 1000)
    # print(result)

    result.to_csv('C:/Users/ajcltm/Desktop/backtesting/result.csv')