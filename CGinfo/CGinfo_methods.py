import flet as ft
from tinydb import TinyDB, Query
import sqlite3
import random # !!! doar pentru dev testing

def get_elev_submissions(kn_user): #returneaza toate submisiile unui elev din db
    return "int main()"

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
    def __init__(self, nume, kn_user, id): #id = get_kn_id(kn_user)
        self.nume = nume
        #self.istoric_submisii = istoric_submisii -> asta o sa existe doar in baza de date si dam query pe kn_user, nu il tinem in memorie
        self.kn_user = kn_user
        self.id = id
        #self.id = random.randint(1, 100000) # !!! doar pentru dev testing

#class Submisie:
#    def __init__(self, content, id, user):
#        self.content = content
#        self.id = id
#        self.user = user

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
        
        db = TinyDB("db_clase.json")
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
                controls=[ButonAddElev(page = self._page, clasa=self.clasa, back_route=self.back_route)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self._page.update()

class ButonAddClasa(ft.Button):
    def __init__(self, page : ft.Page, back_route):
        super().__init__(content=ft.Text("Adaugă o clasă nouă", size=15, text_align=ft.TextAlign.CENTER),)
        
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
    

class ButonAddElev(ft.Button):
    def __init__(self, page : ft.Page, clasa, back_route):
        super().__init__(content=ft.Text("Adaugă un elev", size=15, text_align=ft.TextAlign.CENTER),)
        
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
        self.on_click = self.add_elev
        self.back_route = back_route
        self.clasa = clasa
    
    def add_elev(self, e):
        self._page.clean()
        self._page.title = "Adăugare elev"
        tb_nume = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100)
        tb_kn_user = ft.TextField(text_align=ft.TextAlign.CENTER, text_size=18, border_color=ft.Colors.BLUE_GREY_100)

        def push_elev_nou(e):
            return

        self._page.add(
            ButonBack(self.back_route),
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
                controls=[ButonAddClasa(page=self._page, back_route=self.loadPage)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

###de aici in jos mi am bagat eu mainile - mester


class Submisie:
    def __init__(
        self,
        id,
        time_stamp,
        content,
        problem_id,
        score,
        user_id,
        contest_id,
        wierd_percent
    ):
        self.id = id
        self.time_stamp = time_stamp
        self.content = content
        self.problem_id = problem_id
        self.score = score
        self.user_id = user_id
        self.contest_id = contest_id
        self.wierd_percent = wierd_percent


class Contest:
    def __init__(
        self,
        id,
        name,
        start_time,
        end_time,
        nume_clasa,
        nivel_clasa,
        lista_probleme,
        fetched
    ):
        self.id = id
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.nume_clasa = nume_clasa
        self.nivel_clasa = nivel_clasa
        self.lista_probleme = lista_probleme
        self.fetched = bool(fetched)