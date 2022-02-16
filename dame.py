from enum import IntEnum  # Enumerații -> int (Ex: codez cele 2 culori)
from collections import namedtuple  # pt Mutare
from copy import deepcopy
import time
from math import inf

# Definim Tuplu pentru o Mutare
Move = namedtuple('Move', ('jucator', 'pozitie_initiala', 'pozitie_finala'))


# Se ocupă de toate aspectele legate de afișare tablă, mutări etc
class afisare:

    # Afișare Tablă Curentă
    def afis_configuratie(self, configuratie):
        afisare_tabla(configuratie.tabla)

    # Ia mutarea introdusă și o verifică -> adaugă sau nu (funcția e doar pt om, nu pt pc)
    # Primește mutările posibile ca să poată vedea dacă jucătorul poate muta într-o anumită poziție
    def mutare(self, configuratie, jucator, mutari_posibile):

        start = time.time()

        while True:

            print("Introdu Coordonate piesă și coordonate mutare (x1 y1 x2 y2).")
            print("Scrie exit dacă vrei să abandonezi.")

            linie = input()

            if linie == 'exit':
                return None

            try:
                linie1, coloana1, linie2, coloana2 = map(int,
                                                         linie.split())  # map aplică funcția "int" pt fiecare dintre elementele mele -> verific să nu fie litere sau numere cu zecimale sau ceva
            except ValueError:
                print("Coordonate Invalide! Încearcă din Nou! (Nu sunt numere de la 0-7)\n")
                continue

            pozitie1 = (linie1, coloana1)
            pozitie2 = (linie2, coloana2)

            mutare = Move(jucator, pozitie1, pozitie2)

            if mutare not in mutari_posibile:
                print("Mutare Invalidă! Încearcă din Nou!\n")
                continue

            end_time = time.time()
            print("Jucătorul s-a gândit: %s secunde." % (end_time - start))

            return mutare


# Afișare Generală Tablă (Numerele)
def afisare_tabla(tabla):
    print(" ", ' '.join(str(i) for i in range(8)))

    for i, linie in enumerate(tabla):
        print(i, ' '.join(str(piesa) for piesa in linie))


"--------------------------------------------------------------"
"Clase pt Joc"


# Clasă Jucător (Enumerare)
class Jucator(IntEnum):
    NEGRU = 1
    ALB = 2

    # Întoarce culoarea opusă față de cea aleasă de jucător
    def culoare_reversed(self):
        if self == self.NEGRU:
            return self.ALB
        return self.NEGRU

    # Rădăcina este MAX. Întotdeauna, jocul va începe cu NEGRU. Întorc True dacă jucătorul a ales NEGRU
    def este_negru(self):
        return self == self.NEGRU


# Clasă Piesă (ce piese avem pe tablă, nimic, piese normale, piese care devin regi)
class Piesa(IntEnum):
    GOL = 0
    NEGRU = 1
    ALB = 2
    REGE_NEGRU = 3
    REGE_ALB = 4

    # Afișare piese codate
    def __str__(self):
        if self == self.NEGRU:
            return '●'
        if self == self.ALB:
            return '○'
        if self == self.REGE_NEGRU:
            return 'N'
        if self == self.REGE_ALB:
            return 'A'
        # Celula Goală
        return ' '

    # întoarce cine deține piesa -> gen jucătorul care a ales negru
    def player(self):
        if self == self.NEGRU or self == self.REGE_NEGRU:
            return Jucator.NEGRU
        return Jucator.ALB

    # Dacă piesa e rege sau nu
    def e_rege(self):
        if self == self.REGE_NEGRU or self == self.REGE_ALB:
            return True
        return False


"--------------------------------------------------------------"
"Clasa pentru Starea Jocului"


class Stare_Joc:

    def __init__(self, tabla):
        self.tabla = tabla
        self.lant = False  # True daca jucătorul poate să captureze mai multe piese, gen când are voie să facă mai multe mutări consecutive pt că e un lanț conitnuu
        self.piesa_lant = None  # piesă care face parte din lanț, la care am ajuns

    # Cum arată tabla inițial  ---> Generare Stare Inițială Tablă
    def initial():

        # Mai întâi, o tablă goală
        tabla = []
        for i in range(8):
            linie = []
            for j in range(8):
                linie.append(Piesa.GOL)
            tabla.append(linie)

        # apoi adaug piesele (damele pe poziții) !!!! doar pe diagonala cu negru
        for linie in range(3):
            for coloana in range((linie + 1) % 2, 8,
                                 2):  # deci coloană între 0/1 și 7, și pe toate pozițiile din 2 în 2
                tabla[linie][coloana] = Piesa.ALB

            for coloana in range(linie % 2, 8, 2):
                tabla[7 - linie][coloana] = Piesa.NEGRU

        return Stare_Joc(tabla)

    # Întoarce o listă ce conține toate pozițiile tuturor pieselor unui jucător
    def lista_pozitii_piese_jucator(self, jucator):
        lista = []

        for linie, sir in enumerate(self.tabla):
            for coloana, piesa in enumerate(sir):
                # Dacă piesa nu e goală (adică am o piesă în acea poziție) și dacă e de culoarea jucătorului
                if piesa != Piesa.GOL and piesa.player() == jucator:
                    lista.append([linie, coloana])

        return lista

    # Numărul de Piese care aparțin unui jucător
    def nr_piese(self, jucator):
        suma = 0
        for i in self.lista_pozitii_piese_jucator(jucator):
            suma += 1

        return suma

    # O lista cu toate mutările posibile ale unei piese (ale unui jucător)
    # Le vom cataloga ca mișcări simple si mișcări care obțin capturarea pieselor unui oponent
    def mutari_posibile_piesa(self, jucator, linie, coloana):

        piesa = self.tabla[linie][coloana]
        pozitie_curenta = (linie, coloana)
        jucator_opus = jucator.culoare_reversed()

        # Definim cum se poate mișca piesa: regele se poate mișca înainte și înapoi; restul pieselor doar în față (dar e relativ la tipul de culoare)
        if piesa.e_rege():
            miscari_permise = (-1, 1)
        else:
            # Alb crește linia
            if jucator == Jucator.ALB:
                miscari_permise = (1,)
            else:
                # Negru scade linia
                miscari_permise = (-1,)

        # Mișcările care găsesc celule goale
        miscari_simple = []
        # Mișcări care găsesc piese ale oponentului
        miscari_puncte = []

        for mutare in miscari_permise:
            linie_noua = linie + mutare

            # Dacă avem loc pe tablă
            if not (0 <= linie_noua <= 7):
                continue

            for coloane_posibile in (-1, 1):
                coloana_noua = coloana + coloane_posibile

                # Dacă avem loc pe tablă
                if not (0 <= coloana_noua <= 7):
                    continue

                pozitie_noua = (linie_noua, coloana_noua)
                piesa_poz_noua = self.tabla[linie_noua][coloana_noua]

                # Dacă avem celulă goală
                if piesa_poz_noua == Piesa.GOL:
                    miscari_simple.append(Move(jucator, pozitie_curenta, pozitie_noua))

                # Dacă capturăm piese oponent
                # Trebuie după să verificăm dacă putem să sărim peste piesa oponentului si să găsim o celulă goală, altfel nu merge
                elif piesa_poz_noua.player() == jucator_opus:
                    linie_oponent = linie_noua + mutare
                    coloana_oponent = coloana_noua + coloane_posibile
                    pozitie_dupa_captura = (linie_oponent, coloana_oponent)

                    # să nu depășim limitele tablei și celula să fie goală
                    if (0 <= linie_oponent <= 7 and 0 <= coloana_oponent <= 7):
                        aux = self.tabla[linie_oponent][coloana_oponent]
                        if aux == Piesa.GOL:
                            miscari_puncte.append(Move(jucator, pozitie_curenta, pozitie_dupa_captura))

        return miscari_simple, miscari_puncte

    # Modificăm tabla de joc după ce facem o anumită mutare  ---> obținem o nouă configurație a tablei de joc
    def modificare_dupa_mutare(self, mutare):

        jucator, (linie1, coloana1), (linie2, coloana2) = mutare

        # Facem o copie a tablei inițiale
        copie_tabla = deepcopy(self.tabla)

        # Mutăm piesa în copie_tabla
        copie_tabla[linie2][coloana2] = self.tabla[linie1][coloana1]
        copie_tabla[linie1][coloana1] = Piesa.GOL

        # Facem verificăm să vedem dacă piesele au devenit regi
        if jucator == Jucator.NEGRU and linie2 == 0:
            copie_tabla[linie2][coloana2] = Piesa.REGE_NEGRU
        if jucator == Jucator.ALB and linie2 == 7:
            copie_tabla[linie2][coloana2] = Piesa.REGE_ALB

        # Mutarea compusă (adică am prins o piesă a oponentului) va obține distanța dintre cele 2 coloane mai mare decât 1
        if abs(coloana2 - coloana1) > 1:
            mutare = True
        else:
            mutare = False

        # Dacă avem mutare_compusă (adică am sărit peste piesa oponentului), tb să ștergem piesa oponentului
        if mutare:
            linie = (linie1 + linie2) // 2  # // -> diviziune fără rest
            coloana = (coloana1 + coloana2) // 2
            copie_tabla[linie][coloana] = Piesa.GOL

        configuratie_noua = Stare_Joc(copie_tabla)

        # Dacă este posibil să obținem mai multe capturi de piese, marcăm că avem un lanț
        if mutare:
            miscari_simple, miscari_puncte = configuratie_noua.mutari_posibile_piesa(jucator, linie2, coloana2)
            # Dacă găsim alte mișcări care să aducă puncte (capturare de piese oponent)
            if miscari_puncte:
                configuratie_noua.lant = True
                configuratie_noua.piesa_lant = (linie2, coloana2)

        return configuratie_noua

    # Toate mutările posibile ale unui jucător (cu toate piesele pe care le are)
    def mutari_posibile_jucator(self, jucator):
        # Dacă avem posibilitatea de a captura mai multe piese într-o singură mutare (self.lant == True) -> miscari_puncte ne trebuie selectate doar
        if self.lant == True:
            linie, coloana = self.piesa_lant  # Începem de la prima piesă a lanțului
            miscari_simple, miscari_puncte = self.mutari_posibile_piesa(jucator, linie, coloana)
            return miscari_puncte

        mutari = []

        # Selectăm toate piesele jucătorului și facem toate mutările posibile dacă nu avem lanț
        for linie, coloana in self.lista_pozitii_piese_jucator(jucator):
            miscari_simple, miscari_puncte = self.mutari_posibile_piesa(jucator, linie, coloana)
            mutari += miscari_simple
            mutari += miscari_puncte

        return mutari

    def configuratii_viitoare(self, jucator):
        mutari_posibile = self.mutari_posibile_jucator(jucator)

        # Întoarcem toate configurațiile de tablă posibile
        configuratii = []
        for mutare in mutari_posibile:
            configuratii.append(self.modificare_dupa_mutare(mutare))

        return configuratii

    # Funcțiile de Scor
    def scor(self):
        regi_negri = 0
        regi_albi = 0
        piese_negre = 0
        piese_albe = 0

        for linie, coloana in self.lista_pozitii_piese_jucator(Jucator.NEGRU):
            piece = self.tabla[linie][coloana]
            if piece.e_rege():
                regi_negri += 1
            else:
                piese_negre += 1

        for linie, coloana in self.lista_pozitii_piese_jucator(Jucator.ALB):
            piece = self.tabla[linie][coloana]
            if piece.e_rege():
                regi_albi += 1
            else:
                piese_albe += 1

        return (3 * regi_negri + piese_negre) - (3 * regi_albi + piese_albe)

    def scor1(self):
        return self.nr_piese(Jucator.NEGRU) - self.nr_piese(Jucator.ALB)


"--------------------------------------------------------------"
"Funcțiile Minimax, Alpha-Beta și funcția principală care alege cea mai bună mutare"


# Găsește cea mai bună mutare pentru calculator pornind de la o configurație dată
def mutare_best(config, jucator, adancime_max, retezare):
    # Am generat toate configuratiile posibile
    configuratii_viitoare = config.configuratii_viitoare(jucator)

    # Ce algoritm trebuie aplicat (variabila "retezare" am reținut dacă minimax sau nu)
    if retezare == True:
        algoritm = alpha_beta
    else:
        algoritm = minimax

    # omul joacă cu cealaltă culoare
    adversar = jucator.culoare_reversed()

    # dicționar pt scoruri ca să selectăm mutarea cu cel mai bun scor
    scoruri = {}

    # Pentru fiecare mutare posibilă, stabilim un scor
    for configuratie in configuratii_viitoare:
        # Dacă avem mutări consecutive posibile, le facem pe toate
        if configuratie.lant:
            mutare_urmatoare = jucator
        # Altfel pasăm omului mutarea
        else:
            mutare_urmatoare = adversar

        # Aici se decide scorul unei configurații
        scor = algoritm(configuratie, mutare_urmatoare, adancime_max)
        # Adaug la dicționarul cu toate scorurile
        scoruri[configuratie] = scor

    # JMAX, JMIN ---> negru mereu începe jocul, deci mereu max; alb mereu min
    if jucator.este_negru():
        optimum_func = max
    else:
        optimum_func = min

    # întoarcem scorul optim dintre toate scorurile configurațiilor obținute
    return optimum_func(configuratii_viitoare, key=lambda x: scoruri[x])


# Algoritmul Minimax
def minimax(configuratie, jucator, adancime):
    # Dacă am epuizat adâncimea arborelui (nu ai cum să ajungi în stare finală tablă aici -> toate verificările se fac în main)
    if adancime == 0:
        return configuratie.scor()  # mie îmi tb scorul, nu configurația tablei (configurația o întorc în funcția mutare_best)

    # Generez toate configurațiile posibile
    configuratii_viitoare = configuratie.configuratii_viitoare(jucator)

    adversar = jucator.culoare_reversed()

    # Scor inițial
    if jucator.este_negru():
        scor = -inf
    else:
        scor = +inf

    # Calculăm scorurile
    for configuratie in configuratii_viitoare:
        # Dacă avem lanț, luăm toate mutările posibile ---> mai avantajos
        if configuratie.lant:
            mutare_urmatoare = jucator
        else:
            mutare_urmatoare = adversar

        urmatorul_scor = minimax(configuratie, mutare_urmatoare, adancime - 1)

        if jucator.este_negru():
            scor = max(scor, urmatorul_scor)
        else:
            scor = min(scor, urmatorul_scor)

    return scor


# Algoritmul Alpha-Beta
def alpha_beta(configuratie, jucator, adancime, alpha=-inf, beta=+inf):
    # Dacă am epuizat adâncimea arborelui (nu ai cum să ajungi în stare finală tablă aici -> toate verificările se fac în main)
    if adancime == 0:
        return configuratie.scor()  # mie îmi tb scorul, nu configurația tablei (configurația o întorc în funcția mutare_best)

    # Generez toate configurațiile posibile
    configuratii_viitoare = configuratie.configuratii_viitoare(jucator)

    adversar = jucator.culoare_reversed()

    # Scor inițial
    if jucator.este_negru():
        scor = -inf
    else:
        scor = +inf

    for configuratie in configuratii_viitoare:
        # Dacă avem lanț, luăm toate mutările posibile ---> mai avantajos
        if configuratie.lant:
            mutare_urmator = jucator
        else:
            mutare_urmator = adversar

        urmatorul_scor = alpha_beta(configuratie, mutare_urmator, adancime - 1, alpha, beta)

        if jucator.este_negru():
            scor = max(scor, urmatorul_scor)
            alpha = max(alpha, scor)
        else:
            scor = min(scor, urmatorul_scor)
            beta = min(beta, scor)

        if alpha >= beta:
            break

    return scor


"--------------------------------------------------------------"
"Main"

if __name__ == '__main__':

    # --------------------------------------------------------------------------
    # Întrebările Preliminatorii

    # Alegere Dificultate
    adancime_max = None
    while adancime_max is None:
        print("Alege Nivelul de Dificultate: ")
        print("1. Ușor\n2. Mediu\n3. Greu\n")

        alegere = int(input())

        if alegere == 1:
            adancime_max = 1
        else:
            if alegere == 2:
                adancime_max = 3
            else:
                if alegere == 3:
                    adancime_max = 7
                else:
                    print("Alegere Invalidă! Introdu din nou!\n")

    # Alegere Algoritm
    retezare = None
    while retezare is None:
        print("\nAlege Algoritmul:")
        print("1. Minimax\n2. Alpha-Beta Pruning\n")

        alegere = int(input())

        if alegere == 1:
            retezare = False
        else:
            if alegere == 2:
                retezare = True
            else:
                print("Alegere Invalidă! Introdu din nou!\n")

    # Alegere Culoare Piese de Joc
    jucator_om = None
    while jucator_om is None:
        print("\nAlege Culoarea:")
        print("1. Negru\n2. Alb\n")

        alegere = int(input())

        if alegere == 1:
            jucator_om = Jucator.NEGRU
        else:
            if alegere == 2:
                jucator_om = Jucator.ALB
            else:
                print("Alegere Invalidă! Introdu din nou!\n")

    jucator_pc = jucator_om.culoare_reversed()

    print("\nAți ales: ", jucator_om)
    print("Computerul joaca cu: ", jucator_pc)

    # --------------------------------------------------------------------------

    interfata = afisare()

    # Joc Propriu-zis
    castigator = None
    # Generare Stare Inițială Joc
    configuratie_curenta = Stare_Joc.initial()  # a tablei de joc
    jucator_curent = Jucator.NEGRU  # ca să determinăm ce mutări trebuie să generăm și al cui e rândul

    nr_mutari = 0
    start_time = time.time()

    while True:
        nr_mutari += 1

        print("\nScor NEGRU:", configuratie_curenta.scor())
        print("Scor ALB:", (-1) * configuratie_curenta.scor())
        interfata.afis_configuratie(configuratie_curenta)

        # Verific stările finale part 1
        if configuratie_curenta.nr_piese(jucator_pc) == 0:
            castigator = jucator_om
            break

        if configuratie_curenta.nr_piese(jucator_om) == 0:
            castigator = jucator_pc
            break

        mutari_posibile = configuratie_curenta.mutari_posibile_jucator(jucator_curent)

        # Verific stările finale part 2
        if not mutari_posibile:
            # castigator ramane None -> remiză
            break

        # Mutare Om
        if jucator_curent == jucator_om:
            mutare = interfata.mutare(configuratie_curenta, jucator_curent, mutari_posibile)

            # pt Exit
            if mutare is None:
                break

            configuratie_curenta = configuratie_curenta.modificare_dupa_mutare(mutare)
        # Mutare PC
        else:
            print("\nComputerul se gândește...")

            start = time.time()
            configuratie_curenta = mutare_best(configuratie_curenta, jucator_pc, adancime_max, retezare)
            end_time = time.time()

            print("Calculatorul s-a gândit: %s secunde." % (end_time - start))

        # Verificăm dacă cumva jucătorul curent poate să facă mai multe mutări consecutive (pt că poate să mai captureze din piesele oponentului)  ---> va fi rândul lui și mutarea următoare
        # Altfel, e rândul celuilalt jucător
        if not configuratie_curenta.lant:
            jucator_curent = jucator_curent.culoare_reversed()

    if castigator is None:
        print("\nRemiză\n")
    else:
        print("\n Câștigător: ", castigator)

    print("\nScor NEGRU:", configuratie_curenta.scor())
    print("Scor ALB:", (-1) * configuratie_curenta.scor())

    print("\nJocul s-a terminat după: %s mutări." % str(nr_mutari))
    print("Jocul s-a terminat după: %s secunde." % (time.time() - start_time))