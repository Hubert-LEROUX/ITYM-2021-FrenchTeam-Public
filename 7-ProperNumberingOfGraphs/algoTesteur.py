import time
import networkx as nx
import random
from copy import deepcopy


def s(n, G):
    """renvoie la somme des poids des arrêtes qui ont n en extrémité"""
    somme = 0
    for (_, _, poids) in G.edges.data("weight", nbunch=n, default=1):
        somme += poids
    return somme


def S(G):
    """renvoie la valeur maximale de s(n)"""
    somme_max = 0
    for node in G.nodes():
        somme_max = max(s(node, G), somme_max)
    return somme_max


def description(G):
    """simple description"""
    print("Desc   :", G)
    print("noeuds :", G.nodes())
    print("edges  :", " ".join(
        [f"({debut},{fin})" for (debut, fin, infos) in G.edges.data()]
    )
    )
    print("S(G) :", S(G))
    print("\n\n")


def desc(G):
    """en plus court : numéroDuNoeud(PoidsDuNoeud)"""
    return (" ".join([f"{n}({infos['poids']})" for (n, infos) in G.nodes(data=True)]))


def verification(G, fct):
    """test la fonction fct sur le graph G est renvoie true si elle trouve bien une S(G)+1 numérotation"""
    labelled, SG = fct(deepcopy(G)), S(G)

    for node in G.nodes():
        if not (0 <= G.nodes[node]["poids"] <= SG):
            return f"node {node} non compris entre 0 et {SG} : {G.nodes[node]['poids']}"

        for (_, voisin, poids) in G.edges.data("weight", nbunch=node, default=1):
            if abs(labelled.nodes[node]["poids"] - labelled.nodes[voisin]["poids"]) < poids:
                return False
    return True


def forcerSG(G, SG=-1, seed=42):
    random.seed(seed)
    """complète le graphe pour que s(n) = SG, changer SG à un entier positif pour forcer cette valeur
    si SG < S(G), aucune liaison n'est enlevée"""
    SG = max(S(G), SG)

    pile = list(G.nodes())
    random.shuffle(pile)

    while len(pile) > 1:
        nodeA, nodeB = pile.pop(), pile.pop()

        ajout_liaison = SG - max([s(nodeA, G), s(nodeB, G)])

        if ajout_liaison > 0:
            ajout_liaison = random.randint(1, ajout_liaison)

            if (nodeA, nodeB) in G.edges():
                if not "weight" in G.edges[nodeA, nodeB].keys():
                    G.edges[nodeA, nodeB]["weight"] = 1
                G.edges[nodeA, nodeB]["weight"] += ajout_liaison
            else:
                G.add_edge(nodeA, nodeB, weight=ajout_liaison)

        if s(nodeA, G) != SG:
            pile.append(nodeA)
        if s(nodeB, G) != SG:
            pile.append(nodeB)

        random.shuffle(pile)
    return G


def bandeTests(fct, graphes):
    """vérifie la fonction fct sur plusieurs graphes"""
    for (graphe, commentaire) in graphes:
        print('\tS(G):{:4} | {:40}'.format(S(graphe), commentaire), end="")
        nx.set_node_attributes(graphe, 0, "poids")

        time_start = time.time()
        resultat = verification(graphe, fct)

        if resultat == True:
            print("-> ✅ Ok ({:<6})s.".format(str(round(time.time() - time_start, 3))))

        else:
            print("-> 🔴 Erreur :", resultat)
            exit(1)


def algoSimple(G):
    """prend le noeud avec le plus grand s(G), le numérote s(G) et enlève toutes ses liaisons du noeuds"""
    while G.edges():
        poids, node = max([
            (s(node, G), node)
            for (node, _) in G.edges()
        ])

        G.nodes[node]["poids"] = poids
        a_enlever = deepcopy(G.edges(node))
        G.remove_edges_from(a_enlever)
    return G


graphes_non_pondérées = (
    (nx.complete_graph(8), "graphe complet 8"),
    (nx.complete_graph(7), "graphe complet 7"),
    (nx.cycle_graph(8), "cycle_graph"),
    (nx.star_graph(8), "star_graph"),
    (nx.turan_graph(8, 8), "turan_graph"),
    (nx.wheel_graph(3), "wheel_graph 3"),
    (nx.path_graph(8), "path_graph"),
    (nx.empty_graph(8), "empty_graph"),
    (nx.ladder_graph(8), "ladder_graph"),
    (nx.circular_ladder_graph(8), "circular_ladder_graph"),
    (nx.dorogovtsev_goltsev_mendes_graph(5), "dorogovtsev_goltsev_mendes_graph 5"),
    (nx.full_rary_tree(8, 8), "full_rary_tree"),
)

graphes_pondérées = (
    (nx.Graph([
        (1, 2, {"weight": 6}),
        (1, 3, {"weight": 1}),
        (1, 4, {"weight": 1}),
        (1, 5, {"weight": 16}),
        (2, 3, {"weight": 8}),
        (2, 4, {"weight": 8}),
        (2, 5, {"weight": 1}),
        (3, 4, {"weight": 8}),
        (3, 8, {"weight": 1}),
        (4, 5, {"weight": 2}),
        (4, 6, {"weight": 4}),
        (4, 8, {"weight": 1}),
        (5, 8, {"weight": 1}),
        (6, 7, {"weight": 12}),
        (6, 8, {"weight": 8}),
        (7, 8, {"weight": 12}),
    ]), "graphe pondéré avec une arrête à 16"),
    (nx.Graph([
        (1, 2, {"weight": 10}),
        (3, 4, {"weight": 10}),
        (1, 4, {"weight": 1}),
        (1, 3, {"weight": 1}),
        (2, 3, {"weight": 1}),
        (2, 4, {"weight": 1}),
    ]), "graphe complet à 4 nodes pondérées"),
)

if __name__ == "__main__":
    print("Graphes pondérées :")
    bandeTests(algoSimple,
               [(forcerSG(graphe), commentaire) for (graphe, commentaire) in graphes_pondérées]
               )  # forcer SG permet que tout les noeuds aient s(n) = S(G)
    print("")

    print("Graphes non pondérées :")
    bandeTests(algoSimple,
               [(forcerSG(graphe), commentaire) for (graphe, commentaire) in graphes_non_pondérées]
               )
    print("")

    seed = int(time.time() * 100000)
    random.seed(a=seed)
    SG = random.randint(1, 100)
    print("Graphes pondérées aléatoire : seed=", seed, " SG=", SG, sep="")
    bandeTests(algoSimple,
               [(forcerSG(graphe, seed=seed, SG=SG), commentaire) for (graphe, commentaire) in graphes_non_pondérées]
               )
    print("")

    if input("(o/y/ ) pour continuer avec des graphes aléatoires : ") not in ("o","y"," "):
        exit(0)
    print("en boucle :")
    while True:
        seed = int(time.time() * 100000)
        SG = random.randint(1, 150)
        bandeTests(algoSimple,
                   [(forcerSG(nx.empty_graph(150), seed=seed, SG=SG), f"seed={seed}") for (graphe, commentaire) in graphes_non_pondérées]
                   )
