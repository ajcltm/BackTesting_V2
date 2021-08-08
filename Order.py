import pandas as pd
from Calculator import *


def order(context, symbols, unitPrice, amounts) :
    if isinstance(symbols, str):
        # symbol이 하나만 있다면(하나의 종목에 대해서만 주문)
        temp_account_df = pd.DataFrame(
            data={'date': context.current_time, 'symbol': symbols, 'unitPrice': unitPrice, 'amounts': amounts},
            index=[0])
        # 컬럼에 배정된 값이 스칼라이면 df 생성시 index를 설정해주어야함
        # 임시로 account_df 생성
    else:
        temp_account_df = pd.DataFrame(
            data={'date': context.current_time, 'symbol': symbols, 'unitPrice': unitPrice, 'amounts': amounts})
        # symbol이 리스트이면(여러 종목에 대해 주문) df 생성 시 index 설정하지 않아도됨
        # 임시로 account_df 생성
    temp_account_df = temp_account_df.assign(withdrawal=temp_account_df.unitPrice * temp_account_df.amounts)
    # temp_account_df에 withdrawal을 계산하여 추가함

    temp_account_df = temp_account_df.assign(deposit=0)
    # deposit을 0으로 채움
    temp_account_df = temp_account_df.assign(balance=temp_account_df.apply(lambda x: context.accounts_df['balance'].iloc[-1] - x['withdrawal'] if x.name == 0 else -1*x['withdrawal'], axis=1))
    # temp_account_df의 첫번째 balance 값을 현재 context에 저장된 accounts_df의 마지막 balance값에서 첫번째 withdrawal 값을 뺀 값으로 하고
    # 나머지 줄의 balance 값을 임시로 withdrawal에 마이너스 부호(-)를 붙여서 할당함
    temp_account_df['balance'] = temp_account_df['balance'].cumsum()
    # cumsum()을 사용하여 나머지 줄의 balance 값을 계산
    context.accounts_df = context.accounts_df.append(temp_account_df).reset_index(drop=True)
    # temp_account_df를 context에 저장된 accounts_df에 추가하고 인덱스를 새로 정리
    return context.accounts_df

def deposit(context, dollars) :
    balance = context.accounts_df['balance'].iloc[-1] + dollars
    # 현재 context에 저장된 accounts_df의 마지막 balance값에 입급액(dollars)을 더해줌
    s = pd.Series([context.current_time, dollars, pd.NA, 0, 0, 0, balance], index=context.accounts_df.columns)
    context.accounts_df = context.accounts_df.append(s, ignore_index=True)
    # 업데이트 된 balance를 context.accounts_df에 추가함(나머지 컬럼은 의미없는 값을 넣어줌)

    context.capital_base += dollars

    return context.accounts_df
