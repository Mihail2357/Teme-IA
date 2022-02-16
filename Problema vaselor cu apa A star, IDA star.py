import copy
import math
import os
import time

import stopit



class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0, info2=[0]*4):
        self.info = info
        self.parinte = parinte
        self.g = cost
        self.h = h
        self.f = self.g + self.h
        self.info2= info2  #pentru afisarea mesajului  "Din vasul  xxxxx  s-au turnat  xx  litri de apa de culoare  rosu  in vasul  xx"

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=True, afisLung=True):
        l = self.obtineDrum()
        index=0
        g.write("Solutie:")
        g.write('\n')
        for nod in l:
            index+=1
            g.write(str(index)+".")  #numărul de ordine al fiecărui nod din drum
            g.write('\n')
            if(nod.info2[2]!=0):
                g.write("Din vasul "+str(nod.info2[0])+ " s-au turnat "+str(nod.info2[2])+" litri de apa de culoare "+str(nod.info2[3])+" in vasul "+str(nod.info2[1]))
                g.write('\n')
            for i in range(len(nod.info)):
                g.write(str(i)+" : "+str(nod.info[i][0])+" "+str(nod.info[i][1])+" "+str(nod.info[i][2]))
                g.write('\n')
            g.write('\n'*2)
        if afisCost:
            g.write("Cost: "+str(self.g)+'\n')
        if afisLung:
            g.write("Lungime: "+ str(len(l)))

        g.write('\n' * 2)
        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return sir


class Graph:
    def __init__(self, nume_fisier):
        f = open(nume_fisier, "r")
        continut_fisier = f.read()

        siruriculori = continut_fisier.split("---")
        self.dict = {}
        for x in siruriculori[0].split('\n')[0:-1]:
            y = x.split()
            self.dict[(y[0], y[1])] = y[2]
            self.dict[(y[1], y[0])] = y[2]

        listapreturi = siruriculori[1].strip().split("stare_initiala")
        self.preturi = {}
        for x in listapreturi[0].strip().split('\n'):
            y = x.split()
            y[1] = int(y[1])
            self.preturi[y[0]]=y[1]

        siruristareinitiala = listapreturi[1].strip().split("stare_finala")
        self.start = []
        for x in siruristareinitiala[0].strip().split('\n'):
            y = x.split()
            y[0] = int(y[0])
            y[1] = int(y[1])
            if (len(y) == 2):
                y.append("gol")
                self.start.append(y)
            else:
                self.start.append(y)

        self.scopuri = []
        for x in siruristareinitiala[1].strip().split('\n'):
            y = x.split()
            y[0] = int(y[0])
            self.scopuri.append(y)


    def testeaza_scop(self, nodCurent):
        k=0
        for x in self.scopuri:  #pentru fiecare culoare si cantitate din scop cautam in starea initiala sa vedem daca exista in vreun vas
            for y in nodCurent.info:
                if x==y[1:]:
                    k+=1
                    break
        if k==len(self.scopuri):
            return 1  #daca toate culorile din scop sunt in starea initiala in cantitatile dorite, atunci e stare finala

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica_banala"):
        listaSuccesori = []
        vase_c = nodCurent.info  # stivele din nodul curent
        nr_vase = len(vase_c)

        for x in range(nr_vase):#pentru fiecare 2 vase distincte, turnam unul in altul daca se poate
            for y in range(nr_vase):

                if(x!=y and vase_c[x][1]!=0 and vase_c[y][1]!=vase_c[y][0]):
                    copie1=copy.deepcopy(vase_c)
                    vas1=vase_c[x][1]   #cantitatea de culoare din vasul din care se toarna
                    vas2=vase_c[y][0] - vase_c[y][1]  #capacitatea ramasa a vasului in care se toarna

                    if(vas1>vas2):
                        copie1[y][1]=copie1[y][0]
                        copie1[x][1] -=vas2
                        culoare_turnata=vas2

                    elif vas1<vas2:
                        copie1[x][1]=0
                        copie1[y][1]+=vas1
                        culoare_turnata = vas1
                        copie1[x][2] = "gol"

                    elif vas1==vas2:
                        copie1[x][1] = 0
                        copie1[x][2] = "gol"
                        copie1[y][1] += vas1
                        culoare_turnata = vas2

                    if (vase_c[x][2], vase_c[y][2]) in self.dict.keys():
                        copie1[y][2] = self.dict[(vase_c[x][2], vase_c[y][2])]
                        cost = culoare_turnata * self.preturi[vase_c[x][2]]  #daca cele 2 culori dau o culoare cunoscuta

                    elif vase_c[x][2] == "necunoscut" or vase_c[y][2]=="necunoscut": #daca avem culoare necunoscuta in cel putin un vas
                        if vase_c[x][2] == "necunoscut" and vase_c[y][2]!="necunoscut": #in primul
                            cost = vase_c[x][1]

                        elif vase_c[x][2] != "necunoscut" and vase_c[y][2]=="necunoscut": #in al doilea
                            cost = vase_c[y][1]

                        else: #in ambele
                            cost = vase_c[y][1]+vase_c[x][1]

                        copie1[y][2] = "necunoscut"

                    elif vase_c[y][1]==0:   #daca vasul 2 este gol si primul vas are culoare cunoscuta
                        cost = culoare_turnata * self.preturi[vase_c[x][2]]
                        copie1[y][2] = vase_c[x][2]

                    else:
                        cost = culoare_turnata * self.preturi[vase_c[x][2]] + vase_c[y][1] * self.preturi[vase_c[y][2]]   #daca rezultatul este culoare nedefinita
                        copie1[y][2] = "necunoscut"

                    info2=[x,y,culoare_turnata,vase_c[x][2]]
                    nod_nou = NodParcurgere(copie1,nodCurent,cost=nodCurent.g + cost,h=self.calculeaza_h(copie1, tip_euristica),info2=info2)


                    if not nodCurent.contineInDrum(copie1):
                        listaSuccesori.append(nod_nou)

        return listaSuccesori




    def calculeaza_h(self, infoNod, tip_euristica):
        if tip_euristica == "euristica_banala":
            return self.euristica_banala(infoNod, tip_euristica)
        elif tip_euristica == "euristica_admisibila_1":
            return self.euristica_admisibila_1(infoNod, tip_euristica)
        elif tip_euristica == "euristica_admisibila_2":
            return self.euristica_admisibila_2(infoNod, tip_euristica)
        elif tip_euristica == "euristica_neadmisibila":
            return self.euristica_neadmisibila(infoNod, tip_euristica)
        else:
            raise Exception("Aceasta euristica nu este definita")

    def euristica_banala(self, infoNod, tip_euristica):
        k = 0
        for x in self.scopuri:
            for y in infoNod:
                if x == y[1:]:
                    k += 1
                    break
        if k == len(self.scopuri):
            return 0
        else:
            return 1


    def euristica_admisibila_1(self, infoNod, tip_euristica):
        cost = 0
        #pentru fiecare scop cautam cata cantitate din culoarea respectiva avem deja
        for x in self.scopuri:
            cantitate = 0
            cantiatedoarunvas=0
            for y in infoNod:
                if y[2] == x[1]:
                    if y[1]>=x[0] and cantiatedoarunvas>y[1]:
                        cantitatedoarunvas=y[1]

                    cantitate += y[1]

            if cantiatedoarunvas!=0:   #daca am gasit-o pe toata intr un singur vas ramanem doar cu cantitatea din acel vas
                cantitate=cantiatedoarunvas

            if cantitate > x[0]:
                cost += (cantitate - x[0]) * self.preturi[x[1]]   #daca avem mai multa decat este nevoie, costul minim este costul de a turna surplusul

            elif cantitate < x[0]:  #daca avem mai putina, cautam sa facem cantitatea care ne lipseste
                ok = 0
                for combinatie in self.dict:
                    if self.dict[combinatie] == x[1]:
                        ok = 1
                        cost += min(self.preturi[combinatie[0]], self.preturi[combinatie[1]])  #daca gasim combinatia pentru culoarea cautata, costul minim este costul minim dintre culorile din combinatie
                        cost+=min((x[0] - cantitate),cantitate)*self.preturi[x[1]]      #plus costul de a turna in vas culoarea nou formata

                if ok == 0:    #daca nu avem destula culoare si nici nu se poate forma din combinatia a 2 culori, atunci este imposibil sa ajungem in starea finala
                    return float('inf')

        return cost


    def euristica_neadmisibila(self, infoNod, tip_euristica):
        cost=0
        for x in self.scopuri:
            cantitate=0
            cantiatedoarunvas=0
            for y in infoNod:
                if y[2]==x[1]:
                    if y[2] == x[1]:
                        if y[1] >= x[0] and cantiatedoarunvas > y[1]:
                            cantitatedoarunvas = y[1]
                    cantitate+=y[1]

            if cantiatedoarunvas!=0:
                cantitate=cantiatedoarunvas

            if cantitate>x[0]:
                cost+=(cantitate-x[0])*self.preturi[x[1]]
                return cost

            elif cantitate<x[0]:
                ok=0
                for combinatie in self.dict:
                    if self.dict[combinatie]==x[1]:
                        ok+=1
                        cantitate_culoare_1 = 0
                        cantitate_culoare_2 = 0

                        for y in infoNod:
                            if y[2] == combinatie[0]:
                                cantitate_culoare_1 += y[1]

                        for y in infoNod:
                            if y[2] == combinatie[1]:
                                cantitate_culoare_2 += y[1]

                        cost += (x[0] - cantitate)/2 * min(self.preturi[combinatie[0]], self.preturi[combinatie[1]])
                        cost+=min((x[0] - cantitate),cantitate)*self.preturi[x[1]]

                        if cantitate_culoare_1 + cantitate_culoare_2 >= x[0] - cantitate:
                            break

                        if cantitate_culoare_1+cantitate_culoare_2 < x[0]-cantitate:      #daca nu avem destula cantitate de vopsea pentru a forma restul de culoare scop
                            for combinatie_culoare_1 in self.dict: #vedem daca se poate obtine prima culoare din combinatie din alte 2 culori
                                if self.dict[combinatie_culoare_1] == combinatie[0]:
                                    ok+=1
                                    pret_minim_1=min(self.preturi[combinatie_culoare_1[0]], self.preturi[combinatie_culoare_1[1]])

                            for combinatie_culoare_2 in self.dict:#vedem daca se poate obtine a doua culoare din combinatie din alte 2 culori
                                if self.dict[combinatie_culoare_2] == combinatie[1]:
                                    ok+=2
                                    pret_minim_2= min(self.preturi[combinatie_culoare_2[0]],
                                                     self.preturi[combinatie_culoare_2[1]])


                            if ok==1:  #daca nu se poate obtine nici macar una din cele 2 culori din combinatia pentru culoarea scop, atunci nu putem ajunge in starea scop
                                return float('inf')

                            elif ok==2: #daca se poate doar o culoare din cele 2, obtinem cantitatea ramasa din ea
                                cost+= (x[0] - cantitate-(cantitate_culoare_1 + cantitate_culoare_2))/2*pret_minim_1
                                cost+=min((cantitate_culoare_1 + cantitate_culoare_2) , x[0]-cantitate-(cantitate_culoare_1 + cantitate_culoare_2))*self.preturi[combinatie[0]]

                            elif ok==3:
                                cost+= (x[0] - cantitate-(cantitate_culoare_1 + cantitate_culoare_2))/2*pret_minim_2
                                cost+=min((cantitate_culoare_1 + cantitate_culoare_2) , x[0]-cantitate-(cantitate_culoare_1 + cantitate_culoare_2))*self.preturi[combinatie[1]]


                            elif ok==4:
                                cost+= (x[0] - cantitate-(cantitate_culoare_1 + cantitate_culoare_2))/2*min(pret_minim_1, pret_minim_2)
                                cost+=min((cantitate_culoare_1 + cantitate_culoare_2) , x[0]-cantitate-(cantitate_culoare_1 + cantitate_culoare_2))*min(self.preturi[combinatie[0]], self.preturi[combinatie[1]])


                if ok==0:
                    return float('inf')

        return cost

    def euristica_admisibila_2(self, infoNod, tip_euristica):
        cost = 0
        for x in self.scopuri:
            cantitate = 0
            cantiatedoarunvas=0
            for y in infoNod:
                if y[2] == x[1]:
                    if y[2] == x[1]:
                        if y[1] >= x[0] and cantiatedoarunvas > y[1]:
                            cantitatedoarunvas = y[1]
                    cantitate += y[1]

            if cantiatedoarunvas!=0:
                cantitate=cantiatedoarunvas

            if cantitate > x[0]:
                cost += (cantitate - x[0]) * self.preturi[x[1]]
                return cost

            elif cantitate < x[0]:
                ok = 0
                for combinatie in self.dict:
                    if self.dict[combinatie] == x[1]:
                        ok += 1
                        cantitate_culoare_1 = 0 #cautam in ce cantitati avem culorile din care se formeaza culoarea cautata
                        cantitate_culoare_2 = 0

                        for y in infoNod:
                            if y[2] == combinatie[0]:
                                cantitate_culoare_1 += y[1]

                        for y in infoNod:
                            if y[2] == combinatie[1]:
                                cantitate_culoare_2 += y[1]

                        cost +=  min(self.preturi[combinatie[0]], self.preturi[combinatie[1]])
                        cost += min((x[0] - cantitate), cantitate) * self.preturi[x[1]]

                        if cantitate_culoare_1 + cantitate_culoare_2 >= x[0] - cantitate:
                            break

                        if cantitate_culoare_1 + cantitate_culoare_2 < x[0] - cantitate:    #daca nu avem destula cantitate de vopsea pentru a forma restul de culoare scop
                            for combinatie_culoare_1 in self.dict:#vedem daca se poate obtine prima culoare din combinatie din alte 2 culori si pretul minim de a o obtine
                                if self.dict[combinatie_culoare_1] == combinatie[0]:
                                    ok += 1
                                    pret_minim_1 = min(self.preturi[combinatie_culoare_1[0]],
                                                       self.preturi[combinatie_culoare_1[1]])

                            for combinatie_culoare_2 in self.dict:#vedem daca se poate obtine a doua culoare din combinatie din alte 2 culori si pretul minim de a o obtine
                                if self.dict[combinatie_culoare_2] == combinatie[1]:
                                    ok += 2
                                    pret_minim_2 = min(self.preturi[combinatie_culoare_2[0]],
                                                       self.preturi[combinatie_culoare_2[1]])

                            if ok == 1:#daca nu se poate obtine nici macar una din cele 2 culori din combinatia pentru culoarea scop, atunci nu putem ajunge in starea scop
                                return float('inf')

                            elif ok == 2:  #daca se poate doar o culoare din cele 2, obtinem cantitatea ramasa din ea
                                cost += pret_minim_1  #costul minim de a obtine cantitatea ramasa de culoare intermediara
                                cost += min((cantitate_culoare_1 + cantitate_culoare_2), #costul minim de a o adauga peste cealalta cantitate de culoare intermediara
                                            x[0] - cantitate - (cantitate_culoare_1 + cantitate_culoare_2)) *self.preturi[combinatie[0]]

                            elif ok == 3:
                                cost +=  pret_minim_2
                                cost += min((cantitate_culoare_1 + cantitate_culoare_2),
                                            x[0] - cantitate - (cantitate_culoare_1 + cantitate_culoare_2)) * self.preturi[combinatie[1]]


                            elif ok == 4:#daca putem obtine ambele culori, atunci obtinem restul de cantitate din cea cu pretul cel mai mic
                                cost += min(pret_minim_1, pret_minim_2)
                                cost += min((cantitate_culoare_1 + cantitate_culoare_2),
                                            x[0] - cantitate - (cantitate_culoare_1 + cantitate_culoare_2)) * min(
                                    self.preturi[combinatie[0]], self.preturi[combinatie[1]])

                if ok == 0:
                    return float('inf')

        return cost

@stopit.threading_timeoutable(default="")
def uniform_cost(gr, nrSolutiiCautate=1):
    start_time = time.time()
    c = [NodParcurgere(gr.start,None,0)]
    max_noduri=0
    while len(c) > 0:
        if(len(c)>max_noduri):
            max_noduri=len(c)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            g.write('\n')
            nodCurent.afisDrum()
            g.write("Numarul maxim de noduri in memorie: "+str(max_noduri))
            g.write("\nTimp: %s seconds " % (time.time() - start_time))
            g.write('\n')
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].g > s.g:
                    break
                i += 1
            c.insert(i, s)


@stopit.threading_timeoutable(default="")
def a_star(gr, nrSolutiiCautate, tip_euristica):
    start_time = time.time()
    c = [
        NodParcurgere(
            gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica)
        )
    ]
    max_noduri = 0
    while len(c) > 0:
        if (len(c) > max_noduri):
            max_noduri = len(c)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            g.write('\n')
            nodCurent.afisDrum(afisCost=True)
            g.write("Numarul maxim de noduri in memorie: " + str(max_noduri))
            g.write("\nTimp: %s seconds " % (time.time() - start_time))
            g.write('\n')
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return

        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica)
        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].f >= s.f:
                    break
                i += 1
            c.insert(i, s)


@stopit.threading_timeoutable(default="")
def a_star_optimizat(gr,tip_euristica):
    start_time = time.time()
    c = [NodParcurgere( gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]
    closed = []
    max_noduri = 0

    while len(c) > 0:
        if (len(c) +len(closed)> max_noduri):
            max_noduri = len(c)+len(closed)
        nodCurent = c.pop(0)
        closed.append(nodCurent)

        if gr.testeaza_scop(nodCurent):
            g.write('\n')
            nodCurent.afisDrum(afisCost=True)
            g.write("Numarul maxim de noduri in memorie: " + str(max_noduri))
            g.write("\nTimp: %s seconds " % (time.time() - start_time))
            g.write('\n')
            return

        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica)
        lSuccesoriCopy = lSuccesori.copy()
        for s in lSuccesoriCopy:
            gasitOpen = False
            for elem in c:
                if s.info == elem.info:
                    gasitOpen = True
                    if s.f < elem.f:
                        c.remove(elem)
                    else:
                        lSuccesori.remove(s)
                    break
            if not gasitOpen:
                for elem in closed:
                    if s.info == elem.info:
                        if s.f < elem.f:
                            closed.remove(elem)
                        else:
                            lSuccesori.remove(s)
                        break

        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].f >= s.f:
                    break
                i += 1
            c.insert(i, s)

@stopit.threading_timeoutable(default="")
def ida_star(gr, nrSolutiiCautate, tip_euristica):
    limita = gr.calculeaza_h(gr.start,tip_euristica)
    nodStart = NodParcurgere( gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))

    while True:

        nrSolutiiCautate, rez = construieste_drum(
            gr, nodStart, limita, nrSolutiiCautate,tip_euristica)
        if rez == "gata":
            break
        if rez == float("inf"):
            print("Nu exista suficiente solutii!")
            break
        limita = rez


def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate,tip_euristica):
    start_time = time.time()
    if nodCurent.f > limita:
        return nrSolutiiCautate, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        nodCurent.afisDrum(afisCost=True)
        g.write("\nTimp: %s seconds " % (time.time() - start_time))
        g.write('\n')
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent,tip_euristica)
    minim = float("inf")
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate,tip_euristica)
        if rez == "gata":
            return nrSolutiiCautate, "gata"
        if rez < minim:
            minim = rez

    return nrSolutiiCautate, minim


euristici = ['euristica_banala', 'euristica_admisibila_2', 'euristica_admisibila_1', 'euristica_neadmisibila']


nrSolutiiCautate = int(input('Introduceti numarul de solutii: '))
folder_input = str(input('Introduceti calea de input: '))
folder_output = str(input('Introduceti calea fisierului de output: '))
timeout = int(input('Introduceti timpul de timeout: '))
entries = os.listdir(folder_input)
'''
nrSolutiiCautate = 2
folder_input = str("input")
folder_output = str("output")
timeout = 5
entries = os.listdir(folder_input)
'''

for entry in entries:
        cale_input = os.path.join(folder_input, entry)
        gr = Graph(cale_input)
        for euristica_tip in euristici:
            cale_output = os.path.join(folder_output, "a_star_optimizat" + "_"+euristica_tip+"_"+entry)
            g = open(cale_output, "w")
            a_star_optimizat(gr, euristica_tip,timeout=timeout)
            g.close()

        for euristica_tip in euristici:
            cale_output = os.path.join(folder_output, "a_star" + "_" +euristica_tip+ "_"+entry)
            g = open(cale_output, "w")
            a_star(gr,nrSolutiiCautate, euristica_tip,timeout=timeout)
            g.close()

        for euristica_tip in euristici:
            cale_output = os.path.join(folder_output, "ida_star" + "_"+euristica_tip+"_"+entry)
            g = open(cale_output, "w")
            ida_star(gr,nrSolutiiCautate, euristica_tip,timeout=timeout)
            g.close()

        cale_output = os.path.join(folder_output, "uniform_cost_"  + "_" + entry)
        g = open(cale_output, "w")
        uniform_cost(gr,nrSolutiiCautate, timeout=timeout)
        g.close()



