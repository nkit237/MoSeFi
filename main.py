import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from env import TG_TOKEN
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import db_session
from db_session import User, Genre

reply_keyboard = [[KeyboardButton(text='/help'), KeyboardButton(text='/genres')],
                  [KeyboardButton(text="/stop")]]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

db_sess = db_session.create_session()
genres = []
for g in db_sess.query(Genre):
    genres.append([InlineKeyboardButton(text=str(g.title), callback_data=str(g.title))])
gs = InlineKeyboardMarkup(inline_keyboard=[g for g in genres])

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
        text="/genres - выбрать фильм по жанру \n"
             "/stop - прекратить работу \n",
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
    await message.answer('Выберите жанр', reply_markup=gs)


'''@dp.callback_query(F.data in db_sess.query(Genre))
async def send_film(call: types.CallbackQuery):
    q = db_sess.query(Genre).filter(Genre.title == F.data).first()
    try:
        r_film = random.choice(q.film)
        await call.message.answer(r_film.title)
    except IndexError:
        await call.message.answer("Нет такого фильма.")'''


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока-пока!", reply_markup=ReplyKeyboardRemove())


@dp.message()
async def echo_message(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    asyncio.run(main())
