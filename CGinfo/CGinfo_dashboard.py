import flet as ft
import json
from tinydb import TinyDB, Query
import sqlite3
from CGinfo_methods import *

def main(page: ft.Page):
    db = TinyDB('db_clase.json')
    clase = [Clasa(**i) for i in db.all()]
    clase.sort(key=lambda k : (k.nivel, k.nume))

    mp = MainPage(page = page, clase=clase)
    mp.loadPage()

ft.run(main)