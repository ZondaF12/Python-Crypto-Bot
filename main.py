# main.py
import os
import random
import discord
import asyncio
import time
import datetime
import locale
from dotenv import load_dotenv
from datetime import date
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# 1
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# 2
bot = commands.Bot(command_prefix='#')
locale.setlocale(locale.LC_ALL, "en_GB")


@bot.event
async def on_ready():
    print("CryptoBot is active")


@bot.command(pass_context=True, name='c', help='To use this command do #c <symbol>')
async def c(ctx):
    symbol = ctx.message.content.split(" ")[1]
    coinName, coinPrice, coin24h, coin7d, marketcap, volume24h, supply, rank, cmc_id = await get_price(symbol.upper())

    if coinName and coinPrice and coin24h and coin7d and marketcap and volume24h and supply and rank and cmc_id:

        embed = discord.Embed(
            title="Cryptocurrency Price Tracker",
            description=f"**Coin (Rank)** \n{str(coinName)} (#{rank})",
            color=(0xF85252)
        )
        embed.add_field(
            name="**Price (24h)**",
            value=f"{str(locale.currency(coinPrice,grouping=True))}" +
            f" ({str(round(coin24h,3))}%)",
            inline=False
        )
        embed.add_field(
            name="**7 Day Percentage Change**",
            value=f"{str(round(coin7d,3))}%",
            inline=True
        )
        embed.add_field(
            name="**Market Cap**",
            value=f"{str(locale.currency(marketcap,grouping=True))}",
            inline=False
        )
        embed.add_field(
            name="**Circulating Supply**",
            value=f"{str(locale.currency(supply,symbol=False,grouping=True))} {symbol.upper()}",
            inline=False
        )
        embed.add_field(
            name="**24h Volume**",
            value=f"{str(locale.currency(volume24h,grouping=True))}",
            inline=False
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_thumbnail(
            url=f"https://s2.coinmarketcap.com/static/img/coins/64x64/{cmc_id}.png"
        )
        embed.set_footer(text="Made by Roo#7777",
                         icon_url="https://cdn.discordapp.com/avatars/181094829500006400/98e8dda773d8c880029da1927da85dc0.png?size=256")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Crypto Price",
            description="Please input a correct coin symbol, e.g. BTC or ETH",
            color=(0xF85252)
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="Made by Roo#7777",
                         icon_url="https://cdn.discordapp.com/avatars/181094829500006400/98e8dda773d8c880029da1927da85dc0.png?size=256")
        await ctx.send(embed=embed)


async def get_price(symbol):
    parameters = {
        "symbol": symbol,
        "convert": "GBP"
    }

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv('API_KEY'),
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        parseData = json.dumps(response.json())
        priceObj = json.loads(parseData)

        coinName = priceObj["data"][symbol]["name"]
        coinPrice = priceObj["data"][symbol]["quote"]["GBP"]["price"]
        coin24h = priceObj["data"][symbol]["quote"]["GBP"]["percent_change_24h"]
        coin7d = priceObj["data"][symbol]["quote"]["GBP"]["percent_change_7d"]
        marketcap = priceObj["data"][symbol]["quote"]["GBP"]["market_cap"]
        volume24h = priceObj["data"][symbol]["quote"]["GBP"]["volume_24h"]
        supply = priceObj["data"][symbol]["circulating_supply"]
        rank = priceObj["data"][symbol]["cmc_rank"]
        cmc_id = priceObj["data"][symbol]["id"]

        return (coinName, coinPrice, coin24h, coin7d, marketcap, volume24h, supply, rank, cmc_id)

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


bot.run(TOKEN)
