"""
This Python script runs the first experiment of the dynamic network model, which
discusses the the impact of sparse and dense communities on the evolution of cooperation.

"""

from turtle import pos

import model as ce
import graphs as g

if __name__ == "__main__":

    """
    When the population evolves on either network 1 or network 2 alone, cooperation
    is disfavored by selection regardless of the benefit-to-cost ratio b/c. 

    When the population transitions dynamically between networks 1 and 2, cooperation is favored
    provided the benefit-to-cost ratio b/c exceeds the critical value (b/c) ≈ 7. As a result, we
    see that dynamic population structures can favor cooperation, even when all networks involved
    would each individually suppress cooperation were they static.
    
    Dynamic population structure facilitates cooperation across a wide range of population sizes
    for the pair of networks. When t1 = t2 = 1, which means that individuals each update their 
    strategy once, on average, before the network changes, cooperation can be favored by selection 
    regardless of network size, N.
    """

    # Assign model values.

    n = 16    # Number of nodes in the graph
    c = 3     # Cost coefficient
    b = 3     # Benefit coefficient
    T = 5   # Number of time steps to run the model for

    # Generate a list of network structures.

    Graphs = [
        g.star_complete_barbell_graph(size=n, first='star'),
        g.star_complete_barbell_graph(size=n, first='complete')
    ]

    # Run the model.

    model = ce.CooperationEvolution(L=Graphs, c=c, b=b, p=1/len(Graphs))
    model.run(T=T, visualize=True)