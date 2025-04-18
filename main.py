import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from env import TG_TOKEN  # импорт токена
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

reply_keyboard = [[KeyboardButton(text='/address'), KeyboardButton(text='/phone')],
                  [KeyboardButton(text='/site'), KeyboardButton(text='/work_time')],
                  [KeyboardButton(text="/stop")]]
kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

# создаем маршрутизатор
dp = Dispatcher()


async def main():
    bot = Bot(token=TG_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.reply("Привет.", reply_markup=kb)


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока.", reply_markup=ReplyKeyboardRemove())


@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply("Я бот справочник.")


@dp.message(Command('address'))
async def address(message: types.Message):
    await message.reply("Адрес: г. Москва, ул. Льва Толстого, 16")


@dp.message(Command('phone'))
async def phone(message: types.Message):
    await message.reply("Телефон: +7(495)776-3030")


@dp.message(Command('site'))
async def site(message: types.Message):
    await message.reply("Сайт: http://www.yandex.ru/company")


@dp.message(Command('work_time'))
async def work_time(message: types.Message):
    await message.reply("Время работы: круглосуточно.")


@dp.message()  # декоратор для обработчика прочих сообщений
async def echo_message(message: types.Message):
    await message.answer(message.text)  # отправляет обратно новое сообщение с тем же текстом


if __name__ == '__main__':
    asyncio.run(main())  # начинаем принимать сообщения
