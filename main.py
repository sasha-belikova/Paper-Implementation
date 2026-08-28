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

        
def reach(V, edges, directed):
    if directed == True: 
        graph = create_adjacency_matrix(V, edges, True)
        source = find_source(graph)
        result = np.dot(source, graph)
    return result




