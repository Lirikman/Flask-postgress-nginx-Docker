import random
import requests
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/parsing.html')
def parsing():
    return render_template('parsing.html')


@app.route('/result.html', methods=['POST', 'GET'])
def sqlite():
    # Создание и работа с БД
    connection = sqlite3.connect('my_base.db')
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Cities (
                id INTEGER PRIMARY KEY NOT NULL,
                city TEXT);
            """)
    cities_info = [(1, 'Москва'), (2, 'Санкт-Петербург'), (3, 'Екатеринбург'), (4, 'Новосибирск'), (54, 'Красноярск')]
    cursor.executemany("INSERT OR IGNORE INTO Cities (id, city) VALUES(?, ?)", cities_info)
    cursor.execute("""CREATE TABLE IF NOT EXISTS Result (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            city TEXT,
            job TEXT,
            skills TEXT,
            salary INTEGER);
        """)
    connection.commit()
    connection.close()
    # Парсинг HH.RU
    area = request.form['city']
    vac_text = request.form['vac']
    url = 'https://api.hh.ru/vacancies'
    params = {'text': f'NAME:({vac_text})', 'area': area}
    result = requests.get(url, params=params).json()
    total_pages = result['pages']
    vac_json = []
    # Расчёт средней заработной платы
    for i in range(total_pages):
        url = 'https://api.hh.ru/vacancies'
        params = {'text': f'NAME:({vac_text})', 'area': area, 'page': i, 'per_page': 20}
        vac_json.append(requests.get(url, params=params).json())
    all_salary = 0
    all_vac = 0
    for i in vac_json:
        items = i['items']
        count_vac = 0
        summ_salary = 0
        for j in items:
            if j['salary'] is not None:
                s = j['salary']
                if s['from'] is not None:
                    count_vac += 1
                    summ_salary += s['from']
        all_salary += summ_salary
        all_vac += count_vac
    average_salary = all_salary // all_vac
    # Выбор 3 навыков
    all_skills = []
    for i in vac_json:
        items = i['items']
        for j in items:
            if j['snippet'] is not None:
                k = j['snippet']
                if k['requirement'] is not None:
                    all_skills.append(k['requirement'])
    list_temp = []
    for i in all_skills:
        text = i.find("Требования:")
        if text is not None:
            list_temp.append(i[i.find("Требования: ") + 1:])
    skills = []
    for i in list_temp:
        temp = str(i).split('.')
        for j in temp:
            if len(j) < 5:
                temp.remove(j)
        temp.pop()
        for k in temp:
            skills.append(k)
    for i in skills:
        text = str(i).split()
        if len(text) > 5:
            if text[0] == 'Опыт':
                skills.remove(i)
    random_skills = random.sample(skills, 3)
    skill_1 = random_skills[0]
    skill_2 = random_skills[1]
    skill_3 = random_skills[2]
    skill_str = '\n'.join(random_skills)
    # Добавление данных в БД
    con = sqlite3.connect('my_base.db')
    cur = con.cursor()
    cur.execute("INSERT INTO Result VALUES(?, ?, ?, ?, ?)", (1, area, vac_text, skill_str, average_salary))
    con.commit()
    con.close()
    return render_template('result.html', salary=average_salary, skill_1=skill_1, skill_2=skill_2, skill_3=skill_3)


@app.route('/sqlite.html')
def sql():
    return render_template('sqlite.html')


if __name__ == '__main__':
    app.run(debug=True)
