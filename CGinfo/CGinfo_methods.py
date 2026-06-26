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

class ButonBack(ft.IconButton):
    def __init__(self, dest):
        super().__init__()

        self.bgcolor = ft.Colors.BLUE_GREY_800
        self.style= ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=18)
        )
        self.icon = ft.Icon(
            ft.Icons.ARROW_BACK,
            size=30
        )
        self.width = 60
        self.on_click = lambda e : dest()

class ButonClasa(ft.Button):
    def __init__(self, clasa : Clasa, page : ft.Page, back_route):
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
        self.back_route = back_route

    def class_selection(self, e):
        self._page.clean()
        self._page.title = f"Clasa {self.clasa.nivel}{self.clasa.nume}"
        self._page.add(
            ft.Row(
                ButonBack(dest=self.back_route)
            )
        )
        self._page.update()

class ButonAddClasa(ft.Button):
    def __init__(self, label_text, page : ft.Page, back_route):
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
        self.back_route = back_route

    def add_clasa(self, e):
        self._page.clean()
        self._page.title = "Adăugare clasă"
        self._page.add(
            ft.Row(
                ButonBack(dest=self.back_route)
            )
        )
        self._page.update()

class MainPage():
    def __init__(self, page : ft.Page, clase):
        self._page = page
        self.clase = clase
        self.class_buttons = [ButonClasa(clasa=i, page=self._page, back_route=self.loadPage) for i in self.clase]
        
    def loadPage(self):
        self._page.clean()
        self._page.title = "CGinfo"
        self._page.vertical_alignment = ft.MainAxisAlignment.START
        self._page.theme_mode = ft.ThemeMode.DARK
        self._page.update()

        self._page.add(
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

        for i in range(0, len(self.clase), 3):
            self._page.add(
                ft.Row(
                    controls=self.class_buttons[i:i+3],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=25
                )
            )
        self._page.add(
            ft.Row(
                controls=[ButonAddClasa("Adăugă o clasă nouă", page=self._page, back_route=self.loadPage)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ) #sa fac padding adjustment pe window resize
