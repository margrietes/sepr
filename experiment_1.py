"""
This Python script runs the first experiment of the dynamic network model, which
discusses the the impact of sparse and dense communities on the evolution of cooperation.

"""
import numpy as np
import pandas as pd
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

    # Number of nodes in the graph.
    N = np.arange(start=8, stop=37, step=4).tolist()

    # Number of time steps to run the model for.
    T = 100

    # Number of runs for each parameter set.
    runs = 100

    # Given ratios around the critical value of 7 and the cost (denominator of b/c ratio), 
    # calculate the benefit coefficient.
    ratios = [4, 5, 6, 7, 8, 9, 10, 12]
    C = [1, 2, 3, 5, 10]
    BC = [((r * c), c) for c in C for r in ratios] # (benefit, cost) tuple

    results = []

    for n in N:

        # Generate a list of network structures (n must be an even number).
        Graphs = [
            g.star_complete_barbell_graph(size=n, first='star'),
            g.star_complete_barbell_graph(size=n, first='complete')
        ]

        # Probability of remaining in the same network state.
        P = [1/(n*2), 1/n, 1/(n/2)]

        print(f"N: {n}")

        for p in P:

            for (b, c) in BC:

                # Run the model.
                total = 0
                for i in range(runs):
                    model = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p)
                    outcome = model.run(T=T) # savefig=True, fname='exp1'
                    total += outcome 

                # Save results.
                results.append({'n': n, 'p': p, 'b': b, 'c': c, 'b/c': b/c, 'outcome': total, 'mean_outcome': total/runs})

    # Export results.
    pd.DataFrame(results).to_csv('results.csv', index=False)