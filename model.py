"""
This Python script defines the dynamic network model that will be used to experiment
with the strategic evolution of cooperation.

"""

import numpy as np
import networkx as nx

class CooperationEvolution:

    """
    A model for the evolution of cooperation in a dynamic network 
    with exogenous transitions.

    """
    
    def __init__(self, Graphs, c: float, b: float, d: float =0.01, seed: int =42):

        """
        Args:  
            Graphs: A list of graphs, assumed to be connected graphs generated with NetworkX.
            c: Cost coefficient for any Cooperator node.
            b: Benefit coefficient for any node with a Cooperator neighbor.
            d: Selection intensity, assumed to be small or weak (d≪1).
            seed: Seed for a random number generator.

        """
        
        if not isinstance(Graphs, list) or not all(isinstance(g, nx.Graph) for g in Graphs):
            raise TypeError("G must be a list of NetworkX Graph objects.")

        if not all(nx.is_connected(g) for g in Graphs):
            raise ValueError("All graphs in G must be connected.")
        
        if (c < 0) or (b < 0):
            raise ValueError("Cost and benefit must be non-negative.")

        self.Graphs = Graphs
        self.c = c
        self.b = b
        self.d = d

        # Define a random number generator with the given seed.
        self.rng = np.random.default_rng(seed=seed)

        # Define the initial network state.
        self.L = len(Graphs)
        self.state = self.rng.integers(low=0, high=self.L)
        self.G = Graphs[self.state]

        # Assign a random weight between 0 and 1 to all edges of the graph.
        nx.set_edge_attributes(self.G, 0, 'w')   # Weight indicates the influence between i and j
        for _, _, data in self.G.edges(data=True): 
            data['w'] = self.rng.uniform(low=0.0, high=1.0)

        # Assign a strategy to each node (0: Defector, 1: Cooperator).
        for _, data in self.G.nodes(data=True):
            data['x'] = 0 if self.rng.random() < 0.5 else 1

    def play(self) -> None:

        """
        Executes the donation game between all nodes with their neighbors,
        and stores the fecundity of each node in the data dictionary F of the graph.

        Note: For a dynamic model, the method should be iterated in a loop as many T times as the evolution progresses.

        """

        for i, data in self.G.nodes(data=True):

            # Calculate accumulated payoff of node i.
            xi = data['x']   # "Is node i a cooperator?"
            u = 0
            for j in self.G.neighbors(i):
                xj = self.G.nodes[j]['x']   # "Is node i's neighbor j a cooperator?"
                wij = self.G.edges[i,j]['w']
                u += wij * ((self.b * xj) - (self.c * xi))   # Accumulated payoff of i per edge

            # Transform accumulated payoff into fecundity.
            data['F'] = 1 + self.d * u

    def update_strategy(self, iterations=1) -> None:

        """
        Selects a random node i from the population, and updates its strategy 
        by copying the strategy of a neighbor j with a probability proportional to j's
        fecundity and the weight of the edge between i and j.

        Note: For a dynamic model, the method should be iterated in a loop as many 
        T times as the evolution progresses.

        Args:
            iterations: The number of times that a random strategy update occurs in one 
                        single time step.
        
        """

        for _ in range(iterations):

            # Pick a node i uniformly at random from the population (probability 1/n).
            i = self.rng.choice(np.array(self.G.nodes()))

            # Calculate probability e that node i copies the strategy of its j neighbors.
            e = [self.G.nodes[j]['F'] * self.G.edges[j,i]['w'] for j in self.G.neighbors(i)]
            e = np.array(e) / sum(e)

            # Pick a node j from which i copies its strategy.
            j = self.rng.choice(list(self.G.neighbors(i)), p=e)

            # Update strategy.
            self.G.nodes[i]['x'] = self.G.nodes[j]['x']

    def population_transition(self, p: float) -> None:

        """
        Executes an exogenous transformation of the population.

        Args:
            L: Number of network states.
            p: Probability otf remaining in the same network state.

        """

        # Generate a LxL transition matrix Q.
        # Sticky symmetric matrix
        # Or should i use a pure markov chain?
        L = self.L
        Q = np.full((L, L), (1 - p) / (L - 1))
        np.fill_diagonal(Q, p)
        self.Q = Q

        # Pick a new network state according to the transition probabilities in Q.
        new_state = self.rng.choice(L, p=Q[self.state])
        self.G = self.Graphs[new_state] 
        self.state = new_state

    def run(self, T: int, p: float, strategy_updates: int = 1) -> None:

        """
        Simulates the evolution of cooperation in a dynamic network.

        Args:
            T: Number of time steps to run the model for.
            p: Probability of remaining in the same network state.
            strategy_updates: The number of times that a random strategy update occurs in one single time step.

        """

        for t in range(T):
            self.play()
            self.update_strategy(iterations=strategy_updates)
            self.population_transition(p=p)

    def selection(self) -> str:

        """
        Evaluates the condition for selection to favor cooperation over defection in the limit of weak selection (d→0).

        Returns:
            A string indicating whether selection favors cooperation or defection.

        """

        # Compute the stationary distribution u of the transition matrix Q.
        # Source: 
        # https://datascience.oneoffcoder.com/markov-chain-stationary-distribution.html
        # 11.3. "Numpy, eig"
        S, U = np.linalg.eig(self.Q.T)
        u = list((U[:,np.isclose(S, 1)][:,0] / U[:,np.isclose(S, 1)][:,0].sum()).real)

        # Compute the reproductive value pi of a node i.
        # In this experiment, the reproductive value applied is a generalization of Fisher's
        # classical notion that accounts for environmental changes.
        # Source: ?
        # pi = ...

        # Compute expected number of steps to the most recent common ancestor of the population.
        # T = ...

        # Compute expected time to the most recent common ancestor of i and j.

        # Compute pC, the probability that a single cooperator mutant takes over a resident 
        # population of defectors
        pC = 0


        # Compute pD, the probability that a single defector mutant takes over a resident 
        # population of cooperators.
        pD = 0

        return "Selection favors cooperation." if pC > pD else "Selection favors defection."


        



         




