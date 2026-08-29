import numpy as np


def create_adjacency_matrix(V, edges, directed):
    matrix = [[0] * V for _ in range(V)]
    for edge in edges:
        u, v = edge
        matrix[u][v] = 1
        if directed == False:
            matrix[v][u] = 1 
    return np.array(matrix)


def find_source(graph):
    V = len(graph)
    for node in range(V):
        incoming = any(graph[i][node] == 1 for i in range(V))
        outgoing = any(graph[node][i] == 1 for i in range(V))
        if not incoming and outgoing:
            source = np.zeros(V)
            source[node] = 1
            return np.array(source)
        

def multiply(a, b):
    return np.dot(a, b)


def add(a, b):
    return a + b
        
def reach(node, graph):
    current = node
    reachable = node.copy()

    for i in range(graph.shape[0]):
        current = multiply(current, graph)
        reachable = add(reachable, current)
    reachable = (reachable > 0).astype(int)
    return reachable

def pickAny(matrix):
    for i, row in enumerate(matrix):
        indices = np.nonzero(row)[0]
        if len(indices) > 1:
            matrix[i, indices[1:]] = 0
    matrix = (matrix > 0).astype(int)
    return matrix


def WCC(V, edges):
    directed = False
    matrix = create_adjacency_matrix(V, edges, directed)
    vektor = np.ones(V)
    diag_matrix = np.diag(vektor)
    for i in range(matrix.shape[0]):
        temp = add(diag_matrix, multiply(matrix, diag_matrix))
        diag_matrix = pickAny(temp)
    return diag_matrix


def SCC(V, edges, directed):
    matrix = create_adjacency_matrix(V, edges, directed)
    scc_matrix = np.zeros((V, V))
    reachable_matrix = np.zeros((V, V))

    for i in range(V):
        node = np.zeros(V)
        node[i] = 1
        reachable = reach(node, matrix)
        reachable_matrix[i] = reachable

    for i in range(V):
        for j in range(V):
            if reachable_matrix[i][j] == 1 and reachable_matrix[j][i] == 1:
                scc_matrix[i][j] = 1

    return scc_matrix



