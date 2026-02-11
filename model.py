"""
Here is the definition of the dynamic network model that will be used to experiment
with the strategic evolution of cooperation.
"""

# Import libraries

import numpy as np, scipy as sp, pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import mesa as ms

def define_random_strategy(rn):
    """
    Output: 0 = Defector, 1 = Cooperator.
    """
    return 0 if rn < 0.5 else 1

# Simple model of a static network
# Define an undirected graph: Wij == Wji

n = 10      # nodes
c = 2       # cost
b = 3       # benefit
d = 0.01    # selection intensity, assumed to be small (d≪1)

G = nx.complete_graph(n)            # ...Try also with connected and bipartite graphs
nx.set_edge_attributes(G, 0, 'w')   # unclear... What does weight signify?

rng = np.random.default_rng(seed=42)

for i,j in G.edges():     # Assign a random weight between 0 and 1 to all edges of the graph
    G.edges[i, j]['w'] = rng.uniform(low=0.0, high=1.0)

for i in G:      # Assign a strategy to each node (Defector or Cooperator -> 0 or 1)
    G.nodes[i]['x'] = define_random_strategy(rng.random())

# Play donation game between i and each of its neighbors
for i in G:

    # Calculate accumulated payoff
    xi = G.nodes[i]['x']        # 0 or 1 — is i a cooperator?
    u = 0
    for j in G.neighbors(i):
        xj = G.nodes[j]['x']    # 0 or 1 — is i's neighbor j a cooperator?
        wij = G.edges[i,j]['w']
        u += wij * ((b * xj) - (c * xi))      # accumulated payoff of i

    # Transform accumulated payoff of i into its fecundity
    G.nodes[i]['F'] = 1 + d * u         # where d is the selection intensity

# Pick an individual i uniformly at random from the population: probability 1/n
i = rng.choice(G.nodes())

# Calculate the probability e that i copies the strategy of its j neighbors
e = [G.nodes[j]['F'] * G.edges[j,i]['w'] for j in G.neighbors(i)]
e = np.array(e) / sum(e)

# Pick j from which i copies its strategy
j = rng.choice(list(G.neighbors(i)), p=e)
    # here, p defines the probabilities associated with each neighbor of i.
    # Undefined, it would assume uniform probability (as with the choice of i).

G.nodes[i]['x'] = G.nodes[j]['x']

# Population transition step (exogenous transformation)




