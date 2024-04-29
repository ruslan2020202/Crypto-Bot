import asyncio
import logging
import aioschedule
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

import datetime
import json
import requests
import os
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class ConfigBot:
    token: str


@dataclass
class ConfigDb:
    db_host: str
    db_name: str
    db_user: str
    db_password: str


@dataclass
class ConfigApi:
    url: str
    token: str


@dataclass
class Config:
    bot: ConfigBot
    db: ConfigDb
    api: ConfigApi


def load_config():
    load_dotenv()

    config = Config(
        bot=ConfigBot(token=os.getenv("TOKEN_BOT")),
        db=ConfigDb(db_host=os.getenv("DB_HOST"),
                    db_name=os.getenv("DB_NAME"),
                    db_user=os.getenv("DB_USER"),
                    db_password=os.getenv("DB_PASSWORD")),
        api=ConfigApi(url=os.getenv("URL_API"), token=os.getenv("TOKEN_API")))

    return config


config = load_config()


class Parser:
    URL = config.api.url
    HEADERS = {
        "accept": "application/json",
        "x-cg-demo-api-key": config.api.token
    }

    def __init__(self, coin: str):
        self.coin = coin
        self.PARAMS = {"vs_currencies": "usd", "include_24hr_change": "true", 'ids': coin}

    def get_coin_price(self):
        response = requests.get(self.URL, headers=self.HEADERS, params=self.PARAMS)
        data = json.loads(response.text)
        data[f'{self.coin}']['time'] = datetime.datetime.now().strftime("%H:%M")
        data[f'{self.coin}']['usd_24h_change'] = round(data[f'{self.coin}']['usd_24h_change'], 2)
        return json.dumps(data)

    def check_coin_price(self):
        with open('data.json', 'r') as file:
            data = json.loads(file.read())
            change_price = f"{data[self.coin]['usd_24h_change']}%"
            if int(data[self.coin]['usd_24h_change']) > 0:
                change_price += '💹'
            else:
                change_price += "🔻"
            return (f"BTC: {data[self.coin]['usd']} $\n\n"
                    f"Change price with 24 hours: {change_price}\n\n"
                    f"Last update: {data[self.coin]['time']}")


btc = Parser('bitcoin')
eth = Parser('ethereum')
bot = Bot(config.bot.token)
dp = Dispatcher()


async def change_price():
    with open('data.json', 'w') as file:
        data = btc.get_coin_price()
        file.write(data)


async def update_price():
    while True:
        await change_price()
        await asyncio.sleep(10)
        print('update price')


@dp.message(CommandStart())
async def cdm_start(message: Message):
    await message.answer(
        "Hello, I'm a crypto bot. I will help you keep track of the current rates of all the most popular cryptocurrencies")


@dp.message(Command('price'))
async def cmd_price(message: Message):
    await message.answer(f'{btc.check_coin_price()}')


async def main():
    logging.basicConfig(level=logging.INFO)

    tasks = [
        asyncio.create_task(update_price()),
        asyncio.create_task(dp.start_polling(bot))
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
