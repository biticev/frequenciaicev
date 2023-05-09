from flask import Blueprint, request, jsonify
import requests
from models import *
import json
from datetime import datetime

freq = Blueprint('freq', __name__)

API_ROUTE = "http://45.56.120.227/api/v1/json"

def get_students_json(api_route):
    headers = {'Accept': 'application/json'}
    request_json = requests.get(api_route, headers=headers)
    return request_json.json()

def get_today_info():
    today = datetime.now().strftime("%A")
    time = datetime.now().strftime("%H:%M")
    return today, time

DUMMY_HASH = '6235386135613538'
translated_hash = bytes.fromhex(DUMMY_HASH).decode('utf-8')
estudantes = get_students_json(API_ROUTE)
student = estudantes.get(translated_hash)
today, time = get_today_info()
key_may = list(student.keys())[0]
student_name = student[key_may]['nome']
student_id_person = student[key_may]['idPerson']
student_timetable = student[key_may]['horarios'].get(today)
print(student_timetable)


@freq.route('/frequencia', methods=['GET'])
def get_data():
    rfid_hash = request.args.get('cardData')
    rfid_hash = "C59"


    for aluno in lista_alunos:
        if (rfid_hash.upper() in aluno['rfid_hash']):
            aluno_nome = aluno['nome']
            aluno_curso = aluno['curso']
            aluno_matricula = aluno['matricula']
            
            for horario in lista_horarios:
                if (aluno_curso in horario['course']['name'][5:]):
                    resposta = aluno_curso

            return jsonify([1, aluno_nome, resposta, rfid_hash])
    else:
        resposta = "Rejeitado"
        return jsonify([0, rfid_hash, resposta])