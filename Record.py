import pandas as pd

def record(context, **kwagrs):

    context.record = kwagrs

    if bool(context.record) and context.record_on == False:
        # context.record에 데이터가 저장되어 있고, 녹화가 아직 시작되지 않았다면
        reocrdColumns = ['date'] + [key for key in context.record.keys()]
        record = pd.DataFrame(columns=reocrdColumns)
        # record 공간 dataframe 만들기 (열만 정의된 빈 dataframe이며, record dict 키에 date열만 추가하여 열 정의)
        context.record_df = record
        # context에 record 공간 데이터프레임을 저장
        context.record_on = True
        # 녹화 스위치 켬

    # 녹화 스위치가 켜져 있으면
    record = context.record_df
    # context에 저장된 record 공간 데이터프레임을 가지고 옴
    reocrdColumns = record.columns
    s_data = [context.current_time] + [value for value in context.record.values()]
    # record dict 값들에 현재시간 추가하여 데이터 정의
    s = pd.Series(s_data, index=['date']+list(context.record.keys()))
    # s = pd.Series(s_data, index=reocrdColumns)
    record = record.append(s, ignore_index=True)
    # record 데이터프레임 공간에 데이터 저장

    context.record_df = record
    # context에 다시 저장

    return context