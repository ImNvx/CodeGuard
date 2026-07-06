import flet as ft
import json
from tinydb import TinyDB, Query
import sqlite3
from CGinfo_methods import *


def main(page: ft.Page):
    db = TinyDB('db_clase.json')
    #print(get_clasa(5, "A"))
    clase = [Clasa(**i) for i in db.all()]
    clase.sort(key=lambda k : (k.nivel, k.nume))

    page.window.min_width = 1000
    page.window.min_height = 600
    page.scroll = ft.ScrollMode.AUTO

    mp = MainPage(page = page, clase=clase)
    mp.loadPage()

ft.run(main)