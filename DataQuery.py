import pandas as pd
import datetime


class DataQuery :
    def __init__(self, data, context) :
        self.data = data
        self.current_time = context.current_time
        # 실제 데이터 프레임(data 인자), 현재시간을(current_time 인자) 클래스 인자로 정의
        # data는 열이 'symbol', 'price', 그리고 사용자가 정의한 fators(여러개일수 있음)로 구성됨


    def current_data(self, symbols, factors) :
        # symbols와 factors는 스칼라 문자 또는 리스트 형태로 넣어줄 수 있음

        querydata = self.data[self.data['date'] == self.current_time]
        # 현재시간에 해당하는 데이터만 필터

        if isinstance(symbols, list) :
            if isinstance(factors, list) :
            # symbols와 factors 모두 리스트 형태로 넣어준 것이라면
                columns = ['symbol']+factors
                # 조회하고자하는 데이터 컬럼 정의

            else :
            # symbols는 리스트, factors는 스칼라 문자형태로 넣어준 것이라면

                columns= ['symbol', factors]
                # 조회하고자하는 데이터 컬럼 정의

            querydata = querydata[querydata['symbol'].isin(symbols)][columns]
            # 해당 조건들에 해당하는 데이터프레임 반환

        else :
            if isinstance(factors, list) :
            # symbols는 스칼라 문자형태, factors는 리스트 형태로 넣어준 것이라면

                querydata = querydata[querydata['symbol'] == symbols][factors]
                # 해당 조건들에 해당하는 데이터프레임 반환

            else :
            # symbols와 factors 모두 스칼라 문자형태로 넣어준 것이라면
                querydata = querydata[querydata['symbol']==symbols][factors].values[0]
                # 해당 조건들에 해당하는 스칼라 값을 반환

        return querydata

    def history(self, context, symbols, factors, periods) :
        # symbols와 factors는 스칼라 문자 또는 리스트 형태로 넣어줄 수 있음

        date_univers = context.date_univers
        # context에 저장된 date_univers를 가지고옴
        current_time_index = date_univers[date_univers == context.current_time].index[0]
        # date_univers를 이용해서 현재 시간의 인덱스를 가지고옴
        start = current_time_index + 1 - periods
        # date_univers에서 조회를 시작하는 날짜의 인덱스는 마지막 날짜(current_time_index + 1)에서 조회기간(periods)를 뺀 값
        if start < 0 :
            start = 0
            # 사용자가 실수 등으로 너무 긴 조회기간을 설정해버려서 index가 0보다 작으면 0으로 설정(조회할 수 있는 가장 먼 시간을 반환)
        end = current_time_index + 1
        # 조회하는 마지막 날짜를 지정(+1을 하는 이유는 밑에 iloc에 넣었을 때 예를 들어 10을 넣으면 9까지 조회하기 때문)
        time_list = [date for date in date_univers.iloc[start:end]]
        # 조회하고자하는 날짜 리스트를 생성
        querydata = self.data[self.data['date'].isin(time_list)]
        # 조회시간들에 해당하는 데이터만 필터

        if isinstance(symbols, list) :
            if isinstance(factors, list) :
            # symbols와 factors 모두 리스트 형태로 넣어준 것이라면
                columns = ['symbol']+factors
                # 조회하고자하는 데이터 컬럼 정의

            else :
            # symbols는 리스트, factors는 스칼라 문자형태로 넣어준 것이라면

                columns= ['symbol', factors]
                # 조회하고자하는 데이터 컬럼 정의

            querydata = querydata[querydata['symbol'].isin(symbols)][columns]
            # 해당 조건들에 해당하는 데이터프레임 반환

        else :
            if isinstance(factors, list) :
            # symbols는 스칼라 문자형태, factors는 리스트 형태로 넣어준 것이라면

                querydata = querydata[querydata['symbol'] == symbols][factors]
                # 해당 조건들에 해당하는 데이터프레임 반환

            else :
            # symbols와 factors 모두 스칼라 문자형태로 넣어준 것이라면
                querydata = querydata[querydata['symbol']==symbols][factors]
                # 해당 조건들에 해당하는 시리즈를 반환 (조회되는 date가 여럿이기 때문에 스칼라가 아닌 시리즈 형태로 반환)

        return querydata