import random as rd
import os
import sys

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def doProperKNumbering(graph, weight, nodes=None):
    """
    @param: weight est une liste 2D qui donne la matrice d'adjacence du graphe
    @param: graph est une liste 2D qui donne la liste d'adjacence du graphe
    @return: une liste des labels de chaque noeud
    """
    nbNoeuds = len(graph)

    if nodes == None:
        #* On s'en fiche de l'ordre
        nodes = list(range(nbNoeuds)) # La liste des noeuds dans un ordre donné
        #* On trie en fonction de s(v) croissant
        # nodes.sort(key = lambda node: sum(weight[node]))
        #* On trie en fonction de s(v) décroissant
        # nodes.sort(key = lambda node: sum(weight[node]), reverse = True)
        # print(nodes)
        #* On trie au hasard
        # rd.shuffle(nodes)

    # print(f"Ordre d'application {[ALPHABET[node] for node in nodes]}")

    properNumbering = [0]*nbNoeuds # on met un 0 lorsque l'on a rien labeliser encore

    def searchProperNumberForNode(node):
        """
        @param: noeud est le noeud du graphe que l'on étudie
        @return: "the least possible number for which the required condition for a proper k-numbering will not be violated
        Il faut donc trouver la valeur minimum
        """
        
        # On obtiens l'union des intervals interdits
        S = []
        for neighbor in graph[node]: # Pour chaque voisin
            if properNumbering[neighbor] > 0: # S'il a été etiqueté, il donne une nouvelle contrainte
                w = weight[node][neighbor] # Poids de la liaison
                # print(f"The liaison between: {ALPHABET[node]}-{ALPHABET[neighbor]} has a label = {w}")
                if w > 0:
                    S.append((max(1,properNumbering[neighbor]-w+1) , properNumbering[neighbor]+w)) # Intervalle d'interdiction semi-ouvert [a,b[
                    # print(S)
        UnionIntervalsInterdits = intervals_union(S)
        # print(f"For node: {ALPHABET[node]}, the union of intervals = {UnionIntervalsInterdits}")

        if UnionIntervalsInterdits and UnionIntervalsInterdits[0][0] == 1: # On ne peut pas commencer à 1
            return UnionIntervalsInterdits[0][1] # On renvoie le plus petit numéro libre après cet interval
        else:
            return 1

    for node in nodes:
        properNumbering[node] = searchProperNumberForNode(node)

    return properNumbering


def computeS(weight):
    return max( (sum(liaisons), node) for node, liaisons in enumerate(weight) )

def intervals_union(S):
    # E contient les événements
    # -1 si ouverture
    # +1 si fermeture
    E = [(low, -1) for low, _ in S]
    E += [(high, +1) for _, high in S]
    
    nb_open = 0 # Conserve le nombre d'intervals ouverts en ce moment
    last = None # Conserve le moment où on nb_open=0 pour la dernière fois

    retval = []

    # Et puis on balaye
    for x, _dir in sorted(E): # Pour chaque événement à la date x:
        if _dir == -1: # S'il s'agit d'une ouverture
            if nb_open == 0:
                last = x
            nb_open+=1
        else: # IL s'agit d'une fermeture
            nb_open -= 1 
            if nb_open == 0: # On ferme l'interval
                retval.append((last, x))
    return retval

def extractGraph(filename):
    """
    Construie un graphe d'après la matrice d'adjacence située dans filename
    @return: la liste et la matrice d'adjacence
    """
    with open(filename, "r") as f:
        weight = [list(map(int, line.strip().split())) for line in f]

    nbNodes = len(weight)
    graph = [[] for _ in range(nbNodes)]
    for node in range(nbNodes):
        for otherNode in range(nbNodes):
            if weight[node][otherNode] > 0:
                graph[node].append(otherNode)

    return graph, weight

def afficheGraphe(graph, weight):
    """
    Permet d'afficher proprement un graphe
    """
    for node, neighbors in enumerate(graph):
        print(ALPHABET[node], [(ALPHABET[neighbor], weight[node][neighbor]) for neighbor in neighbors])

def giveDataGraph(graph, weight, useAlphabet=True):
    """
    Affiche les données brutes du graphe utilisable pour le site suivant https://csacademy.com/app/graph_editor/
    """
    nb_noeuds = len(graph)
    print(nb_noeuds)

    def giveNotationNode(node):
        return ALPHABET[node % len(ALPHABET)] if useAlphabet else node

    # On affiche les noeuds
    for node in range(nb_noeuds):
        print(giveNotationNode(node))

    for a in range(nb_noeuds):
        for b in range(a+1, nb_noeuds):
            if weight[a][b] > 0:
                print(giveNotationNode(a), giveNotationNode(b), weight[a][b])
    print()
    for line in weight:
        print(" ".join([str(node) for node in line]))


def main(N = 4):
    """
    Nous allons construire KN et faire varier les coefficients
    """
    graph = [[] for _ in range(N)]
    for node in range(N):
        for other in range(N):
            if other != node:
                graph[node].append(other)

    weight = [[0]*N for _ in range(N)]

    variables = [(a,b) for a in range(N) for b in range(N) if a < b]
    # valuesPossible = list(range(10))
    valuesPossible = [1,int(1e6)]
    # valuesPossible = [0,1]
    bestRatio = 0

    def recursiveTest(positionVariable):
        """
        Cette fonction permet de remplir la matrice d'adjacence en omettant aucun cas
        On reproduira cependant de nombreuses fois le même graphe à un isomorphisme près
        On met également à jour le meilleur ratio k / S
        """
        nonlocal weight, bestRatio
        if positionVariable == -1: # Toutes les cases ont été remplies
            S = computeS(weight)[0]
            if S > 1:
                properNumbering = doProperKNumbering(graph, weight)
                k = max(properNumbering)
                ratio = k / S
                if bestRatio < ratio:
                    bestRatio = ratio
                    print(f"k={max(properNumbering)}\tS={computeS(weight)[0]}\tRATIO={ratio}")
                    afficheGraphe(graph, weight)
                    properNumbering = doProperKNumbering(graph, weight)
                    print([(ALPHABET[node], value) for node, value in enumerate(properNumbering)])
                    giveDataGraph(graph, weight)
                    print()
                    print()
                if k >= 2 * S:
                    afficheGraphe(graph, weight)
                    print(f"k={max(properNumbering)}\tS={computeS(weight)[0]}\tRATIO={ratio}")
                    properNumbering = doProperKNumbering(graph, weight)
                    print([(ALPHABET[node], value) for node, value in enumerate(properNumbering)])
                    print(f"We have a vertex {max(properNumbering)}-numbering !")
                    giveDataGraph(graph, weight)
                    exit()
            return

        for value in valuesPossible:
            y,x = variables[positionVariable]
            weight[y][x] = value
            weight[x][y] = value
            recursiveTest(positionVariable-1)

    recursiveTest(len(variables)-1)
    print(bestRatio)




if __name__ == '__main__':
    # directoryGraphs = "examplesGraphs"
    # graph, weight = extractGraph(os.path.join(directoryGraphs, "graph4"))
    # # print(graph)
    # print(f"S = {computeS(weight)}")
    # properNumbering = doProperKNumbering(graph, weight)
    # afficheGraphe(graph, weight)
    # giveDataGraph(graph, weight)
    # print([(ALPHABET[node], value) for node, value in enumerate(properNumbering)])
    # print(f"We have a vertex {max(properNumbering)}-numbering !")

    main(5)
    
    