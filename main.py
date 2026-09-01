import numpy as np
from scipy.sparse import csr_matrix, eye, diags

def create_adjacency_matrix(V, edges, directed):
    if not edges:
        return csr_matrix((V, V), dtype=bool)
    edges_array = np.array(edges)
    rows = edges_array[:, 0]
    cols = edges_array[:, 1]
    data = np.ones(len(edges), dtype=bool)
    if not directed:
        rows = np.concatenate([rows, cols])
        cols = np.concatenate([cols, edges_array[:, 0]])
        data = np.concatenate([data, data])
    return csr_matrix((data, (rows, cols)), shape=(V, V), dtype=bool)


def reach(source_node, matrix):
    v = csr_matrix(source_node, dtype=bool)
    V = matrix.shape[0]
    for i in range(V):
        prev_none_zero = v.nnz
        v = v + (v @ matrix)
        if v.nnz == prev_none_zero:
            break
    return v


def pickAny(matrix):
    V = matrix.shape[0]
    matrix = matrix.tocsr()
    matrix.sum_duplicates()
    new_data = []
    new_indices = []
    new_indptr = [0]
    for i in range(V):
        start = matrix.indptr[i]
        end = matrix.indptr[i+1]
        if start < end:
            new_indices.append(matrix.indices[start])
            new_data.append(True)
            new_indptr.append(new_indptr[-1] + 1)
        else:
            new_indptr.append(new_indptr[-1])      
    return csr_matrix((new_data, new_indices, new_indptr), shape=matrix.shape, dtype=bool)


def WCC(V, edges):
    matrix = create_adjacency_matrix(V, edges, directed = False)

    label = eye(V, dtype=bool, format='csr')
    for i in range(V):
        prev_label = label
        new_lable = label + (matrix @ label)
        label = pickAny(new_lable)
        if (label != prev_label).nnz == 0:
            break
    return label


def SCC(V, edges):
    matrix = create_adjacency_matrix(V, edges, directed = True)
    rows = []
    cols = []
    data = []
    for i in range(V):
        node = np.zeros((1, V), dtype = bool)
        node[0, i] = True
        reachable = reach(node, matrix)
        coordinate = reachable.tocoo()
        for j in coordinate.col:
            rows.append(i)
            cols.append(j)
            data.append(True)
    R = csr_matrix((data, (rows, cols)), shape=(V, V), dtype=bool)
    scc_matrix = R.multiply(R.transpose())
    return scc_matrix



