import flet as ft
import json
from tinydb import TinyDB, Query
import sqlite3
from CGinfo_methods import *

def add_clasa(e, page : ft.Page):
    page.title = "Adăugare clasă"


def main_page(page, clase, class_buttons):
    page.add(
        ft.Stack(
            controls=[
                ft.Container(
                    content=ft.Text("CGinfo Dashboard", size=35, weight=ft.FontWeight.BOLD),
                    alignment=ft.Alignment.TOP_LEFT,
                    padding=15,
                ),
                
                ft.Container(
                    content=ft.Image(src="cg_shield.png", width=125),
                    alignment=ft.Alignment.TOP_CENTER,
                    padding=20,
                )
            ],
            height=200
        ),
    )

    for i in range(0, len(clase), 3):
        page.add(
            ft.Row(
                controls=class_buttons[i:i+3],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=25
            )
        )
    page.add(
        ft.Row(
            controls=[ButonAddClasa("Adăugă o clasă nouă", page=page)],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    #sa fac padding adjustment pe window resize

def main(page: ft.Page):
    db = TinyDB('db_clase.json')
    clase = [Clasa(**i) for i in db.all()]

    clase.sort(key=lambda k : (k.nivel, k.nume))

    page.title = "CGinfo"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK

    class_buttons = [ButonClasa(clasa=i, page=page) for i in clase]

    main_page(page, clase, class_buttons)

ft.run(main)