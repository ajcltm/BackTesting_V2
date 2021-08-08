import pandas as pd


def calculate_portfolio_value(context, dataquery, price='price') :

    data_temp = dataquery.data.loc[dataquery.data['date']==context.current_time]
    # 현재 시간에 해당하는 data만 조회

    cash_values = context.accounts_df['balance'].iloc[-1]
    # cash_values는 현재 balance 값임
    # if cash_values < 0 :
    #     cash_values = 0
        # balance 값이 0보다 작으면 cash_values는 0으로 함

    for_symbol = context.accounts_df['symbol'].dropna().unique().tolist()
    # 주문한 기록이 있는 symbol들을 불러옴(중복 제거됨)
    stock_values_df = data_temp.loc[data_temp['symbol'].isin(for_symbol)][['symbol', context.price]]
    # data에서 for_symbol에 해당하는 data만 조회한 후 symbol과 price 열만 가지고옴
    stock_values_df = stock_values_df.assign(amounts=stock_values_df['symbol'].apply(lambda x: context.accounts_df.loc[context.accounts_df['symbol'] == x]['amounts'].sum()))
    # 각 symbol의 amounts를 조회한 후 누적합을 계산함(현재 보유하고 있는 각 symbol의 amounts는 accounts_df에 있는 amounts의 누적합)
    stock_values_df = stock_values_df.assign(stock_values=stock_values_df[context.price] * stock_values_df['amounts'])
    # 각 symbol의 stock_values 백터 계산
    stock_values = stock_values_df['stock_values'].sum()
    # stock_values의 총합 계산

    s = pd.Series([cash_values, stock_values, cash_values + stock_values], index=context.portfolio_df.columns)
    context.portfolio_df = context.portfolio_df.append(s, ignore_index=True)
    # 계산된 cash_values, stock_value, portfolio_values를 portfolio_df에 할당한 후에 context.porfolio_df에 덮어씌움

    return context.portfolio_df