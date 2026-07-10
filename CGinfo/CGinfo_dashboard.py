import flet as ft
import json
from tinydb import TinyDB, Query
import sqlite3
from CGinfo.CGinfo_methods import *

def main(page: ft.Page):
    page.window.min_width = 1000
    page.window.min_height = 600
    page.scroll = ft.ScrollMode.AUTO

    mp = MainPage(page = page)
    mp.loadPage()

ft.run(main)