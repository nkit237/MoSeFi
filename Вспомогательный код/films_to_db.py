import json
import requests

import db_session
from db_session import Film, Genre

with open('../film.json', encoding='utf-8') as f:
    data = json.load(f)
    data = data['data']

for i in range(75, 10001):
    res = requests.get('https://kinobd.net/api/films', params={'page':i, 'with':'genres'})
    print(f'Запрос: {res.url}')
    data = res.json()['data']
    print(len(data))
    s_films = []
    db_sess = db_session.create_session()
    for f in data:
        film = Film()
        film.title = f['name_russian']
        film.about = f['description']

        try:
            genre = f['genres'][0]['name_ru']
        except IndexError:
            print(f'Фильм: {f['name_russian']} пропущен по причине того что нет жанра')
            continue
        g = db_sess.query(Genre).filter(Genre.title == genre).first()

        if g is None:
            ge = Genre()
            ge.title = genre
            db_sess.add(ge)
            db_sess.commit()
            print(f'Добавлен жанр: {genre}')
            genre = f['genres'][0]['name_ru']
            g = db_sess.query(Genre).filter(Genre.title == genre).first()

        film.id_genre = g.id

        film.link = f['trailer']
        film.grade = 0
        film.quantity = 0

        s_films.append(film)

    db_sess.add_all(s_films)
    db_sess.commit()
    print('Фильмы сохранены в БД')
