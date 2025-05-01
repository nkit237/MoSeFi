import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from env import TG_TOKEN
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db_session
from db_session import User, Genre, Watch, Review

reply_keyboard = [[KeyboardButton(text='/help'), KeyboardButton(text='/genres')],
                  [KeyboardButton(text="/stop")]]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

db_sess = db_session.create_session()

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


async def main():
    bot = Bot(token=TG_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def start(message: types.Message):
    u_id = message.from_user.id
    user = db_sess.query(User).filter(User.id_user == u_id).first()
    if not user:
        user = User()
        user.id_user = u_id
        user.name = message.from_user.first_name
        db_sess.add(user)
        db_sess.commit()

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Help",
        callback_data="/help")
    )
    await message.reply('Привет! Это бот для поиска фильмов!', reply_markup=kb)
    await message.answer(
        "Нажми 'Help', чтоб узнать о возможностях бота!",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "/help")
async def send_help(callback: types.CallbackQuery):
    await callback.answer(
        text=f"/genres - выбрать жанр для поиска фильма\n"
             f"/stop - прекратить работу",
        show_alert=True,
    )


@dp.message(Command('help'))
async def stop(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Help",
        callback_data="/help"))
    await message.answer(
        "Нажми 'Help', чтоб узнать о возможностях бота!",
        reply_markup=builder.as_markup()
    )


@dp.message(Command('genres'))
async def genres(message: types.Message):
    await message.answer('Выберите жанр из списка ниже:', reply_markup=gs)


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
        await call.message.answer(f"Название: {r_film.title}\n\nСюжет: {r_film.about}\n\n"
                                  f"Оценка: {r_film.grade}\nКол-во оценок: {r_film.quantity}\n\n"
                                  f"Ссылка на трейлер: {r_film.link}", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Посмотрел(а) фильм', callback_data=f'com_1@{r_film.id}')],
                             [InlineKeyboardButton(text='Получить случайный отзыв',
                                                   callback_data=f'com_2@{r_film.id}')]]))
    except IndexError:
        await call.message.answer("Больше нет фильмов по указанному жанру.")


@dp.callback_query(F.data.startswith("com_"))
async def watch_and_reviews(call: types.CallbackQuery):
    d = call.data[4:].split('@')
    if d[0] == '1':
        # пример добавления просмотра, но он должен быть не тут, а после оценки и оставления отзыва
        # watch = Watch()
        # watch.id_user = call.from_user.id
        # watch.id_film = int(d[1])
        # db_sess.add(watch)
        # db_sess.commit()
        await call.message.answer("Поставь оценку и оставь свой отзыв на фильм.")
    elif d[0] == '2':
        q = db_sess.query(Review).filter(Review.id_film == d[1]).all()
        try:
            r_review = random.choice(q)
            await call.message.answer(f"Автор: {r_review.user.name}\n\n"
                                      f"Оценка: {r_review.grade}\n\n"
                                      f"Отзыв: {r_review.review}", reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text='Посмотрел(а) фильм', callback_data=f'com_1@{d[1]}')],
                                 [InlineKeyboardButton(text='Получить случайный отзыв',
                                                       callback_data=f'com_2@{d[1]}')]]))
        except IndexError:
            await call.message.answer("На данный фильм нет отзывов.", reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text='Посмотрел(а) фильм', callback_data=f'com_1@{d[1]}')],
                                 [InlineKeyboardButton(text='Получить случайный отзыв',
                                                       callback_data=f'com_2@{d[1]}')]]))


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока-пока!", reply_markup=ReplyKeyboardRemove())


@dp.message()
async def echo_message(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    asyncio.run(main())
