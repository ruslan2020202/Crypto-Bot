import datetime
import json
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN_BOT'))
dp = Dispatcher()


class Parser:
    url = "https://api.coingecko.com/api/v3/simple/price"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": os.getenv("TOKEN_API")
    }
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
    }

    def get_coin_price(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        with open('data.json', 'w') as file:
            data = json.loads(response.text)
            data['bitcoin']['time'] = datetime.datetime.now().strftime("%H:%M")
            file.write(json.dumps(data))

    def check_coin_price(self):
        with open('data.json', 'r') as file:
            data = json.loads(file.read())
            return f"BTC: {data['bitcoin']['usd']} $\n\nLast update: {data['bitcoin']['time']}"


parser = Parser()


@dp.message(CommandStart())
async def cdm_start(message: Message):
    await message.answer(
        "Hello, I'm a crypto bot. I will help you keep track of the current rates of all the most popular cryptocurrencies")


@dp.message(Command('price'))
async def cmd_price(message: Message):
    await message.answer(f'{parser.check_coin_price()}')


@dp.message(Command('photo'))
async def cmd_photo(message: Message):
    photo1 = open('img_1.png', 'r').read()
    await message.answer_photo(photo1, caption='Photo')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        print('Start Bot')
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        print('Exit')
