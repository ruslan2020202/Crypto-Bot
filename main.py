import json

import requests
import os


class Parser:
    url = "https://api.coingecko.com/api/v3/simple/price"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": os.getenv("TOKEN")
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
            return f"{data['bitcoin']['usd']} $"


pars = Parser()

print(pars.check_coin_price())
