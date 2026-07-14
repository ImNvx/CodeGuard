import flet as ft
from tinydb import TinyDB, Query
import sqlite3
import random # !!! doar pentru dev testing
from CGinfo.kn import get_kn_id
from CGinfo.CGinfo_ds import *
import os
from pathlib import Path
import sys
import datetime
import CGinfo.database
import re

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

def get_unix_now():
    return datetime.datetime.now().timestamp() * 1000

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
                         ft.Row(controls=[ContestHistoryButton(page=self._page, clasa=self.clasa, back_route=self.class_selection), NewContestButton(self._page, clasa=self.clasa, back_route=self.class_selection)])],
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
                if tb_nume.value == '' or tb_kn_user.value == '' or (get_kn_id(tb_kn_user.value) == -1):
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
    
class NewContestButton(ft.Button):
    def __init__(self, page : ft.Page, clasa : Clasa, back_route):
        super().__init__(content=ft.Row(controls=[ft.Text("Contest nou", size=24, weight='bold', text_align=ft.TextAlign.CENTER),
                                 ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=55)], alignment=ft.MainAxisAlignment.CENTER, spacing=-2)) # prea multe paranteze haha
        self._page = page
        self.clasa = clasa
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
        self._page.title = "Contest nou"

        # banuiesc ca nu da nimeni concurs de la 11 noaptea pana urmatoarea zi, deci sper ca nu o sa fie probleme cu timpul daca il pun ca incepand azi si terminandu-se tot azi :/

        nume_concurs = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100)
        lista_probleme = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100, hint_text='ex: 4423, 4424, 4225')
        text_start_time = ft.TextField(f"{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}", text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100, read_only=True, width=150)
        text_end_time = ft.TextField(f"{datetime.datetime.now().hour:02}:{datetime.datetime.now().minute:02}", text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100, read_only=True, width=150)

        def set_start_time_text(e):
            text_start_time.value = f"{start_time.value.hour:02}:{start_time.value.minute:02}"
            self._page.update()

        def change_start_time(e):
            self._page.show_dialog(start_time)

        def set_end_time_text(e):
            text_end_time.value = f"{end_time.value.hour:02}:{end_time.value.minute:02}"
            self._page.update()

        def change_end_time(e):
            self._page.show_dialog(end_time)

        start_time = ft.TimePicker(
            hour_format=ft.TimePickerHourFormat.H24,
            on_change=set_start_time_text
        )

        end_time = ft.TimePicker(
            hour_format=ft.TimePickerHourFormat.H24,
            on_change=set_end_time_text
        )

        def push_contest_to_elev_db(id):
            db = get_db()
            q = Query()

            res = db.get((q.nivel == self.clasa.nivel) & (q.nume == self.clasa.nume))

            res['contest_ids'].append(id)
            db.update(
                {"contest_ids": res['contest_ids']},
                (q.nivel == self.clasa.nivel) & (q.nume == self.clasa.nume)
            )

        def finish_contest(e):
            if nume_concurs.value == '' or lista_probleme.value == '' or ((60 * end_time.value.hour + end_time.value.minute) - (60 * start_time.value.hour + start_time.value.minute) < 0):
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
            else:
                id_probleme = re.split(r'[;,\s]+', lista_probleme.value)

                t_start = datetime.datetime.now().replace(hour=start_time.value.hour, minute=start_time.value.minute) # din nou, sper ca nu incepe nimeni concurs la 11:59:59 noaptea

                t_end = t_start.replace(hour=end_time.value.hour, minute=end_time.value.minute)

                t_start_unix = int(t_start.timestamp() * 1000) 
                t_end_unix = int(t_end.timestamp() * 1000)

                id_contest = CGinfo.database.add_contest(
                    name=nume_concurs.value,
                    start_time=t_start_unix,
                    end_time=t_end_unix,
                    nume_clasa=self.clasa.nume,
                    nivel_clasa=self.clasa.nivel,
                    lista_probleme=id_probleme
                )
                if id_contest:
                     push_contest_to_elev_db(id_contest)
                     self._page.show_dialog(ft.SnackBar(
                        content=ft.Row(
                            controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINED, align=ft.Alignment.CENTER, color=ft.Colors.BLUE_GREY_100, size=40),
                            ft.Text("Contest creat cu succes!", size=22, weight='bold', text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_GREY_100)],
                            alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        duration=3000,
                        bgcolor=ft.Colors.TEAL_600
                        ))
                     self._page.update()


        self._page.add(
            ft.Row(
                ButonBack(dest=self.back_route),
            ),
            ft.Row(
                ft.Text("Contest nou", size=38, weight='bold'),
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                height=20
            ),

            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Nume concurs", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100, width=250),
                            nume_concurs
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Listă id-uri probleme", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100, width=250),
                            lista_probleme
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        height=30
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Ora de start:   ", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100), # pixel de ceee
                            text_start_time,
                            ft.ElevatedButton("Schimbă", on_click=change_start_time),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Ora de sfârșit: ", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100),
                            text_end_time,
                            ft.ElevatedButton("Schimbă", on_click=change_end_time),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        height=25
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(content=ft.Text("Start contest", size=18, text_align=ft.TextAlign.CENTER), width=200, height=50, icon=ft.Icons.PLAY_ARROW_ROUNDED, on_click=finish_contest)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
            )
        )

        return

def get_date_from_unix(ts):
    return datetime.datetime.fromtimestamp(ts / 1000)

class ContestButton(ft.Button):
    def __init__(self, page : ft.Page, contest_id : int, is_running : bool, properties : Contest, back_route):
        ts_start = get_date_from_unix(properties.start_time)
        ts_end = get_date_from_unix(properties.end_time)

        #submissions = CGinfo.database.get_submissions_of_contest(properties.id)
        submissions = 0
        correct_submissions = 0
        #for i in submissions:
        #    if i.score == 100:
        #       correct_submissions += 1

        super().__init__(content=
                         ft.Column(controls=[
                             ft.Row(
                                 controls=[ft.Text(f"{ts_start.strftime('%m/%d/%y')} {ts_start.strftime('%H:%M')} -> {ts_end.strftime('%H:%M')}", size=18),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                             ),
                             ft.Row(controls=[
                                  ft.Text(f"Contest #{contest_id}", size=45),
                             ],
                             alignment=ft.MainAxisAlignment.CENTER
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(f"Număr submisii: {correct_submissions}", text_align=ft.TextAlign.LEFT, size=14), # len(submissions)
                                    ft.Text(f"Submisii corecte: {correct_submissions}", text_align=ft.TextAlign.RIGHT, size=14)
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                         ],
                         spacing=2))
        
        self._page = page
        self.contest_id = contest_id
        self.properties = properties

        if is_running:
            self.bgcolor = ft.Colors.GREEN_ACCENT_400
            self.color = ft.Colors.BLACK
        else:
            self.bgcolor = ft.Colors.BLUE_GREY_200
            self.color = ft.Colors.BLACK
        
        self.width = 300
        self.height = 120
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        self.back_route = back_route

class ContestHistoryButton(ft.IconButton):
    def __init__(self, page : ft.Page, clasa : Clasa, back_route):
        super().__init__(icon=ft.Icons.HISTORY_ROUNDED, icon_size=40)
        self._page = page
        self.clasa = clasa
        self.back_route = back_route

        self.bgcolor = "#3A3A4A"
        self.color = ft.Colors.BLUE_GREY_100
        self.width = 60
        self.height = 60
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=18)
        )
        self.on_click = self.contest_history

    def get_contests_ids(self):
        all_contests = CGinfo.database.get_all_contests()
        contests = []

        ids = []
        db = get_db()
        q = Query()

        res = db.get((q.nivel == self.clasa.nivel) & (q.nume == self.clasa.nume))
        ids = res['contest_ids']

        for i in all_contests:
            if i.id in ids:
                contests.append(i)

        return contests
    
    

    def contest_history(self):
        self._page.clean()
        self._page.title = f"Istoric contest clasa {self.clasa.nivel}{self.clasa.nume}"
        contest_ids = self.get_contests_ids()

        self._page.add(
            ButonBack(self.back_route),
            ft.Container(
                content=ft.Row(
                controls=[
                    ft.Text("Istoric concursuri", size=38, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_100),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20),
        )

        def contest_is_running(current_time, end_time) -> bool:
            return (end_time - current_time) > 0
        
        contest_buttons = []
        for i in contest_ids:
            contest_buttons.append(ContestButton(page=self._page, contest_id=i.id, is_running=contest_is_running(get_unix_now(), i.end_time), properties=i, back_route=self.contest_history))

        contest_buttons.sort(key= lambda k : k.properties.end_time, reverse=True)

        for i in range(0, len(contest_ids), 3):
            self._page.add(
                ft.Row(
                    controls=contest_buttons[i:i+3],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=25
                )
            )

        self._page.update()
        return

###de aici in jos mi am bagat eu mainile - mester

