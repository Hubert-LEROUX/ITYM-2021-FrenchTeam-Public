ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def doProperKNumbering(graph, weight):
    """
    @param: weight est une liste 2D qui donne la matrice d'adjacence du graphe
    @param: graph est une liste 2D qui donne la liste d'adjacence du graphe
    @return: une liste des labels de chaque noeud
    """
    nbNoeuds = len(graph)
    nodes = list(range(nbNoeuds)) # La liste des noeuds dans un ordre donné

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
                S.append((max(1,properNumbering[neighbor]-w) , properNumbering[neighbor]+w))
        UnionIntervalsInterdits = intervals_union(S)

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


if __name__ == '__main__':
    graph, weight = extractGraph("graph1")
    # print(graph)
    print(f"S = {computeS(weight)}")
    properNumbering = doProperKNumbering(graph, weight)
    print([(ALPHABET[node], value) for node, value in enumerate(doProperKNumbering(graph, weight))])
    print(f"We have a vertex {max(properNumbering)}-numbering !")
    
    