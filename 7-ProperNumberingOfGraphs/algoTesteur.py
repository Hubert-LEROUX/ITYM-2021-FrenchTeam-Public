import time
import networkx as nx
import random
from copy import deepcopy
import matplotlib.pyplot as plt


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
    """test la fonction fct sur le graph G est renvoie resultat, SG? max(poids)"""
    labelled, SG = fct(deepcopy(G)), S(G)
    max_node = max(nx.get_node_attributes(labelled, 'poids').values())
    min_node = min(nx.get_node_attributes(labelled, 'poids').values())

    for node in G.nodes():
        if not (0 <= G.nodes[node]["poids"] <= SG):
            return f"node {node} non compris entre 0 et {SG} : {G.nodes[node]['poids']}"

        for (_, voisin, poids) in G.edges.data("weight", nbunch=node):
            if abs(labelled.nodes[node]["poids"] - labelled.nodes[voisin]["poids"]) < poids:
                print(labelled.nodes[node]["poids"], "-", labelled.nodes[voisin]["poids"], " est inférieur au poids de l'arrête", poids)
                return (False, SG, max_node - min_node)
    return (True, SG, max_node - min_node)


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


def check_graph(graphe):
    nx.set_node_attributes(graphe, 0, "poids")
    for edge in graphe.edges():
        graphe.edges[edge]["weight"] = graphe.edges[edge].get("weight", 1)
    return graphe


def bandeTests(fct, graphes):
    """vérifie la fonction fct sur plusieurs graphes"""
    for position, (graphe, commentaire) in enumerate(graphes):
        time_start = time.time()
        graphe = check_graph(graphe)
        print('{:>2}:\tS(G):{:4} | {:40}'.format(position, S(graphe), commentaire), end="")
        resultat, SG, delta_poids = verification(graphe, fct)

        if resultat == True:
            print("-> ✅ Ok ({:<6})s. ({:>2})".format(str(round(time.time() - time_start, 3)), str(delta_poids + 1 - SG)))

        else:
            print("-> 🔴 Erreur :", resultat)
            input("pause")


def comparaisonAlgos(algos, graphes):
    """vérifie la fonction fct sur plusieurs graphes"""
    for position, (graphe, commentaire) in enumerate(graphes):
        graphe = check_graph(graphe)
        SG = S(graphe)
        print('{:>2}:\tS(G):{:4} | {:40}'.format(position, S(graphe), commentaire), end="\t\t")

        resultats = [verification(deepcopy(graphe), algo) for algo in algos]
        for resultat, _, delta_poids in resultats:
            icons = "✅"
            if resultat == True:
                if delta_poids + 1 - SG < 1:
                    icons = "💛"
                if delta_poids == min([poids for _, _, poids in resultats]):
                    icons = {1: "🥇", 2: "🥈"}.get([poids for _, _, poids in resultats].count(delta_poids), "🥉")
            else:
                icons = "🔴"
                delta_poids = float("inf")
            print("{} ({:>3})".format(icons, str(delta_poids + 1 - SG)), end="\t")
        print()


def algoSimple(G):
    """prend le noeud avec le plus grand s(G), le numérote s(G) et enlève toutes ses liaisons du noeuds"""
    backup = deepcopy(G)
    while G.edges():
        poids, node = max([
            (s(node, G), node)
            for node in G.nodes()
        ])
        backup.nodes[node]["poids"] = poids
        G.nodes[node]["poids"] = poids
        a_enlever = deepcopy(G.edges(node))
        G.remove_edges_from(a_enlever)
    return backup


def algoOpti(G):
    """peut être plus éfficace que S(G)+1"""
    backup = deepcopy(G)
    nx.set_node_attributes(backup, 0, "poids")

    while G.edges():
        _, node = max([
            (s(node, G), node)
            for node in G.nodes()
            if s(node, G) != 0
        ])
        for (debut, fin, weight) in deepcopy(G.edges.data("weight", nbunch=node)):
            backup.nodes[fin]["poids"] = max(backup.nodes[fin]["poids"], backup.nodes[debut]["poids"] + weight)
            G.remove_edge(debut, fin)
    return backup


def algoTest(G):
    """peut être plus éfficace que S(G)+1"""
    backup = deepcopy(G)
    nx.set_node_attributes(backup, 0, "poids")
    nx.set_node_attributes(backup, False, "fait")

    while G.edges():
        _, node = min([
            (backup.nodes[node]["poids"], node)
            for node in backup.nodes()
            if backup.nodes[node]["fait"] == False
        ])
        backup.nodes[node]["fait"] = True

        for (debut, fin, weight) in deepcopy(G.edges.data("weight", nbunch=node)):
            backup.nodes[fin]["poids"] = max(backup.nodes[fin]["poids"], backup.nodes[debut]["poids"] + weight)
            G.remove_edge(debut, fin)
    return backup


graphes_non_pondérées = (
    (nx.complete_graph(8), "graphe complet 8"),
    (nx.complete_graph(7), "graphe complet 7"),
    (nx.cycle_graph(4), "cycle_graph 3"),
    (nx.cycle_graph(4), "cycle_graph 4"),
    (nx.cycle_graph(4), "cycle_graph 5"),
    (nx.cycle_graph(8), "cycle_graph 8"),
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
        (1, 2, {"weight": 1}),
        (1, 3, {"weight": 1}),
        (1, 4, {"weight": 1}),
        (2, 3, {"weight": 1}),
    ]), "Petit test"),
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
    try:
        if input("Entrer une lettre pour un test sur un seul algo : ") in ("\n", " ", ""):

            algos = (algoSimple, algoOpti, algoTest)

            print("\n(", "/".join(map(str, [algo.__name__ for algo in algos])),")\n")
            print("Graphes pondérées :")
            comparaisonAlgos(algos, [(graphe, commentaire) for (graphe, commentaire) in graphes_pondérées])
            print("")

            print("Graphes non pondérées :")
            comparaisonAlgos(algos, [(graphe, commentaire) for (graphe, commentaire) in graphes_non_pondérées])
            print("")

            seed = int(time.time() * 100000)
            random.seed(a=seed)
            SG = random.randint(1, 100)
            print("Graphes pondérées aléatoire : seed=", seed, " SG=", SG, sep="")
            comparaisonAlgos(algos, [(forcerSG(graphe, seed=seed, SG=SG), commentaire) for (graphe, commentaire) in graphes_non_pondérées])
            print("")

        else:
            # algo = algoOpti
            algo = algoTest
            print("Test de l'algo : ", algo.__name__, "\n")

            print("Graphes pondérées :")
            bandeTests(algo, [(graphe, commentaire) for (graphe, commentaire) in graphes_pondérées])
            print("")

            print("Graphes non pondérées :")
            bandeTests(algo, [(graphe, commentaire) for (graphe, commentaire) in graphes_non_pondérées])
            print("")

            seed = int(time.time() * 100000)
            random.seed(a=seed)
            SG = random.randint(1, 100)
            print("Graphes pondérées aléatoire : seed=", seed, " SG=", SG, sep="")
            bandeTests(algo, [(forcerSG(graphe, seed=seed, SG=SG), commentaire) for (graphe, commentaire) in graphes_non_pondérées])
            print("")

            if input("(o/y/ ) pour continuer avec des graphes aléatoires : ") not in ("o", "y", " "):
                exit(0)
            print("en boucle :")
            while True:
                seed = int(time.time() * 100000)
                SG = random.randint(1, 150)
                bandeTests(algo,
                           [(forcerSG(nx.empty_graph(150), seed=seed, SG=SG), f"seed={seed}") for (graphe, commentaire) in graphes_non_pondérées]
                           )
    except KeyboardInterrupt:
        print("\n")
