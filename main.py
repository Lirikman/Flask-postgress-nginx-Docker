import werkzeug.exceptions
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mysql.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return '<City %r>' % self.id


with app.app_context():
    try:
        moscow = City(id=1, city='Москва')
        piter = City(id=2, city='Санкт-Петербург')
        ekaterinburg = City(id=3, city='Екатеринбург')
        novosibirsk = City(id=4, city='Новосибирск')
        krasnoyarsk = City(id=54, city='Красноярск')
        db.session.add(moscow)
        db.session.add(piter)
        db.session.add(ekaterinburg)
        db.session.add(novosibirsk)
        db.session.add(krasnoyarsk)
        db.session.commit()
    except:
        pass


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(1024), nullable=False)
    vac = db.Column(db.String(1024), nullable=False)
    text = db.Column(db.Text, nullable=False)
    salary = db.Column(db.Integer)

    def __repr__(self):
        return '<Search %r>' % self.id


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/parsing.html')
def parsing():
    return render_template('parsing.html')


@app.route('/result.html', methods=['POST', 'GET'])
def result_hh():
    if request.method == "POST":
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
        skill_txt = str(skill_1) + '\n' + str(skill_2) + '\n' + str(skill_3)

        s = Search(city=area, vac=vac_text, text=skill_txt, salary=average_salary)

        try:
            db.session.add(s)
            db.session.commit()
            return render_template('result.html', salary=average_salary, skill_1=skill_1, skill_2=skill_2,
                                   skill_3=skill_3)
        except:
            db.session.rollback()
            return 'Ошибка добавления в БД'
    else:
        return render_template('parsing.html')


@app.route('/sqlite.html', methods=['POST', 'GET'])
def sql():
    if request.method == "POST":
        city_id = request.form['city']
        vac = request.form['vac']
        skill = request.form['skills']
        salary = request.form['salary']
        manual_search = Search(city=city_id, vac=vac, text=skill, salary=salary)
        try:
            db.session.add(manual_search)
            db.session.commit()
            return redirect('sqlite.html')
        except:
            db.session.rollback()
            return 'Ошибка добавления в БД. Попробуйте снова.'
    else:
        all_str = Search.query.all()
        return render_template('sqlite.html', all_str=all_str)


@app.route('/delete.html', methods=['POST', 'GET'])
def delete():
    if request.method == "POST":
        check_none = Search.query.all()
        if len(check_none) > 0:
            number = request.form['number']
            search_del = Search.query.get(number)
            try:
                db.session.delete(search_del)
                db.session.commit()
                return redirect('delete.html')
            except:
                db.session.rollback()
                return 'Ошибка удаления записи из БД. Попробуйте снова.'
        else:
            return redirect('delete.html')
    else:
        all_str = Search.query.all()
        all_id = [x.id for x in db.session.query(Search.id).distinct()]
        return render_template('delete.html', all_str=all_str, all_id=all_id)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
