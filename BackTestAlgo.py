import types
import statsmodels.api as sm

from numpy import nan as NA

from AlphaBeta import *
from Calculator import *
from DataQuery import *


class BackTester:
    def __init__(self, initialize, tradingAlgo):
        print('\nHello backtesting')

        self.context = types.SimpleNamespace()
        # context 네임스페이스 객체 생성

        self.context.capital_base = 0
        # 투자원금의 기본값을 설정함 (initialize 밑에서 설정하면, initialize에서 투자원금에 특정값을 부여해도 기본값을 다시 부여해버림)

        self.context.market_benchmark = {}
        # initialize()에서 지정하면 win_rate 계산 시에 비교, 지정 안하면 절대수익(0%와 비교)으로 계산

        initialize(self.context)
        # initialize 함수로 context에 symbols와 price 상태 저장(symbols와 price에 해당하는 이름을 반드시 정의해줘야 함)
        # 그 밖에 사용하고자 하는 사용자 정의 key : value 지정할 수 있음 ( ex : context.hold = True )

        self.context.current_time = pd.NA
        # context에 current_time 정보 저장하기

        accounts_col = ['date', 'deposit', 'symbol', 'unitPrice', 'amounts', 'withdrawal', 'balance']
        accounts_df = pd.DataFrame(columns=accounts_col)
        self.context.accounts_df = accounts_df
        # context에 accounts_df 저장하기(컬럼만 있는 빈 dataframe)

        s = pd.Series([self.context.current_time, 0, pd.NA, 0, 0, 0, self.context.capital_base], index=self.context.accounts_df.columns)
        self.context.accounts_df = self.context.accounts_df.append(s, ignore_index=True)
        # balance의 초기값을 capital_base로 설정(나머지 컬럼들의 초기값은 형식적인 값들로 설정)
        # 단위 시간별로 accounts_df에 새로운 행들이 추가되는 형식으로 운영함(하나의 단위시간에 여러 order가 있을 경우 각각 추가함)


        portfolio_col = ['cash_values', 'stock_values', 'portfolio_values']
        portfolio_df = pd.DataFrame(columns=portfolio_col)
        # portfolio_df를 만듬
        portfolio_df = portfolio_df.append(pd.Series([self.context.capital_base, 0, 0], index=portfolio_col), ignore_index=True)
        self.context.portfolio_df = portfolio_df
        # cash 컬럼의 초기값을 capital_base으로 설정하고, 나머지 컬럼은 0으로 초기값 설정 후 context에 저장
        # 업데이트 될때마다 기존 portfolio_df를 새로운 portfolio_df로 덮어씌우는 형식으로 운영됨

        benchmark = {'benchmark_symbols' : 0, 'benchmark_df' : 0, 'benchmark_class' : 0}
        self.context.benchmark = benchmark

        self.context.record = {}
        self.context.record_on = False
        # context에 record 상태 공간 만들기, 녹화 스위치(record_on)는 껴놓은 상태로 저장

        self.tradingAlgo = tradingAlgo

    def run(self, data, benchmark_data=None, free_risk_data=None):
        # data는 'data', 'symbol', 'price_factor' 형태로 줘야함
        # benchmark_data 디폴트값은 none이며, data를 넣어줄때는 columns = [date, benchmark, price] 또는 [date, benchmark, return] 형식으로 줘야함
        # free_risk_data는 데이터프레임 형태로 넣어줄수 있음 (return 값으로 넣어야함, price아님)

        data['price'] = data[self.context.price]
        # data에 price 정보에 해당하는 열을 지정해줌

        if isinstance(benchmark_data, pd.DataFrame):
        # benchmark_data가 입력되었는지 확인함
            benchmark = AlphaBeta(self.context, benchmark_data)
            # benchmark_data가 있으면 AlphaBeta 클래스 생성
            self.context.benchmark['benchmark_class'] = benchmark
            # 클래스 객체를 context에 저장(main 등에서 클래스 객처를 별도로 만들지 않고 데이터 조회등에 활용할 수 있음)
            benchmark_symbols = self.context.benchmark['benchmark_symbols']
            # AlphaBeta 클래스 생성 시 init에서 benchmark_data에 있는 benchmakrk symbol를 정리하여 context에 저장해 놓은 것을 꺼내어 씀
            beta_list = ['beta_{0}'.format(i) for i in benchmark_data['benchmark'].unique().tolist()]
            # benchmark 데이터의 symbol 개수 만큼 beta 변수를 만들고 list 형태로 지정함
        else :
            beta_list = ['beta']
            # benchmakrk data가 없으면 beta 변수를 하나만 만듬

        resultColumns = ['date', 'capital_base', 'starting_cash', 'ending_cash',
                         'starting_stock_value', 'ending_stock_value', 'starting_portfolio_value', 'ending_portfolio_value']
        # result의 컬럼을 미리 만듬
        self.result = pd.DataFrame(columns=resultColumns)
        # result 공간 dataframe 만들기 (열만 정의된 빈 dataframe)

        date_univers = data.drop_duplicates(['date'])['date']
        # date_univers 정의 (데이터에 있는 일자를 중복제거 해서 event를 일으킬 일자 정의)

        date_univers = date_univers.reset_index(drop=True)

        self.context.date_univers = date_univers
        # date_univers를 context에 저장함(DataQuery와 AlphaBeta에서 history 함수 호출할때 사용)

        ending_portfolio_value = self.context.portfolio_df.iat[-1,0]
        # 기초평가액은 전날의 기말평가액임(첫날 이전의 기말평가액은 존재 하지 않으므로 초기 셋팅을 첫날 기초현금가로 셋팅해야함)


        for i in range(0, len(date_univers)):
            current_time = date_univers.iloc[i]
            # 현재 일자 정의

            self.context.current_time = current_time
            # context에 현재시간 저장

            dataquery = DataQuery(data, self.context)
            # DataQuery의 class 객체 생성(run 함수에 넣은 data 인자와 현재 시간을 인수로 넣어줌)

            starting_cash=self.context.portfolio_df.iat[-1, 0]
            starting_portfolio_value = ending_portfolio_value
            starting_stock_value = starting_portfolio_value - starting_cash
            # tradingAlgo를 실행 하기 전에 '기초 현금, 기초 평가액, 기초 주식 가치'를 기록해놓음
            starting_capital_base = self.context.capital_base
            # tradingAlgo 전후의 deposit을 비교하기 위해 기록해둠

            self.tradingAlgo(self.context, dataquery)
            # tradingAlgo 실행 (tradingAlgo에 context 정보와 데이터를 조회할 수 있는 dataquery 객체를 인자로 넣어줌)
            ending_capital_base = self.context.capital_base
            if starting_capital_base != ending_capital_base :
                starting_cash += ending_capital_base - starting_capital_base
                starting_portfolio_value += ending_capital_base - starting_capital_base
            # tradingAlgo 안에서 deposit()이 호출될 경우, starting_cash가 늘어나야하고, 그로인해 starting_portfolio_value도 늘어야함
            # deposit이 증가하면 투자원금이 증가하는데, starting 금액에 편입안되면 그 금액만큼 수익으로 인식되어 수익률이 과대평가됨
            # tradingAlgo 안에서 deposit()이 호출된 사실을 인식하려면, starting_capital_base과 ending_capital_base를 비교해야함
            # (self.context.portfolio_df['cash']는 tradingAlgo에 order()가 호출될경우 인출이 발생하기 때문에 이미 왜곡되어 활용할수 없음)

            ending_portfolio_df = calculate_portfolio_value(self.context, dataquery)
            # tradingAlgo가 종료되면 portfolio_value를 업데이트하고 그 결과가 반영된 portfolio_df를 객체화함
            ending_cash = ending_portfolio_df.iat[-1,0]
            # portfolio_df의 첫번째 컬럼('cash') 값을 가져옴
            ending_portfolio_value = ending_portfolio_df.iat[-1,2]
            # portfolio_df의 세번째 컬럼('portfolio_values') 값을 가져옴
            ending_stock_value = ending_portfolio_value - ending_cash
            # stock_value는 portfolio_values에서 cash를 뺀 값

            capital_base = self.context.capital_base
            # 투자원금은 deposit()이 생길때마다 누적하여 계산되어 있음


            s = pd.Series([current_time, capital_base, starting_cash, ending_cash,
                           starting_stock_value, ending_stock_value, starting_portfolio_value, ending_portfolio_value], index=resultColumns)

            self.result = self.result.append(s, ignore_index=True)
            # result 데이터프레임 공간에 결과값 저장

        starting_portfolio_value_temp = self.result['starting_portfolio_value'].apply(lambda x: 1e-50 if x == 0 else x)
        # 나누기 사전 작업(0 값을 1e-50으로 대체)
        self.result = self.result.assign(
            portfolio_return=self.result['ending_portfolio_value'] / starting_portfolio_value_temp - 1)
        # 단위 시간별 portfolio_return 백터 연산
        self.result = self.result.assign(
            annualized_return=self.result['portfolio_return'].add(1).cumprod() ** (252 / (self.result.index.values + 1)) - 1)
        # annualized_return 계산
        self.result = self.result.assign(
            roll_annualized_return=(self.result['portfolio_return'] + 1).rolling(window=252).apply(np.prod, raw=True) - 1)
        # roll_annualized_return 계산
        self.result = self.result.assign(volatility=self.result['portfolio_return'].rolling(window=len(self.result), min_periods=1).apply(
            lambda roll: np.std(roll) * (252 ** (1 / 2)), raw=True))
        # 연율화된 volatility 계산
        self.result = self.result.assign(roll_volatility=self.result['portfolio_return'].rolling(window=252).apply(
            lambda roll: np.std(roll) * (252 ** (1 / 2)), raw=True))
        # 연율화된 roll_volatility 계산
        volatility = self.result['volatility'].apply(lambda x: 1e-50 if x == 0 else x)
        # 나누기 사전 작업(0 값을 1e-50으로 대체)
        self.result = self.result.assign(sharp_ratio=self.result['annualized_return'] / volatility)
        # sharp_ratio 계산
        roll_volatility = self.result['roll_volatility'].apply(lambda x: 1e-50 if x == 0 else x)
        # 나누기 사전 작업(0 값을 1e-50으로 대체)
        self.result = self.result.assign(roll_sharp_ratio=self.result['roll_annualized_return'] / roll_volatility)
        # sharp_ratio 계산
        self.result = self.result.assign(cumulative_return=self.result['portfolio_return'].add(1).cumprod() - 1)
        # cumulative_return 계산
        self.result = self.result.assign(
            total_profit=self.result['ending_portfolio_value'] - self.result['capital_base'])
        # total_profit 백터 연산
        cumula_return = self.result['portfolio_return'].add(1).cumprod()
        # 정규 누적 수익률(누적수익률에서 1을 제거하지 않은 상태) 계산
        cummax_return = self.result['portfolio_return'].add(1).cumprod().cummax().apply(lambda x: 1e-50 if x == 0 else x)
        # 해당 시점까지의 최대 정규 누적 수익률 값을 저장하고, 나누기 사전 작업으로 0을 1e-50으로 대체
        self.result = self.result.assign(drawdown_ratio=(cumula_return - cummax_return) / cummax_return)
        # drawdown_ratio 계산
        self.result = self.result.assign(MDD=self.result['drawdown_ratio'].cummin())
        # MDD 계산
        s = self.result['portfolio_return'].add(1).cumprod().rolling(len(self.result), min_periods=1).apply(
            lambda x: x.idxmax()).astype('int')
        # 해당 시점까지의 최대 정규 누적 수익률값의 index로 구성된 series를 저장함
        self.result = self.result.assign(underwater_period=(self.result['date'] - s.apply(lambda x: self.result['date'][x])).cummax())
        delta = self.result['portfolio_return']
        # underwater_period를 계산함 (현재 date에서 해당 시점까지의 최대 정규 누적 수익률값의 index에 해당하는 date를 뺀 값)
        self.result = self.result.assign(absolute_win_rate=delta.fillna(0).rolling(len(self.result), min_periods=1).apply(
            lambda x: len(x[x > 0]) / len(x)))
        # absolute_win_rate 계산(수익률이 0보다 크면 승리로 간주)
        self.result = self.result.assign(
            roll_absolute_win_rate=delta.fillna(0).rolling(252).apply(lambda x: len(x[x > 0]) / len(x)))
        # roll_absolute_win_rate 계산


        if isinstance(benchmark_data, pd.DataFrame):
            # benchmark_data가 입력되어 있다면,

            delta = self.result['portfolio_return'] - self.context.benchmark['benchmark_data']['return']
            # 수익률 비교를 위해 portfolio_return에서 bench_return을 뺌
            self.result = self.result.assign(relative_win_rate=delta.fillna(0).rolling(len(self.result), min_periods=1).apply(
                lambda x: len(x[x > 0]) / len(x)))
            # relative_win_rate 계산(delta가 0보다 크면(portfolio_return이 bench_return 보다 크면) 승리로 간주)
            self.result = self.result.assign(
                roll_relative_win_rate=delta.fillna(0).rolling(252).apply(lambda x: len(x[x > 0]) / len(x)))
            # roll_relative_win_rate 계산

            ad_bench_return = self.context.benchmark['benchmark_data']['return'].iloc[1:]
            # bench_return의 첫번째 값은 항상 na값이기 때문에 두번째 값부터 새로운 series를 구성함
            ad_portfolio = self.result.portfolio_return.iloc[1:]
            # ad_bench_return와 쌍을 맞추기 위해 두번째 값부터 새로운 series를 구성함

            self.result = self.result.assign(alpha=ad_portfolio.rolling(len(ad_portfolio), min_periods=2).apply(
                lambda x: sm.OLS(x, sm.add_constant(ad_bench_return.iloc[:x.index[-1]])).fit().params[0]))
            # alpha 값을 계산
            self.result = self.result.assign(beta=ad_portfolio.rolling(len(ad_portfolio), min_periods=2).apply(
                lambda x: sm.OLS(x, sm.add_constant(ad_bench_return.iloc[:x.index[-1]])).fit().params[1]))
            # beta 값을 계산
            self.result = self.result.assign(roll_alpha=ad_portfolio.rolling(252).apply(
                lambda x: sm.OLS(x, sm.add_constant(ad_bench_return.loc[x.index[0]:x.index[-1]])).fit().params[0]))
            # roll_alpha 값을 계산
            self.result = self.result.assign(roll_beta=ad_portfolio.rolling(252).apply(
                lambda x: sm.OLS(x, sm.add_constant(ad_bench_return.loc[x.index[0]:x.index[-1]])).fit().params[1]))
            # roll_beta 값을 계산

        if bool(self.context.record):
        # record된 것이 있다면
            self.result = pd.merge(self.result, self.context.record_df, how='outer', left_on='date', right_on='date')
            # date 칼럼을 기준으로 result 데이터프레임과 record 데이터프레임 병합(없는 값은 nan 처리)

        return self.result