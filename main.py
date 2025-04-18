import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from env import TG_TOKEN  # импортируем токен
import logging

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

# создаем диспетчер
dp = Dispatcher()


async def main():
    bot = Bot(token=TG_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))  # декоратор для обработчика команды start
async def process_start_command(message: types.Message):
    """
    Создаем и регистрируем в диспетчере асинхронный обработчик сообщений.
    В параметре message содержится вся информация о сообщении - см. документацию.
    """
    await message.reply("Привет!\nНапиши мне что-нибудь!")  # отправляет ответ на сообщение


@dp.message(Command('help'))  # декоратор для обработчика команды help
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отправлю этот текст тебе в ответ!")


@dp.message()  # декоратор для обработчика прочих сообщений
async def echo_message(message: types.Message):
    await message.answer(message.text)  # отправляет обратно новое сообщение с тем же текстом


if __name__ == '__main__':
    asyncio.run(main())  # начинаем принимать сообщения
