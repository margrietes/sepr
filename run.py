"""
This Python script runs the dynamic network model that will be used to experiment
with the strategic evolution of cooperation.

"""

# Import libraries.

import model as ce
import graphs as g

# Assign model values.

n = 10    # Number of nodes in the graph
c = 2     # Cost coefficient
b = 3     # Benefit coefficient
T = 10   # Number of time steps to run the model for

# Generate a list of network structures.

Graphs = [
    g.star_complete_barbell_graph(size=n, first='star'),
    g.star_complete_barbell_graph(size=n, first='complete')
]

# Run the model.

for t in range(T):
    model = ce.CooperationEvolution(L=Graphs, c=c, b=b, p=1/len(Graphs))
    model.run(T=1)
    

