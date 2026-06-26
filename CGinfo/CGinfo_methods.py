import flet as ft

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
    def __init__(self, clasa : Clasa, page : ft.Page):
        super().__init__(content=ft.Text(f"{clasa.nivel}{clasa.nume}", size=50),)
        
        self._page = page
        self.clasa = clasa
        self.bgcolor = ft.Colors.BLUE_GREY_800
        self.color = ft.Colors.BLUE_GREY_200
        self.width = 300
        self.height = 120
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        self.on_click = self.class_selection

    def class_selection(self, e):
        self._page.clean()
        self._page.title = f"Clasa {self.clasa.nivel}{self.clasa.nume}"
        self._page.update()

class ButonAddClasa(ft.Button):
    def __init__(self, label_text, page : ft.Page):
        super().__init__(content=ft.Text(label_text, size=15, text_align=ft.TextAlign.CENTER),)
        
        self._page = page
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
        self.on_click = self.add_clasa

    def add_clasa(self, e):
        self._page.clean()
        self._page.title = "Adăugare clasă"
        self._page.update()