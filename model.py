"""
This Python script defines the dynamic network model that will be used to experiment
with the strategic evolution of cooperation.

"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class CooperationEvolution:

    """
    A model for the evolution of cooperation in a dynamic network 
    with exogenous transitions.

    """
    
    def __init__(self, L, c: float, b: float, p: float, d: float =0.01, seed: int =42):

        """
        Args:  
            L: A list of NetworkX graphs, assumed to be connected graphs.
            c: Cost coefficient for any Cooperator node.
            b: Benefit coefficient for any node with a Cooperator neighbor.
            p: Probability of remaining in the same network state.
            d: Selection intensity, assumed to be small or weak (d≪1).
            seed: Seed for a random number generator.

        """
        
        if not isinstance(L, list) or not all(isinstance(g, nx.Graph) for g in L):
            raise TypeError("L must be a list of NetworkX Graph objects.")

        if not all(nx.is_connected(G) for G in L):
            raise ValueError("All graphs in L must be connected.")
        
        if (c < 0) or (b < 0):
            raise ValueError("Cost and benefit must be non-negative.")

        self.L = L
        self.c = c
        self.b = b
        self.d = d

        # Define a random number generator with the given seed.
        self.rng = np.random.default_rng(seed=seed)

        # Define the initial network state.
        state = self.rng.integers(low=0, high=len(self.L))
        self.G = self.L[state]
        self.n = self.G.number_of_nodes()

        # Generate a LxL transition matrix Q (a sticky symmetric matrix).
        L = len(self.L)
        Q = np.full((L, L), (1 - p) / (L - 1))
        np.fill_diagonal(Q, p)
        self.Q = Q

        # Compute the stationary distribution u of the transition matrix Q.
        # Source: 
        # https://datascience.oneoffcoder.com/markov-chain-stationary-distribution.html (Section 11.3. "Numpy, eig")
        S, U = np.linalg.eig(self.Q.T)
        self.u = list((U[:,np.isclose(S, 1)][:,0] / U[:,np.isclose(S, 1)][:,0].sum()).real)

        # Assign a random weight between 0 and 1 to all edges of the graph.
        for G in self.L:    
            nx.set_edge_attributes(G, 0, 'w')   # Weight indicates the influence between i and j
            for _, _, data in G.edges(data=True): 
                data['w'] = self.rng.uniform(low=0.0, high=1.0)

        # Assign a strategy to each node (0: Defector, 1: Cooperator).
        # for _, data in self.G.nodes(data=True):
            # data['x'] = 0 if self.rng.random() < 0.5 else 1
        self.x = (self.rng.random(self.n) < 0.5).astype(int)

    def play(self) -> None:

        """
        Executes the donation game between all nodes with their neighbors,
        and stores the fecundity of each node in the data dictionary F of the graph.
        """

        for i in self.G.nodes():

            # Calculate accumulated payoff of node i.
            xi = self.x[i]   # "Is node i a cooperator?"
            u = 0.0
            for j in self.G.neighbors(i):
                xj = self.x[j]   # "Is node i's neighbor j a cooperator?"
                wij = self.G.edges[i,j]['w']
                u += wij * ((self.b * xj) - (self.c * xi))   # Accumulated payoff of i per edge

            # Transform accumulated payoff into fecundity.
            self.G.nodes[i]['F'] = 1 + self.d * u

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
            # self.G.nodes[i]['x'] = self.G.nodes[j]['x']
            self.x[i] = self.x[j]

    def population_transition(self) -> None:

        """
        Executes an exogenous transformation of the population.

        Args:
            L: Network states.

        """

        # Pick a new network state according to the transition probabilities in Q.
        new_state = self.rng.choice(len(self.L), p=self.Q[self.L.index(self.G)])
        self.G = self.L[new_state] 

    def run(self, T: int, strategy_updates: int = 1, visualize: bool = False) -> None:

        """
        Simulates the evolution of cooperation in a dynamic network.

        Args:
            T: Number of time steps to run the model for.
            strategy_updates: The number of times that a random strategy update occurs in one single time step.
            visualize: Whether to generate a visualization of the network state at each time step of the evolution.
        """

        self.T = T
        if visualize:
            fig, axes = plt.subplots(1, self.T, figsize=(6*T, 3))
            # if T == 1:
                # axes = [axes]
        for t in range(T):
            self.play()
            self.update_strategy(iterations=strategy_updates)
            self.population_transition()
            if visualize:
                self.visualize(fig, axes, ax=t, pos=nx.kamada_kawai_layout(self.G)) # seed=3113794652
        if visualize:
            plt.tight_layout()
            plt.show()


    def visualize(self, fig, axes, ax: int, pos) -> None:
        
        """
        Visualizes the current network state, with node colors indicating strategy (red: Cooperator, blue: Defector).
        Args:
            fig: The figure object for the visualization.
            axes: The axes object for the visualization.
            ax: The index of the current time step, used for labeling the visualization.
        """

        axt = axes[ax]
        axt.clear() 

        # Source: https://networkx.org/documentation/stable/auto_examples/drawing/plot_labels_and_colors.html
        options = {"edgecolors": "tab:gray", "node_size": 200, "alpha": 0.9}
       
        # Sync node strategies.
        nx.set_node_attributes(self.G, {i: int(self.x[i]) for i in self.G.nodes()}, "x")

        cooperators = [node for node, data in self.G.nodes(data=True) if data['x'] == 1]
        defectors = [node for node, data in self.G.nodes(data=True) if data['x'] == 0]
        labels = {n: ("C" if self.G.nodes[n].get('x', 0) == 1 else "D") for n in self.G.nodes()}

        nx.draw_networkx_nodes(self.G, pos=pos, nodelist=cooperators, node_color="tab:green", ax=axt, **options)
        nx.draw_networkx_nodes(self.G, pos=pos, nodelist=defectors, node_color="tab:red", ax=axt, **options)
        nx.draw_networkx_edges(self.G, pos=pos, edge_color="tab:gray", alpha=0.5, ax=axt)
        nx.draw_networkx_labels(self.G, pos=pos, labels=labels, font_size=10, font_color="whitesmoke", ax=axt)

        axt.set_title(f"Time step {ax+1}", fontsize=10)
        axt.set_axis_off()

    def selection(self) -> str:
        """
        Evaluates the condition for selection to favor cooperation over defection in the limit of weak selection (d→0).

        Returns:
            A string indicating whether selection favors cooperation or defection.
        """

        def random_walk_probability(b, i, j):  
            """Args: b: A network state (graph) in L; i: A node in b; j: A neighbor of i in b. Returns the probability that a random walk from i to j is taken, proportional to edge weight of i and j."""
            p_ij = b.edges[i,j]['w'] / sum(b.edges[i,k]['w'] for k in b.neighbors(i))
            return p_ij
        
        def pi():
            """Args: ..."""
            
            # The calculation applied is a generalization of Fisher's classical notion that 
            # accounts for environmental changes (see Equation 7 in Methods).

            ### APPLY LINEAR SYSTEM HERE ###
            ### CHECK THAT SUM OF PI OVER ALL NODES IN A NETWORK IS 1 ###

            return 0
        
        def coalescence_times(b_idx, i, j):
            """Args: ..."""

            if i == j:
                t = 0
            else:

                def q_tilde(b_idx, g_idx):
                    return (self.u[g_idx] / self.u[b_idx]) * self.Q[g_idx, b_idx]
            
                t = 0 ### IMPLEMENT LINEAR SYSTEM HERE TO SOLVE FOR t ###

            T = self.n * t
            return T, t
        
        def payoff(b, i):
            "Args: ..."
            T, t1 = 0, 0 # coalescence_times(ARGS)
            T, t2 = 0, 0 # coalescence_times(ARGS)
            payoff = sum((  - (T - t1) * b.edges[i,l]['w'] * self.c
                            + (T - t2) * b.edges[l,i]['w'] * self.b) for l in b.nodes())
            return payoff

        pC = 0
        pD = 0
            
        # Iterate through all network states b in L.
        for b_idx, b in enumerate(self.L):

            # Iterate through all nodes i in network state b.
            for i in b.nodes():

                # Iterate through all neighbors j of node i in network state b.
                for j in b.neighbors(i):

                    # Compute pC, the probability that a single cooperator mutant takes over a resident 
                    # population of defectors
                    pC += self.u[b_idx] * 1 ### FILL HERE ###

                    for k in b.neighbors(i):

                        # Compute pD, the probability that a single defector mutant takes over a resident 
                        # population of cooperators.
                        pD += self.u[b_idx] * 1 ### FILL HERE ###

        return "Selection favors cooperation." if pC > pD else "Selection favors defection."