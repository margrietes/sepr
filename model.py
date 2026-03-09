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
    
    def __init__(self, L, b: float, c: float, p: float, strategy: str = 'random', d: float =0.01):

        """
        Args:  
            L: A list of NetworkX graphs, assumed to be connected graphs.
            b: Benefit coefficient for any node with a Cooperator neighbor.
            c: Cost coefficient for any Cooperator node.
            p: Probability of remaining in the same network state.
            strategy: 'random' (default), 'single cooperator' or 'single defector', to assign one cooperator mutant to a population of defectors.
            d: Selection intensity, with default assumed to be small or weak (d≪1).

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
        self.rng = np.random.default_rng() # seed=42

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
        # Source: https://datascience.oneoffcoder.com/markov-chain-stationary-distribution.html 
        # (Section 11.3. "Numpy, eig")
        S, U = np.linalg.eig(self.Q.T)
        self.u = list((U[:,np.isclose(S, 1)][:,0] / U[:,np.isclose(S, 1)][:,0].sum()).real)

        # Assign a random weight between 0 and 1 to all edges of the graph.
        for G in self.L:    
            nx.set_edge_attributes(G, 0, 'w')   # Weight indicates the influence between i and j
            for _, _, data in G.edges(data=True): 
                data['w'] = self.rng.uniform(low=0.0, high=1.0)

        if strategy == 'random':
            # Assign a strategy to each node (0: Defector, 1: Cooperator).
            self.x = (self.rng.random(self.n) < 0.5).astype(int)
        elif strategy == 'single cooperator':
            # Assign Defector strategy to all nodes.
            self.x = np.zeros(self.n, dtype=int)
            # Select a random node to transform into Cooperator.
            self.x[self.rng.integers(self.n)] = 1
        elif strategy == 'single defector':
            # Assign Cooperator strategy to all nodes.
            self.x = np.ones(self.n, dtype=int)
            # Select a random node to transform into Defector.
            self.x[self.rng.integers(self.n)] = 0
        else: 
            raise ValueError("Strategy must be 'random', 'single cooperator', or 'single defector'.")

        self.outcome = -1111

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
            self.G.nodes[i]['F'] = np.exp(self.d * u)

    def update_strategy(self, iterations=1) -> None:

        """
        Selects a random node i from the population, and updates its strategy 
        by copying the strategy of a neighbor j with a probability proportional to j's
        fecundity and the weight of the edge between i and j.

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
        """

        # Pick a new network state according to the transition probabilities in Q.
        new_state = self.rng.choice(len(self.L), p=self.Q[self.L.index(self.G)])
        # print(f"{self.L.index(self.G)} -> {new_state}")
        self.G = self.L[new_state] 

    def run(self, max_steps: int = 500, strategy_updates: int = 1, savefig: bool = False, fname: str = '') -> None:

        """
        Simulates the evolution of cooperation in a dynamic network.

        Args:
            max_steps: Maximum steps of running the simulation.
            strategy_updates: The number of times that a random strategy update occurs in one single time step.
            savefig: Whether to save a visualization of the run. 
            fname: Name to save the figure with.
        """

        frames = []
        t = 0

        # Run the evolution.
        while len(set(self.x)) > 1 and t < max_steps:
            self.play()
            self.update_strategy(iterations=strategy_updates)
            self.population_transition()
            if savefig:
                frames.append((self.x.copy(), self.L.index(self.G)))
            t += 1
                
        if len(set(self.x)) == 1:
            self.outcome = 1 if self.x[0] == 1 else -1
        else:
            self.outcome = 0

        if savefig:

            # Create the canvas for the visualization.
            T = len(frames)
            ncols = min(10, T)
            nrows = int(np.ceil(T/ncols))
            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(2*ncols, 2*nrows))
            if nrows == 1:
                axes = axes.reshape(1, -1)
            pos = nx.kamada_kawai_layout(self.G)

            # Visualize each time step.
            for t, (x, g) in enumerate(frames):
                self.x = x
                self.G = self.L[g]
                row = int(t // ncols)
                col = int(t % ncols)
                ax = axes[row, col]

                self.visualize(ax=ax, pos=pos, t=t)

            # Hide empty axes.
            for empty in range(T, nrows * ncols):
                row = empty // ncols
                col = empty % ncols
                axes[row, col].set_visible(False)

            plt.tight_layout()
            plt.savefig(fname=f'figures/{fname}')

        return self.outcome

    def visualize(self, ax, pos, t: int) -> None:
        
        """
        Visualizes the current network state, with node colors indicating strategy (green: Cooperator, red: Defector).
        Args:
            ax: The [nrows, ncols] index of the current time step, used for labeling the visualization.
            pos: The node layout mapping.
            t: The time step that is being visualized.
        """

        ax.clear() 

        # Source: https://networkx.org/documentation/stable/auto_examples/drawing/plot_labels_and_colors.html
        options = {"edgecolors": "tab:gray", "node_size": 130, "alpha": 0.9}
       
        # Sync node strategies.
        nx.set_node_attributes(self.G, {i: int(self.x[i]) for i in self.G.nodes()}, "x")

        cooperators = [i for i in self.G.nodes() if self.x[i] == 1]
        defectors   = [i for i in self.G.nodes() if self.x[i] == 0]
        labels = {n: ("C" if self.G.nodes[n].get('x', 0) == 1 else "D") for n in self.G.nodes()}

        nx.draw_networkx_nodes(self.G, pos=pos, nodelist=cooperators, node_color="tab:green", ax=ax, **options)
        nx.draw_networkx_nodes(self.G, pos=pos, nodelist=defectors, node_color="tab:red", ax=ax, **options)
        nx.draw_networkx_edges(self.G, pos=pos, edge_color="tab:gray", alpha=0.3, ax=ax)
        nx.draw_networkx_labels(self.G, pos=pos, labels=labels, font_size=8, font_color="whitesmoke", ax=ax)

        ax.set_title(f"Time step {t+1}", fontsize=10)
        ax.set_axis_off()

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