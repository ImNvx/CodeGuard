import flet as ft

class Clasa:
    def __init__(self, nivel=9, nume="A", nr_elevi=0):
        self.nivel = nivel
        self.nume = nume
        self.nr_elevi = nr_elevi
        self.elevi = []

class Elev:
    def __init__(self, nume, istoric_submisii):
        self.nume = nume
        self.istoric_submisii = istoric_submisii

class ButonClasa(ft.Button):
    def __init__(self, label_text):
        super().__init__(content=ft.Text(label_text, size=50),)
        
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK
        self.width = 300
        self.height = 120
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8)
        )


def main(page: ft.Page):
    clase = [Clasa(nume="B"), Clasa(nr_elevi=28), Clasa(nivel=10, nume="B", nr_elevi=22), Clasa(nivel=11, nume="C", nr_elevi=25), Clasa(nivel=7, nume="D", nr_elevi=33),
             Clasa(nivel=5, nume="A")
            ] # aici o sa facem sa le ia din db mai tarziu (tinyDB pare smecher)
    
    clase.sort(key=lambda k : (k.nivel, k.nume))

    page.title = "CGinfo"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK

    class_buttons = [ButonClasa(label_text=f"{i.nivel}{i.nume}") for i in clase]

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

    #sa fac padding adjustment pe window resize

ft.run(main)