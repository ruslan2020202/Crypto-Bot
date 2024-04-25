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
            file.write(response.text)

    def check_coin_price(self):
        with open('data.json', 'r') as file:
            data = json.loads(file.read())
            return f"BTC: {data['bitcoin']['usd']} $\n\nLast update: {data['bitcoin']['time']}"

    def add_time(self):
        with open('data.json', 'r') as file:
            data = json.loads(file.read())
        data['bitcoin']['time'] = datetime.datetime.now().strftime("%H:%M")
        with open('data.json', 'w') as file:
            file.write(json.dumps(data))


parser = Parser()


def update_price():
    parser.get_coin_price()
    parser.add_time()


@dp.message(CommandStart())
async def cdm_start(message: Message):
    await message.answer(
        "Hello, I'm a crypto bot. I will help you keep track of the current rates of all the most popular cryptocurrencies")


@dp.message(Command('price'))
async def cmd_price(message: Message):
    await message.answer(f'{parser.check_coin_price()}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        print('Start Bot')
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        print('Exit')
