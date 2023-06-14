import pandas as pd
import numpy as np
import datetime 
from flask import jsonify
import os
import requests

PATH_CSV = './data/today.csv'
PATH_CSV_SENT = 'data/today_transformed.csv'
PATH_CSV_TO_RETRY = 'data/today_to_retry.csv'

def get_filtered_csv(path):
    df = pd.read_csv(path, sep=';')
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    df['weekday'] = df['weekday'].astype('category')
    df['idUser'] = df['idUser'].astype('int64')
    df['idClass'] = df['idClass'].astype('int64')
    df['idSubject'] = df['idSubject'].astype('int64')
    df['start'] = pd.to_datetime(df['start'], format='%H:%M')
    df['end'] = pd.to_datetime(df['end'], format='%H:%M')
    df['startTime'] = pd.to_datetime(df['startTime'], format='%H:%M')
    df['endTime'] = pd.to_datetime(df['endTime'], format='%H:%M')
    df['status'] = df['status'].astype('int64')
    return df

def calculate_interval_data(df, interval_gap=30):
    df['interval'] = df['end'] - df['start']
    df['interval'] = df['interval'].apply(lambda x: x-datetime.timedelta(minutes=interval_gap))
    df['intervalTime'] = df['endTime'] - df['startTime']
    df['fit'] = df.apply(lambda x: x['intervalTime'] >= x['interval'], axis=1)
    #df['interval'] = df['interval'].apply(lambda x: transform_timedelta_to_hours_and_minutes(x))
    #df['intervalTime'] = df['intervalTime'].apply(lambda x: transform_timedelta_to_hours_and_minutes(x))
    return df

def transform_time_to_especificTime(date,time):
    date = date.strftime('%Y-%m-%d')
    time = time.strftime('%H:%M')
    return str(date) + 'T' + str(time) + ':00.000Z'

def transform_timedelta_to_hours_and_minutes(timedelta):
    hours = timedelta.seconds//3600
    minutes = (timedelta.seconds//60)%60
    time = str(hours) + ':' + str(minutes)
    return time

def merge_with_to_retry(df):
    df_to_retry = pd.read_csv(PATH_CSV_TO_RETRY, sep=';')
    df = df._append(df_to_retry, ignore_index=True)
    df.reset_index(drop=True, inplace=True)
    return df

def post_student_into_gennera_api(df):
    for index in df.index: 
        if (df['registered'][index] != 1) & (df['fit'][index] == True):
            id_user = df['idUser'][index]
            id_subject = df['idSubject'][index]
            id_class = df['idClass'][index]
            start_date_utz = df['start'][index]
            url = f'http://45.56.120.227/api/v1/registra_frequencia/{id_user}/{id_subject}/{id_class}/{start_date_utz}'
            response = requests.get(url)
            if response.status_code == 200:
                df['registered'][index] = 1
            else:
                df['registered'][index] = 0
    return df

def save_transfomed_df(df):
    df_transformed = pd.read_csv(PATH_CSV_SENT, sep=';')
    df_transformed = df_transformed._append(df, ignore_index=True)
    df_transformed.reset_index(drop=True, inplace=True)
    df_transformed.to_csv(PATH_CSV_SENT, sep=';', index=False)

def save_to_retry_df(df):
    df_to_retry = df[df['registered'] == 0]
    df_to_retry.to_csv(PATH_CSV_TO_RETRY, sep=';', index=False)

def clean_df_today(df):
    df = df.copy()
    df = df.iloc[0:0]
    df.to_csv(PATH_CSV, sep=';', index=False)

def run_script():
    df = get_filtered_csv(PATH_CSV)
    df = calculate_interval_data(df)

    list_time_columns = ['start', 'end', 'startTime', 'endTime']

    for col in list_time_columns:
        df[col] = df.apply(lambda x: transform_time_to_especificTime(x['date'], x[col]), axis=1)

    df = merge_with_to_retry(df)
    df.sort_values(by=['date', 'idUser', 'start'], inplace=True)

    df_transformed = df.copy()
    df_transformed = post_student_into_gennera_api(df_transformed)
    save_transfomed_df(df_transformed)
    save_to_retry_df(df_transformed)
    clean_df_today(df)
    return jsonify({'message': 'Script executed successfully', 'status':200,"df":df_transformed.to_json()})

if __name__ == "__main__":
    run_script()