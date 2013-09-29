class BinaryHeap:
    def __init__(self):
        self.heap = [0,[0,-1],[0,-1],[0,-1]]
        self.size = 0

    # node -> [(x, y), cost]
    def insert(self, node):
        if self.size == len(self.heap)-1:
            self.heap += [[0,-1]]*(self.size+1)
        self.size += 1
        pos = self.size
        while pos > 1 and node[1] < self.heap[pos/2][1]:
            self.heap[pos] = self.heap[pos/2]
            pos /= 2
        self.heap[pos] = node

    def remove_priority(self):
        if self.size == 1:
            priority = self.heap[1]
            self.heap[1] = [0,-1]
            self.size = 0
            return priority
        elif self.size > 0:
            priority = self.heap[1]
            node = self.heap[self.size]
            self.heap[self.size] = [0,-1]
            self.size -= 1
            pos = 1
            while pos <= self.size/2:
                lchild = self.heap[2*pos]
                rchild = self.heap[2*pos+1]
                if node[1] > max(lchild[1],rchild[1]) > -1:
                    if lchild[1] <= rchild[1] or rchild[1] == -1:
                        self.heap[pos] = lchild
                        pos = 2*pos
                    else:
                        self.heap[pos] = rchild
                        pos = 2*pos+1
                elif node[1] > min(lchild[1],rchild[1]) > -1:
                    if lchild[1] < rchild[1]:
                        self.heap[pos] = lchild
                        pos = 2*pos
                    else:
                        self.heap[pos] = rchild
                        pos = 2*pos+1
                else:
                    break
            self.heap[pos] = node
            return priority
        else:
            return -1

# source, target -> (x,y)
def Dijkstra(grid, source, target):

    ### DATA STRUCTURES
    # distances and parents dictionary
    D = {}
    # visited vertices list
    S = []
    # priority queue for minimum distance node
    Q = BinaryHeap()

    ### INITIALIZATIONS
    maxn = grid.n
    maxm = grid.m
    # dictionary initiation
    for n in xrange(grid.n):
        for m in xrange(grid.m):
            if n == source[0] and m == source[1]:
                D[(n, m)] = (0, source)
            else:
                # since there are less than 1000 nodes on the graph, this can serve as /infinite/ distance
                D[(n, m)] = (1000, 0)
    Q.insert([source, 0])
    ### MAIN LOOP
    while Q.size > 0:
        x = Q.remove_priority()
        if x[0] == target:
            break
        if x[1] == 1000:
            break
        S.append(x[0])
        # for each v near x
        for i in [[1,0], [0,1], [-1,0], [0,-1]]:
            # maxn, maxm are size of grid
            if maxn > x[0][0]+i[0] >= 0 and maxm > x[0][1]+i[1] >= 0:
                v = (x[0][0]+i[0], x[0][1]+i[1])
                if v not in S:
                    # where 1 is the dist between adjacent nodes (diagonals excluded)
                    d = D[x[0]][0] + 1
                    if d < D[v][0]:
                        D[v] = (d, x[0])
                        Q.insert([v, d])
    # retrieve past
    waypoints = [target]
    p = target
    while p != source:
        p = D[p][1]
        waypoints.insert(0, p)
    return waypoints
