import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from env import TG_TOKEN
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

import db_session
from db_session import User, Genre

reply_keyboard = [[KeyboardButton(text='/help'), KeyboardButton(text='/genre')],
                  [KeyboardButton(text='/reg'), KeyboardButton(text="/stop")]]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

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
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id_user==u_id).first()
    if not user:
        user = User()
        user.id_user = u_id
        user.name = message.from_user.first_name
        db_sess.add(user)
        db_sess.commit()
    await message.reply("Привет! Это бот для поиска фильмов! Нажми /help, чтоб узнать о возможностях бота!",
                        reply_markup=kb)


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока.", reply_markup=ReplyKeyboardRemove())


@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply('/genre - выбрать фильм по жанру \n'
                        '/reg - зарегистрироваться в MoSeFi \n'
                        '/stop - прекратить работу \n')


@dp.message(Command('reg'))
async def address(message: types.Message):
    await message.reply("Soon")


@dp.message(Command('genre'))
async def genre(message: types.Message):
    db_sess = db_session.create_session()
    n = 'комедия'
    g = db_sess.query(Genre).filter(Genre.title==n).first()
    try:
        r_film = random.choice(g.film)
        await message.reply(r_film.title)
    except IndexError:
        await message.reply("Нет таких фильмов")



@dp.message()
async def echo_message(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    asyncio.run(main())
