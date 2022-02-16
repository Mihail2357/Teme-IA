import time
import copy

ADANCIME_MAX = 2


class Joc:

    NR_COLOANE = 10
    JMIN = None
    JMAX = None
    GOL = "□"
    ARROW="↔"

    def __init__(self, tabla=None):  # Joc()
        if tabla is not None:
            self.matr = tabla
        else:
            self.matr = [[Joc.GOL for i in range(10)]for j in range(10)]
            self.matr[6][0]="alb"
            self.matr[9][3] = "alb"
            self.matr[9][6] = "alb"
            self.matr[6][9] = "alb"
            self.matr[0][3] = "negru"
            self.matr[0][6] = "negru"
            self.matr[3][9] = "negru"
            self.matr[3][0] = "negru"

        self.JMIN_position = [[6,0],[9,3],[9,6],[6,9]]   #lista care retine pozitiile pieselor jucatorului JMIN
        self.JMAX_position = [[0,3],[0,6],[3,9],[3,0]]      #lista care retine pozitiile pieselor jucatorului JMAX

    @classmethod
    def jucator_opus(cls, jucator):
        if jucator == cls.JMIN:
            return cls.JMAX
        else:
            return cls.JMIN

    def final(self,jucator): #daca jucatorul nu mai poate muta, pierde
        if jucator==self.JMIN:
            l=self.JMIN_position
        else:
            l=self.JMAX_position

        y=[-1,0,1]
        for x in l:
            for i in y:
                for j in y:
                    if self.matr[x[0]+i][x[1]+j]==self.GOL:
                        return False

        return self.jucator_opus(jucator)

    def nr_mutari_fara_sageata(self, jucator):  # numaram cate locuri libere are pe tabla un jucator
        if jucator == self.JMIN:
            l = self.JMIN_position
        else:
            l = self.JMAX_position
        nr_mutari=0
        y = [-1, 0, 1]
        for x in l:  # pentru fiecare piesa a jucatorului
            for i in y:  # pentru fiecare varianta de modificare a primei coordonate (ramane la fel, creste cu 1, scade cu 1)
                for j in y:  # pentru fiecare varianta de modificare a celei de a 2 a coordonate
                    linie = x[0] + i
                    coloana = x[1] + j
                    while linie < 10 and linie >= 0 and coloana < 10 and coloana >= 0 and self.matr[linie][coloana] == self.GOL:  # mergem pe o directie din casuta in casuta pana nu mai putem inainta
                        nr_mutari+=1
                        linie += i
                        coloana += j

        return nr_mutari

    def mutari_posibile(self,linie_initiala,coloana_initiala):  #similar cu def mutari(), generam toate mutarile posibile a unei singure piese
        l_mutari = []
        y = [-1, 0, 1]
        for i in y:
                for j in y:
                    linie=linie_initiala+i
                    coloana=coloana_initiala+j
                    while linie<10 and linie>=0 and coloana<10 and coloana>=0 and self.matr[linie][coloana]==self.GOL:
                        for m in y:
                            for n in y:
                                linie_sageata=linie+m
                                coloana_sageata=coloana+n
                                while (m!=0 or n!=0) and (linie_sageata!=linie or coloana_sageata!=coloana) and linie_sageata<10 and linie_sageata>=0 and coloana_sageata<10 and coloana_sageata>=0 and (self.matr[linie_sageata][coloana_sageata] == self.GOL or (linie_sageata==linie_initiala and coloana_sageata==coloana_initiala)):
                                    l_mutari.append([linie_initiala,coloana_initiala,linie,coloana,linie_sageata,coloana_sageata])
                                    linie_sageata+=m
                                    coloana_sageata+=n
                        linie+=i
                        coloana+=j

        return l_mutari

    def mutari(self, jucator):  # jucator = simbolul jucatorului care muta
        if jucator == self.JMIN:
            l = self.JMIN_position
        else:
            l = self.JMAX_position
        l_mutari = []
        y = [-1, 0, 1]
        for x in l:   #pentru fiecare piesa a jucatorului
            for i in y:  #pentru fiecare varianta de modificare a primei coordonate (ramane la fel, creste cu 1, scade cu 1)
                for j in y: #pentru fiecare varianta de modificare a celei de a 2 a coordonate
                    linie=x[0]+i
                    coloana=x[1]+j
                    while linie<10 and linie>=0 and coloana<10 and coloana>=0 and self.matr[linie][coloana]==self.GOL:  #mergem pe o directie din casuta in casuta pana nu mai putem inainta
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[x[0]][x[1]]=self.GOL
                        for m in y: #dupa ce am pus piesa, facem acelasi lucru si pentru sageata
                            for n in y:
                                linie_sageata=linie+m
                                coloana_sageata=coloana+n
                                while (m!=0 or n!=0) and (linie_sageata!=linie or coloana_sageata!=coloana) and linie_sageata<10 and linie_sageata>=0 and coloana_sageata<10 and coloana_sageata>=0 and (self.matr[linie_sageata][coloana_sageata] == self.GOL or (linie_sageata==x[0] and coloana_sageata==x[1])):
                                    copie_matr[linie_sageata][coloana_sageata]=self.ARROW
                                    l_mutari.append(Joc(copie_matr))
                                    linie_sageata+=m
                                    coloana_sageata+=n
                        linie+=i
                        coloana+=j

        return l_mutari


    def estimeaza_scor(self, adancime,jucator):
        t_final = self.final(jucator)
        if t_final == self.__class__.JMAX:
            return 99 + adancime
        elif t_final == self.__class__.JMIN:
            return -99 - adancime
        elif t_final == "remiza":
            return 0
        else:
            return len(self.mutari(jucator))-len(self.mutari(self.jucator_opus(jucator)))  #numarul de mutari posibile ale jucatorului-numarul de mutari posibile ale adversarului

    def estimeaza_scor2(self, adancime,jucator):
        t_final = self.final(jucator)
        if t_final == self.__class__.JMAX:
            return 99 + adancime
        elif t_final == self.__class__.JMIN:
            return -99 - adancime
        elif t_final == "remiza":
            return 0
        else:
            return self.nr_mutari_fara_sageata(jucator)-self.nr_mutari_fara_sageata(self.jucator_opus(jucator))

    def __str__(self):
        sir = "  |"
        for i in range(self.NR_COLOANE):
            sir += str(i) + " "
        sir += "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        for i in range(self.NR_COLOANE):  # itereaza prin linii
            sir += (
                    str(i)
                    + " |"
                    + " ".join([self.caracter(x) for x in self.matr[i]])
                    + "\n"
            )
        return sir

    def caracter(self,x):
        if x=="alb":
            return '●'
        elif x=="negru":
            return '○'
        else:
            return str(x)

class Stare:

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, estimare=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # estimarea favorabilitatii starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.estimare = estimare

        # lista de mutari posibile (tot de tip Stare) din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        # e de tip Stare (cel mai bun succesor)
        self.stare_aleasa = None

    def mutari(self):
        # lista de informatii din nodurile succesoare
        l_mutari = self.tabla_joc.mutari(self.j_curent)

        juc_opus = Joc.jucator_opus(self.j_curent)

        # mai jos calculam lista de noduri-fii (succesori)
        l_stari_mutari = [
            Stare(mutare, juc_opus, self.adancime - 1, parinte=self)
            for mutare in l_mutari
        ]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir


""" Algoritmul MinMax """


def min_max(stare):

    # daca sunt la o frunza in arborele minimax sau la o stare finala
    if stare.adancime == 0 or stare.tabla_joc.final(stare.j_curent):
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime,stare.j_curent)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutariCuEstimare = [
        min_max(x) for x in stare.mutari_posibile
    ]  # expandez(constr subarb) fiecare nod x din mutari posibile

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu estimarea maxima
        stare.stare_aleasa = max(mutariCuEstimare, key=lambda x: x.estimare)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu estimarea minima
        stare.stare_aleasa = min(mutariCuEstimare, key=lambda x: x.estimare)

    stare.estimare = stare.stare_aleasa.estimare
    return stare


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        estimare_curenta = float("-inf")

        for mutare in stare.mutari_posibile:
            # calculeaza estimarea pentru starea noua, realizand subarborele
            stare_noua = alpha_beta(
                alpha, beta, mutare
            )  # aici construim subarborele pentru stare_noua

            if estimare_curenta < stare_noua.estimare:
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if alpha < stare_noua.estimare:
                alpha = stare_noua.estimare
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        estimare_curenta = float("inf")
        # completati cu rationament similar pe cazul stare.j_curent==Joc.JMAX
        for mutare in stare.mutari_posibile:
            # calculeaza estimarea
            stare_noua = alpha_beta(
                alpha, beta, mutare
            )  # aici construim subarborele pentru stare_noua

            if estimare_curenta > stare_noua.estimare:
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if beta > stare_noua.estimare:
                beta = stare_noua.estimare
                if alpha >= beta:
                    break

    stare.estimare = stare.stare_aleasa.estimare

    return stare


def afis_daca_final(stare_curenta):
    # metoda final() returneaza castigatorul ("alb" sau "negru") sau False daca nu e stare finala
    final = stare_curenta.tabla_joc.final(stare_curenta.j_curent)
    if final:
        print("A castigat " + final)
        return True

    return False


def main():
    # initializare algoritm
    raspuns_valid = False

    while not raspuns_valid:
        tip_algoritm = input(
            "Algoritmul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-beta\n "
        )
        if tip_algoritm in ["1", "2"]:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")
    # initializare jucatori
    raspuns_valid = False
    while not raspuns_valid:
        Joc.JMIN = input("Doriti sa jucati cu negru sau cu alb? ").lower()
        if Joc.JMIN in ["alb", "negru"]:
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie alb sau negru.")
    Joc.JMAX = "alb" if Joc.JMIN == "negru" else "negru"
    # expresie= val_true if conditie else val_false  (conditie? val_true: val_false)

    # initializare tabla
    tabla_curenta = Joc()
    print(tabla_curenta.JMIN_position)
    # apelam constructorul
    print("Tabla initiala")
    print(str(tabla_curenta))

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, "alb", ADANCIME_MAX)
    while True:
        if stare_curenta.j_curent == Joc.JMIN:
            # muta jucatorul
            print("Acum muta utilizatorul cu simbolul", stare_curenta.j_curent)
            raspuns_valid = False
            while not raspuns_valid:
                try:
                    linie_initiala = int(input("linie initiala="))
                    coloana_initiala = int(input("coloana initiala="))
                    linie = int(input("linie ="))
                    coloana = int(input("coloana ="))
                    linie_sageata = int(input("linie sageata="))
                    coloana_sageata = int(input("coloana sageata="))
                    if tabla_curenta.matr[linie_initiala][coloana_initiala]==Joc.JMIN and ([linie_initiala,coloana_initiala,linie,coloana,linie_sageata,coloana_sageata] in tabla_curenta.mutari_posibile(linie_initiala,coloana_initiala)):
                            raspuns_valid = True  #verificam daca si a ales o piesa valida si verificam daca se poate muta piesa respectiva in coordonatele cerute precum si sageata

                    else:
                        print("mutare invalida")

                except ValueError:
                    print("Linia si coloana trebuie sa fie numere intregi")

            # dupa iesirea din while sigur am valide atat linia cat si coloana
            # deci pot plasa simbolul pe "tabla de joc"

            stare_curenta.tabla_joc.matr[linie][coloana] = Joc.JMIN   #mutam piesa specificata in locul specificat
            stare_curenta.tabla_joc.matr[linie_initiala][coloana_initiala] = Joc.GOL  #vechea pozitie va fi libera
            stare_curenta.tabla_joc.matr[linie_sageata][coloana_sageata] = Joc.ARROW  #puem sageata in locul specificat
            for i in range(4):
                if tabla_curenta.JMIN_position[i]==[linie_initiala,coloana_initiala]:  #actualizam pozitia piesei mutate in lista cu pozitiile pieselor jucatorului
                    tabla_curenta.JMIN_position[i]=[linie,coloana]

            # afisarea starii jocului in urma mutarii utilizatorului
            print("\nTabla dupa mutarea jucatorului")
            print(str(stare_curenta))
            # testez daca jocul a ajuns intr-o stare finala
            # si afisez un mesaj corespunzator in caz ca da
            if afis_daca_final(stare_curenta):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
        # --------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator

            print("Acum muta calculatorul cu simbolul", stare_curenta.j_curent)
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))
            # stare actualizata e starea mea curenta in care am setat stare_aleasa (mutarea urmatoare)
            if tip_algoritm == "1":
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm==2
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)

            # aici se face de fapt mutarea !!!
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc

            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            print(
                'Calculatorul a "gandit" timp de '
                + str(t_dupa - t_inainte)
                + " milisecunde."
            )
            if afis_daca_final(stare_curenta):
                break

            # S-a realizat o mutare.  jucatorul cu cel opus
            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)


if __name__ == "__main__":
    main()
