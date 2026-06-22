import flet as ft
import json
from tinydb import TinyDB, Query

class Clasa:
    def __init__(self, nivel=9, nume="A", nr_elevi=0, elevi=[]):
        self.nivel = nivel
        self.nume = nume
        self.nr_elevi = nr_elevi
        self.elevi = []

    def to_dict(x):
        return {
            "nivel" : x.nivel,
            "nume" : x.nume,
            "nr_elevi" : x.nr_elevi,
            "elevi" : x.elevi
        }

class Elev:
    def __init__(self, nume, istoric_submisii):
        self.nume = nume
        self.istoric_submisii = istoric_submisii

class ButonClasa(ft.Button):
    def __init__(self, label_text):
        super().__init__(content=ft.Text(label_text, size=50),)
        
        self.bgcolor = ft.Colors.BLUE_GREY_800
        self.color = ft.Colors.BLUE_GREY_200
        self.width = 300
        self.height = 120
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12)
        )

class ButonAddClasa(ft.Button):
    def __init__(self, label_text):
        super().__init__(content=ft.Text(label_text, size=15, text_align=ft.TextAlign.CENTER),)
        
        self.bgcolor = ft.Colors.TEAL_200
        self.color = ft.Colors.BLACK
        self.width = 200
        self.height = 50
        self.icon = ft.Icon(
            ft.Icons.ADD,
            size=25,
        )
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=16)
        )

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
            controls=[ButonAddClasa("Adăugă o clasă nouă",)],
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

    def classSelection(e):
        page.clean()

    class_buttons = [ButonClasa(label_text=f"{i.nivel}{i.nume}") for i in clase]
    for i in class_buttons: #spaghetti code
        i.on_click = classSelection

    
    main_page(page, clase, class_buttons)

ft.run(main)