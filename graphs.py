"""
A module for specific graph generation functions.

"""

import networkx as nx

def star_complete_barbell_graph(size: int, first: str) -> nx.Graph:
    
    """
    Generates an asymmetric barbell graph that consists of a star graph and a complete graph, where the center or hub node of the star is connected to a node in the complete graph.
    
    Args:
        size: Number of leaves in the star graph, and number of nodes in the complete graph. NOTE: the number must be even.
        first: 'star' or 'complete', to indicate which graph is generated first. The two outcomes are opposite to one another.

    """

    size = int(size / 2)

    if first == 'star':
        star = nx.star_graph(size)
        star.add_edge(0, size) 
        complete = nx.complete_graph(size)
        complete = nx.relabel_nodes(complete, lambda x: x + size)
        G = nx.compose(star, complete)
    
    elif first == 'complete':
        complete = nx.complete_graph(size)
        complete.add_edge(0, size)
        star = nx.star_graph(size-1)
        star = nx.relabel_nodes(star, lambda x: x + size)
        G = nx.compose(complete, star)

    else:
        raise ValueError("Argument 'first' must have value 'star' or 'complete'.")

    return G

def three_communities_graph(size: int, pair: str) -> nx.Graph:
    
    """
    Generates a graph with three distinct communities of star (S) and complete (C) graphs, which are connected by an edge in such a way that S-C-S or C-S-C.
    
    Args:
        size: Total number of nodes. NOTE: the number must be a multiple of 3.
        pair: 'star' or 'complete', to indicate which graph structure is generated in the central community, i.e. O in X-O-X. 

    """

    size = int(size / 3)

    if pair == 'star':
        star = nx.star_graph(size)
        star.add_edge(0, size) 
        complete = nx.complete_graph(size)
        complete = nx.relabel_nodes(complete, lambda x: x + size)
        G = nx.compose(star, complete)
    
    elif pair == 'complete':
        complete = nx.complete_graph(size)
        complete.add_edge(0, size)
        star = nx.star_graph(size-1)
        star = nx.relabel_nodes(star, lambda x: x + size)
        G = nx.compose(complete, star)

    else:
        raise ValueError("Argument 'pair' must have value 'star' or 'complete'.")

    return G