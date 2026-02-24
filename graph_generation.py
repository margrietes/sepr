"""
A module for specific graph generation functions.

"""

import networkx as nx

def star_complete_barbell_graph(size: int, first: str) -> nx.Graph:
    
    """
    Generates an asymmetric barbell graph that consists of a star graph and a complete graph, where the center or hub node of the star is connected to a node in the complete graph.

    Args:
        size: Number of leaves in the star graph, and number of nodes in the complete graph.
        first: 'star' or 'complete', to indicate which graph is generated first. The two outcomes are opposite to one another.

    """

    if first == 'star':
        star = nx.star_graph(size)
        star.add_edge(0, size) 
        complete = nx.complete_graph(size)
        complete = nx.relabel_nodes(complete, lambda x: x + size)
        G = nx.compose(star, complete)
        print(G.edges)
    
    elif first == 'complete':
        complete = nx.complete_graph(size)
        complete.add_edge(0, size)
        star = nx.star_graph(size-1)
        star = nx.relabel_nodes(star, lambda x: x + size)
        G = nx.compose(complete, star)
        print(G.edges)

    else:
        raise ValueError("Argument 'first' must have value 'star' or 'complete'.")

    return G

# Implement graph with three components: two stars and a complete graph.

# Implement...

# ...

# ...