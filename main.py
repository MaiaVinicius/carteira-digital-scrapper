import datetime
import json
import os
from dotenv import load_dotenv

from Santander.SantanderScrapper import SantanderScrapper

load_dotenv(verbose=True)

from Clear.ClearScrapper import ClearScrapper
from GuiaBolso.GuiaBolsoScrapper import GuiaBolsoScrapper
from Rico.RicoScrapper import RicoScrapper
from SmarttBot.SmarttBotScrapper import SmarttBotScrapper


def save_output(provider, data):
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    time = datetime.datetime.today().strftime('%X')

    dir = 'output/' + date + '/'
    if not os.path.exists(dir):
        os.makedirs(dir)

    f = open(dir + provider + '.json', 'w')

    data['date'] = date
    data['time'] = time
    data['label'] = provider

    f.write(json.dumps(data))
    f.close()


def scrap_rico():
    if os.getenv("RICO_USR"):
        rico_scrapper = RicoScrapper(os.getenv("RICO_USR"), os.getenv("RICO_PWD"))
        res = rico_scrapper.init()

        save_output('rico', res)


def scrap_clear():
    if os.getenv("CLEAR_CPF"):
        clear_scrapper = ClearScrapper(os.getenv("CLEAR_CPF"), os.getenv("CLEAR_PWD"), os.getenv("CLEAR_BIRTHDATE"))

        res = clear_scrapper.init()
        save_output('clear', res)


def scrap_smartt_bot():
    if os.getenv("SMARTT_BOT_USR"):
        smartt_bot_scrapper = SmarttBotScrapper(os.getenv("SMARTT_BOT_USR"), os.getenv("SMARTT_BOT_PWD"))

        res = smartt_bot_scrapper.init()
        save_output('smartt_bot', res)


def scrap_guiabolso():
    if os.getenv("GUIABOLSO_USR"):
        guiabolso_scrapper = GuiaBolsoScrapper(os.getenv("GUIABOLSO_USR"), os.getenv("GUIABOLSO_PWD"))

        res = guiabolso_scrapper.init()
        save_output('guiabolso', res)


def scrap_santander():
    guiabolso_scrapper = SantanderScrapper(os.getenv("SANTANDER_CPF"), os.getenv("SANTANDER_PWD"),
                                           os.getenv("SANTANDER_LAST_DIGITS"))

    res = guiabolso_scrapper.init()


def scrap_all():
    scrap_guiabolso()
    scrap_clear()
    scrap_rico()
    scrap_smartt_bot()


# scrap_smartt_bot()
# scrap_clear()
# scrap_guiabolso()
scrap_all()
# scrap_rico()
# scrap_santander()
