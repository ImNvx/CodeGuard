import flet as ft
from tinydb import TinyDB, Query
import sqlite3
import random # !!! doar pentru dev testing
from CGinfo.kn import get_kn_id
from CGinfo.CGinfo_ds import *
import os
from pathlib import Path
import sys

def get_elev_submissions(kn_user): #returneaza toate submisiile unui elev din db
    return "int main()"

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent

def get_db():
    exe_path = get_base_dir()
    path = exe_path / 'db_clase.json'
    return TinyDB(path)

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
        self.height = 45
        self.on_click = dest

class ButonElev(ft.Button):
    def __init__(self, nume):
        super().__init__(content=ft.Text(nume, size=20))
        self.width = 300
        self.height = 45
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15)
        )

class ButonClasa(ft.Button):
    def __init__(self, clasa : Clasa, page : ft.Page, back_route):
        super().__init__(content=ft.Text(f"{clasa.nivel}{clasa.nume}", size=50),)
        
        self._page = page
        self.clasa = clasa
        self.bgcolor = ft.Colors.LIGHT_BLUE_ACCENT_100
        self.color = ft.Colors.BLACK
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
                controls=[ButonBack(dest=self.back_route),
                         ft.Row(controls=[ContestHistoryButton(page=self._page, back_route=self.back_route), ContestButton(self._page, back_route=self.back_route)])],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True
            ),
            ft.Row(
                ft.Text(f"Clasa {self.clasa.nivel}{self.clasa.nume}", size=38, weight='bold'),
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                height=20 # pentru design
            )
        )
        
        db = get_db()
        q = Query()
        res = db.search((q.nivel == self.clasa.nivel) & (q.nume == self.clasa.nume)) # aceste 2 conditii ar trebui sa fie suficiente parerea mea
        
        elevi = [Elev(**e) for e in res[0]["elevi"]]
        elevi.sort(key = lambda k : k.nume)


        for i in elevi:
            self._page.add(
                ft.Row(
                    controls=ButonElev(nume=i.nume),
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )

        # adaugare lista cu elevii aici pe linia asta
        self._page.add(
            ft.Row(
                controls=[ButonAddElev(page = self._page, clasa=self.clasa, back_route=self.class_selection)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self._page.update()

class ButonAddClasa(ft.Button):
    def __init__(self, page : ft.Page, back_route):
        super().__init__(content=ft.Text("Adaugă o clasă nouă", size=16, text_align=ft.TextAlign.CENTER),)
        
        self._page = page
        self.bgcolor = ft.Colors.TEAL_ACCENT_400
        self.color = ft.Colors.BLACK
        self.width = 200
        self.height = 50
        self.icon = ft.Icon(
            ft.Icons.ADD_ROUNDED,
            size=35,
        )
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=16)
        )
        self.on_click = self.add_clasa
        self.back_route = back_route

    

    def add_clasa(self, e):
        self._page.clean()
        self._page.title = "Adăugare clasă"

        dropdown_nivel = ft.Dropdown(
            options=[
                ft.DropdownOption(key=5, text="5"),
                ft.DropdownOption(key=6, text="6"),
                ft.DropdownOption(key=7, text="7"),
                ft.DropdownOption(key=8, text="8"),
                ft.DropdownOption(key=9, text="9"),
                ft.DropdownOption(key=10, text="10"),
                ft.DropdownOption(key=11, text="11"),
                ft.DropdownOption(key=12, text="12"),
            ],
            text_align=ft.TextAlign.CENTER, # de ce nu arata centrat totusi in ui???????
            border_color=ft.Colors.BLUE_GREY_100,
            text_size=18,
            width=150
        )
        nume_clasa = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100, width=150)

        def push_clasa_noua(e):
            db = get_db()

            if dropdown_nivel.value != None and nume_clasa.value != '': # fac check ca sa nu fie empty field-urile
                    clasa = Clasa(int(dropdown_nivel.value), nume_clasa.value)
                    db.insert(Clasa.to_dict(clasa))
                    print(Clasa.to_dict(clasa))

                    self._page.show_dialog(ft.SnackBar(
                    content=ft.Row(
                        controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINED, align=ft.Alignment.CENTER, color=ft.Colors.BLUE_GREY_100, size=40),
                        ft.Text("Clasă adăugată cu succes!", size=22, weight='bold', text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_GREY_100)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    duration=3000,
                    bgcolor=ft.Colors.TEAL_600
                    ))
                    self._page.update()
            else:
                self._page.show_dialog(ft.SnackBar(
                    content=ft.Row(
                        controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, align=ft.Alignment.CENTER, color=ft.Colors.BLUE_GREY_100, size=40),
                        ft.Text("Valori invalide", size=22, weight='bold', text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_GREY_100)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    duration=3000,
                    bgcolor=ft.Colors.RED_900
                    ))
                self._page.update()

        self._page.add(
            ft.Row(
                ButonBack(dest=self.back_route)
            ),
            ft.Container(
                content=ft.Row(
                controls=[
                    ft.Text("Adăugare clasă", size=38, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                ),
            padding=20
            ),
            
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Nivel clasă", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100, width=150),
                            dropdown_nivel
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Nume clasă", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100, width=150),
                            nume_clasa
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
            ]
        ),
        ft.Row(
            controls=[
                ft.ElevatedButton(content=ft.Text("Adaugă Clasă", color=ft.Colors.BLUE_GREY_100, size=16), width=150, height=50, on_click=push_clasa_noua)],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
        self._page.update()
    

class ButonAddElev(ft.Button):
    def __init__(self, page : ft.Page, clasa, back_route):
        super().__init__(content=ft.Text("Adaugă un elev", size=17, text_align=ft.TextAlign.CENTER),)
        
        self._page = page
        self.bgcolor = ft.Colors.TEAL_ACCENT_400
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
        self.on_click = self.add_elev
        self.back_route = back_route
        self.clasa = clasa
    
    def add_elev(self, e):
        self._page.clean()
        self._page.title = "Adăugare elev"
        tb_nume = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100)
        tb_kn_user = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100)

        def push_elev_nou(e):
            db = get_db()
            q = Query()

            res = db.get((q.nivel == self.clasa.nivel) & (q.nume == self.clasa.nume))
            if res: # am adaugat checking ca sa aiba sens mesajul de succes :))
                if tb_nume.value == '' or tb_kn_user.value == '':
                    self._page.show_dialog(ft.SnackBar(
                    content=ft.Row(
                        controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, align=ft.Alignment.CENTER, color=ft.Colors.BLUE_GREY_100, size=40),
                        ft.Text("Valori invalide", size=22, weight='bold', text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_GREY_100)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    duration=3000,
                    bgcolor=ft.Colors.RED_900
                ))
                    
                else:
                    elev = Elev(nume=tb_nume.value, kn_user=tb_kn_user.value, id=get_kn_id(tb_kn_user.value))

                    res['elevi'].append(elev.to_dict())
                    db.update(
                        {"elevi": res['elevi']},
                        (q.nivel == self.clasa.nivel) & (q.nume == self.clasa.nume)
                    )
                    self._page.show_dialog(ft.SnackBar(
                        content=ft.Row(
                            controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINED, align=ft.Alignment.CENTER, color=ft.Colors.BLUE_GREY_100, size=40),
                            ft.Text("Elev adăugat cu succes!", size=22, weight='bold', text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_GREY_100)],
                            alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        duration=3000,
                        bgcolor=ft.Colors.TEAL_600
                    ))
                    self._page.update()
            else:
                self._page.show_dialog(ft.SnackBar(
                    content=ft.Row(
                        controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, align=ft.Alignment.CENTER, color=ft.Colors.BLUE_GREY_100, size=40),
                        ft.Text("Eroare, clasa nu există în baza de date sau ceva a mers rău", size=22, weight='bold', text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_GREY_100)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    duration=3000,
                    bgcolor=ft.Colors.RED_900
                ))
                self._page.update()
            

        self._page.add(
            ButonBack(self.back_route),
            ft.Container(
                content=ft.Row(
                controls=[
                    ft.Text("Adăugare elev", size=38, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20),
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Nume elev", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100, width=250),
                            tb_nume
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Username kilonova", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100, width=250),
                            tb_kn_user
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(content=ft.Text("Adaugă Elev", color=ft.Colors.BLUE_GREY_100, size=18), width=150, height=50, on_click=push_elev_nou)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.START
            )
        )

        self._page.update()

# !!!! neaparat sa fac elementele sa isi dea resize in functie de window size, probabil ca event 
# pe window resize si sa fie un procent din size-ul curent sau ceva multiplier in functie de size
class MainPage():
    def __init__(self, page : ft.Page):
        self._page = page
        self.db = get_db()
        
    def loadPage(self):
        self.clase = [Clasa(**i) for i in self.db.all()]
        self.clase.sort(key=lambda k : (k.nivel, k.nume))
        self.class_buttons = [ButonClasa(clasa=i, page=self._page, back_route=self.loadPage) for i in self.clase]

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
                    content=ft.Image(src="CGinfo/cg_shield.png", width=125),
                    alignment=ft.Alignment.TOP_CENTER,
                    padding=20,
                ),
                
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
                controls=[ButonAddClasa(page=self._page, back_route=self.loadPage)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
    
class ContestButton(ft.Button):
    def __init__(self, page : ft.Page, back_route):
        super().__init__(content=ft.Row(controls=[ft.Text("Contest nou", size=24, weight='bold', text_align=ft.TextAlign.CENTER),
                                 ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=55)], alignment=ft.MainAxisAlignment.CENTER, spacing=-2)) # prea multe paranteze haha
        self._page = page
        self.back_route = back_route

        self.bgcolor = ft.Colors.TEAL_ACCENT_100
        self.color = ft.Colors.BLUE_GREY_900
        self.width = 220
        self.height = 60
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=18)
        )
        self.on_click = self.contest_creation

    def contest_creation(self):
        self._page.clean()
        

        return

class ContestHistoryButton(ft.IconButton):
    def __init__(self, page : ft.Page, back_route):
        super().__init__(icon=ft.Icons.HISTORY_ROUNDED, icon_size=40)
        self._page = page
        self.back_route = back_route

        self.bgcolor = "#3A3A4A"
        self.color = ft.Colors.BLUE_GREY_100
        self.width = 60
        self.height = 60
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=18)
        )

    def contest_history(self):
        return

###de aici in jos mi am bagat eu mainile - mester

