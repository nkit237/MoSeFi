import aiohttp
import asyncio
import logging
import random
import types

from bs4 import BeautifulSoup

from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from env import TG_TOKEN
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db_session
from db_session import User, Genre, Watch, Review, Film

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
dp = Dispatcher()
db_sess = db_session.create_session()

reply_keyboard = [[KeyboardButton(text='/help')],
                  [KeyboardButton(text='/genres'), KeyboardButton(text='/game')],
                  [KeyboardButton(text='/watchs'), KeyboardButton(text='/reviews')],
                  [KeyboardButton(text="/stop")]]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

genres = [[]]
for g in db_sess.query(Genre):
    if len(genres[-1]) < 2:
        genres[-1].append(InlineKeyboardButton(text=str(g.title), callback_data=str(g.title)))
    else:
        genres.append([InlineKeyboardButton(text=str(g.title), callback_data=str(g.title))])
gs = InlineKeyboardMarkup(inline_keyboard=[g for g in genres])

sp_g = set(x.title for x in db_sess.query(Genre))
sp_wg = set(x for x in ['Посмотрел(а) фильм', 'Получить случайный отзыв'])

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

dp = Dispatcher()
fr = Router()


async def main():
    bot = Bot(token=TG_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Help",
        callback_data="/help")
    )

    u_id = message.from_user.id
    user = db_sess.query(User).filter(User.id_user == u_id).first()
    if not user:
        user = User()
        user.id_user = u_id
        user.name = message.from_user.first_name
        db_sess.add(user)
        db_sess.commit()

        await message.reply(f'Здравствуйте, {message.from_user.first_name}! Это бот для поиска фильмов!',
                            reply_markup=kb)
        await message.answer(
            "Нажмите 'Help', чтоб узнать о возможностях бота!",
            reply_markup=builder.as_markup()
        )
    else:
        await message.reply(f'С возвращением, {message.from_user.first_name}! Решили снова найти новый для себя фильм?',
                            reply_markup=kb)
        await message.answer(
            "Если вдруг забыли, то нажмите 'Help', чтоб вспомнить возможности бота!",
            reply_markup=builder.as_markup()
        )


@dp.callback_query(F.data == "/help")
async def send_help(callback: types.CallbackQuery):
    await callback.answer(
        text=f"Функционал:\n\n"
             f"/genres - выбрать жанр для поиска фильма\n\n"
             f"/watchs - посмотреть список просмотренных фильмов\n\n"
             f"/reviews - посмотреть свои отзывы и оценки на фильмы.\n\n"
             f"/stop - прекратить работу",
        show_alert=True,
    )


async def film_image():
    async with aiohttp.ClientSession() as session:
        q = db_sess.query(Film).all()
        f = random.choice(q)
        async with session.get(
                f'https://yandex.ru/images/search?from=tabbar&text=кадр из фильма {f.title}') as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            sel = soup.select('div[class="SerpList"]')
            r_image = random.choice(sel[0].find_all('img'))
            link = r_image.get('src')
            return link
            # print(html, file=open('page.html', 'w', encoding='utf-8'))


@dp.message(Command('game'))
async def game(message: types.Message):
    await message.answer('Угадай фильм по кадру из него.')
    link = await film_image()
    print(link)
    await message.answer(link)


@dp.message(Command('help'))
async def stop(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Help",
        callback_data="/help"))
    await message.answer(
        "Нажмите 'Help', чтоб посмотреть возможности бота!",
        reply_markup=builder.as_markup()
    )


@dp.message(Command('genres'))
async def genres(message: types.Message):
    await message.answer('Выберите жанр из списка ниже:', reply_markup=gs)


def list_watchs(id, page):
    offset_v = int(page) * 10
    return ([x.film.title for x in db_sess.query(Watch).filter(Watch.id_user == id).limit(10).offset(offset_v).all()],
            db_sess.query(Watch).filter(Watch.id_user == id).count() // 10)


@dp.message(Command('watchs'))
async def send_list_watchs(message: types.Message):
    s_watchs = list_watchs(message.from_user.id, 0)
    if s_watchs[0]:
        data = "\n".join(s_watchs[0])
        try:
            z1 = (0 - 1) % s_watchs[1]
            z2 = (0 + 1) % s_watchs[1]
        except ZeroDivisionError:
            z1 = 0
            z2 = 0
        await message.answer(f'Список просмотренных фильмов:\n\n{data}',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [InlineKeyboardButton(text='<',
                                                           callback_data=f'com_3@{z1}'),
                                      InlineKeyboardButton(text='>',
                                                           callback_data=f'com_3@{z2}')]]))
    else:
        await message.answer('Вы не посмотрели ни одного фильма. Список просмотренных фильмов пуст.')


def list_reviews(id, page):
    print(page)
    offset_v = int(page) * 1
    return ([(x.review, x.grade, x.film.title) for x in
             db_sess.query(Review).filter(Review.id_user == id).limit(1).offset(offset_v).all()],
            db_sess.query(Review).filter(Review.id_user == id).count() // 1)


@dp.message(Command('reviews'))
async def send_list_reviews(message: types.Message):
    s_reviews = list_reviews(message.from_user.id, 0)
    print(s_reviews)
    if s_reviews[0][0]:
        r = s_reviews[0][0]
        await message.answer(f'Ваши отзывы:\n'
                             f'Фильм: {r[2]}\n\n'
                             f'Оценка: {r[1]}\n\n'
                             f'Отзыв: {r[0]}\n\n',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [InlineKeyboardButton(text='<',
                                                           callback_data=f'com_4@{(0 - 1) % s_reviews[1]}'),
                                      InlineKeyboardButton(text='>',
                                                           callback_data=f'com_4@{(0 + 1) % s_reviews[1]}')]]))
    else:
        await message.answer('Вы не оставили ни одного отзыва. Список ваших отзывов пуст.')


@dp.callback_query(F.data.in_(sp_g))
async def send_film(call: types.CallbackQuery):
    q = db_sess.query(Genre).filter(Genre.title == call.data).first().film
    q_films = []
    u_id = call.from_user.id
    films = [x.film for x in db_sess.query(Watch).filter(Watch.id_user == u_id).all()]
    for f in q:
        if f not in films:
            q_films.append(f)
    try:
        r_film = random.choice(q_films)
        await call.message.edit_text(f"Название: {r_film.title}\n\n"
                                     f"Жанр: {call.data}\n\n"
                                     f"Сюжет: {r_film.about}\n\n"
                                     f"Оценка: {r_film.grade}\nКол-во оценок: {r_film.quantity}\n\n"
                                     f"Ссылка на трейлер: {r_film.link}", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Посмотрел(а) фильм', callback_data=f'com_1@{r_film.id}')],
                             [InlineKeyboardButton(text='Получить случайный отзыв',
                                                   callback_data=f'com_2@{r_film.id}')]]))
    except IndexError:
        await call.message.answer("Больше нет фильмов по указанному жанру.")


class ReviewStates(StatesGroup):
    grade = State()
    review = State()
    confirm = State()


@dp.callback_query(F.data.startswith("com_"))
async def watch_and_reviews(call: types.CallbackQuery, state: FSMContext):
    d = call.data[4:].split('@')
    if d[0] == '1':
        watch = Watch()
        watch.id_user = call.from_user.id
        watch.id_film = int(d[1])
        db_sess.add(watch)
        db_sess.commit()
        await state.set_state(ReviewStates.confirm)
        await state.update_data(film=watch.id_film, user=watch.id_user)
        await call.message.edit_reply_markup(None)
        await call.message.answer("Хотите оставить отзыв и оценку?", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Да', callback_data=f'Да@{d[1]}')],
                             [InlineKeyboardButton(text='Нет', callback_data='Нет')]]))
    elif d[0] == '2':
        q = db_sess.query(Review).filter(Review.id_film == d[1]).all()
        try:
            r_review = random.choice(q)
            await call.message.edit_reply_markup(None)
            await call.message.answer(f"Автор: {r_review.user.name}\n\n"
                                      f"Оценка: {r_review.grade}\n\n"
                                      f"Отзыв: {r_review.review}", reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text='Посмотрел(а) фильм', callback_data=f'com_1@{d[1]}')],
                                 [InlineKeyboardButton(text='Получить случайный отзыв',
                                                       callback_data=f'com_2@{d[1]}')]]))
        except IndexError:
            await call.message.edit_reply_markup(None)
            await call.message.answer("На данный фильм нет отзывов.", reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text='Посмотрел(а) фильм', callback_data=f'com_1@{d[1]}')],
                                 [InlineKeyboardButton(text='Получить случайный отзыв',
                                                       callback_data=f'com_2@{d[1]}')]]))
    elif d[0] == '3':
        s_watchs = list_watchs(call.from_user.id, d[1])
        data = "\n".join(s_watchs[0])
        try:
            z1 = (int(d[1]) - 1) % s_watchs[1]
            z2 = (int(d[1]) + 1) % s_watchs[1]
        except ZeroDivisionError:
            z1 = 0
            z2 = 0
        await call.message.edit_text(f'Список просмотренных фильмов:\n\n{data}',
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[
                                             [InlineKeyboardButton(text='<',
                                                                   callback_data=f'com_3@{z1}'),
                                              InlineKeyboardButton(text='>',
                                                                   callback_data=f'com_3@{z2}')]]))
    elif d[0] == '4':
        s_reviews = list_reviews(call.from_user.id, d[1])
        print(s_reviews)
        r = s_reviews[0][0]
        await call.message.edit_text(f'Ваши отзывы:\n'
                                     f'Фильм: {r[2]}\n\n'
                                     f'Оценка: {r[1]}\n\n'
                                     f'Отзыв: {r[0]}\n\n',
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[
                                             [InlineKeyboardButton(text='<',
                                                                   callback_data=f'com_4@{(int(d[1]) - 1) % s_reviews[1]}'),
                                              InlineKeyboardButton(text='>',
                                                                   callback_data=f'com_4@{(int(d[1]) + 1) % s_reviews[1]}')]]))


@dp.callback_query(F.data == 'Нет')
async def end_fd(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_reply_markup(None)
    await call.message.answer('Нет так нет.')


@dp.callback_query(F.data.startswith('Да'))
async def feedback(call: types.CallbackQuery, state: FSMContext):
    d = call.data.split('@')
    await state.set_state(ReviewStates.grade)
    await call.message.delete()
    await call.message.answer('Поставьте оценку от 0 до 5:', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=f'{x}', callback_data=f'grade.{x}.{d[1]}')] for x in range(6)]
    ))


@dp.callback_query(F.data.startswith('grade.'))
async def safe_grade(call: types.CallbackQuery, state: FSMContext):
    d = call.data.split('.')
    await state.update_data(grade=d[1])
    await call.message.edit_text(f'Ваша оценка: {d[1]}')
    await call.message.answer('Спасибо за оценку!')

    q_film = db_sess.query(Film).filter(Film.id == int(d[2])).first()
    q_film.grade = round(((q_film.grade * q_film.quantity) + int(d[1])) / (q_film.quantity + 1), 2)
    q_film.quantity += 1
    db_sess.commit()

    await state.set_state(ReviewStates.review)
    await call.message.answer('Оставьте отзыв:')


@dp.message(ReviewStates.review)
async def safe_review(message: types.Message, state: FSMContext):
    data = await state.get_data()
    fback = Review()

    review = message.text

    fback.grade = data['grade']
    fback.review = review
    fback.id_user = data['user']
    fback.id_film = data['film']

    db_sess.add(fback)
    db_sess.commit()
    await state.clear()
    await message.answer('Сохранено!')


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока-пока!", reply_markup=ReplyKeyboardRemove())


@dp.message()
async def echo_message(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    asyncio.run(main())
