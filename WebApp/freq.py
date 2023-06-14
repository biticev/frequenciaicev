from flask import Blueprint, request, jsonify
import requests
import datetime
from datetime import datetime as dt
import pandas as pd
import os
from sendfreq import run_script

dict_uid_translation = {
    '95a2a353':'b58a5a58',
    'b58a5a58':'b58a5a58',
}

freq = Blueprint('freq', __name__)

API_ROUTE = "http://45.56.120.227/api/v1/json"

def get_students_json(api_route):
    headers = {'Accept': 'application/json'}
    request_json = requests.get(api_route, headers=headers)
    return request_json.json()

def get_today_info():
    today = dt.now().strftime("%A")
    time = dt.now().strftime("%H:%M")
    date = dt.now().strftime("%d/%m/%Y")
    return today, time, date

def validade_time(start, end, time, minutes=15):
    # start - 30 min
    start = dt.strptime(start, "%H:%M")
    start = start - datetime.timedelta(minutes=minutes)
    start = start.strftime("%H:%M")
    # end + 30 min
    end = dt.strptime(end, "%H:%M")
    end = end + datetime.timedelta(minutes=minutes)
    end = end.strftime("%H:%M")

    print(start, end, time)

    if start <= time and end >= time:
        return True
    return False

PATH_DATA = './data/today.csv'
print("Carregando arquivo de registros de hoje...")
df_today = pd.read_csv(PATH_DATA, sep=';')
students = get_students_json(API_ROUTE)

@freq.route('/frequencia', methods=['GET'])
def get_data():
    global df_today
    global students
    rfid_hash = request.args.get('cardData')
    translated_hash = dict_uid_translation.get(rfid_hash)
    student = students.get(translated_hash)
    

    if student != None:
        key_mat = list(student.keys())[0]
        student_id_user = student[key_mat]['idUser']
        student_name = student[key_mat]['nome']
        student_name = student_name.split(' ')
        student_name = str(student_name[0] + ' ' + student_name[-1])
        today, time, date = get_today_info()
        for studant_class in student[key_mat]['horarios'].get(today):
            class_id = studant_class['idClass']
            subject_id = studant_class['idSubject']
            class_name = str(studant_class['subjectName'])
            start = studant_class['hourStart']
            end = studant_class['hourEnd']
            if validade_time(start, end, time):
                if df_today[(df_today['idUser'] == student_id_user) & (df_today['idClass'] == class_id)].empty:
                    status = 1
                    df_today = df_today._append({'date':date, 'weekday':today, 'idUser':student_id_user, 'idClass':class_id, 'idSubject':subject_id, 'start':start, 'end':end, 'startTime':time, 'status':status}, ignore_index=True)
                    break
                else:
                    df_today = df_today[(df_today['idUser'] == student_id_user) & (df_today['idClass'] == class_id)]
                    status = int(df_today['status'][0]) + 1
                    df_today['endTime'] = time
                    df_today['status'] = status
                    break
        class_name = class_name if class_name != None else 'disciplina nao identificada'
        if len(df_today) % 3 == 0:
            df_today.to_csv(PATH_DATA, sep=';', index=False)
        return jsonify([1, class_name, student_name, translated_hash, status])
    class_name = class_name if class_name != None else 'disciplina nao identificada'
    student_name = student_name if student_name != None else 'aluno nao identificado'
    return jsonify([0, class_name, student_name, translated_hash, 0])

@freq.route('/enviarfrequencia', methods=['GET'])
def sendfreq():
    run_script()