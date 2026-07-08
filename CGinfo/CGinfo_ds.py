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

    def to_dict(self):
        return {
            "nume" : self.nume,
            "kn_user" : self.kn_user,
            "id" : self.id
        }

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
        weird_percent
    ):
        self.id = id
        self.time_stamp = time_stamp
        self.content = content
        self.problem_id = problem_id
        self.score = score
        self.user_id = user_id
        self.contest_id = contest_id
        self.weird_percent = weird_percent


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