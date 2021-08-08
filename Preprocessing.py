import pandas as pd
import numpy as np
import datetime
import types

def checking_data_contidion(initialize, data, benchmark_data=None) :
    context = types.SimpleNamespace()
    initialize(context)

    print('\n<Cheking Data Columns>')
    necesserly_columns = ['date', 'symbol']
    print(' - necesserly columns : {0}'.format(necesserly_columns))


    data_columns = data.columns.values.tolist()
    print(' - data columns : {0}'.format(data_columns))

    not_in_necesserly_columns = []
    for symbol in necesserly_columns:
        if not symbol in data_columns:
            not_in_necesserly_columns.append(symbol)
    if not not_in_necesserly_columns :
        not_in_necesserly_columns = 'Nothing'
    print(' - data symbols not in context symbols : {0}'.format(not_in_necesserly_columns))

    if not not_in_necesserly_columns == 'Nothing' :
        print('Please check the data columns. if you fix it, this process will go further')
    else :
        print('\n<Cheking Symbols>')
        print(' - length of context symbols : {0}'.format(len(context.symbols)))
        print(' - context symbols : {0}'.format(context.symbols))

        data_symbols = data['symbol'].unique().tolist()
        print(' - length of data symbols : {0}'.format(len(data_symbols)))
        print(' - data symbols : {0}'.format(data_symbols))

        not_in_data_symbols = []
        for symbol in context.symbols :
            if not symbol in data_symbols :
                not_in_data_symbols.append(symbol)
        if not not_in_data_symbols :
            not_in_data_symbols = 'Nothing'
        print(' - context symbols not in data symbols : {0}'.format(not_in_data_symbols))

        not_in_context_symbols = []
        for symbol in data_symbols:
            if not symbol in context.symbols:
                not_in_context_symbols.append(symbol)
        if not not_in_context_symbols :
            not_in_context_symbols = 'Nothing'
        print(' - data symbols not in context symbols : {0}'.format(not_in_context_symbols))

        print('\n<Cheking Data imformation>')
        print(' - Please be sure "date" column should be the type of datetime')
        print(' - {0}'.format(data.info()))

        if isinstance(benchmark_data, pd.DataFrame):
            print('\n<Checking date_univers>')
            date_univers = data.drop_duplicates(['date'])['date'].tolist()
            benchmark_data_univers = benchmark_data.drop_duplicates(['date'])['date'].tolist()

            if date_univers==benchmark_data_univers :
                print(' - date univers of data equals the one of benchmark data : True')
            else :
                print(' - date univers of data equals the one of benchmark data : False')

    print('\n<Checking Price Symbol>')

    print(' - context price symbol : {0}'.format([context.price]))








