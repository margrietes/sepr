"""
This Python script runs the first experiment of the dynamic network model, which
discusses the the impact of sparse and dense communities on the evolution of cooperation.

"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import model as ce
import graphs as g

if __name__ == "__main__":

    """
    When the population transitions dynamically between networks 1 and 2, cooperation is favored
    provided the benefit-to-cost ratio b/c exceeds the critical value (b/c) ≈ 7. As a result, we
    see that dynamic population structures can favor cooperation, even when all networks involved
    would each individually suppress cooperation were they static.
    
    Dynamic population structure facilitates cooperation across a wide range of population sizes
    for the pair of networks. When t1 = t2 = 1, which means that individuals each update their 
    strategy once, on average, before the network changes, cooperation can be favored by selection 
    regardless of network size, N.
    """

    sample_run = False

    ### SAMPLE RUN ###

    # The sample run saves the visualization of a simulation given one parameter set.

    if sample_run:

        n = 12
        b, c = 8, 1

        Graphs = [
                g.star_complete_barbell_graph(size=n, first='star'),
                g.star_complete_barbell_graph(size=n, first='complete')]
        
        model = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=0.75, strategy='single cooperator')
        outcome = model.run(savefig=True, fname='exp_1_single_coop')

        model = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=0.75, strategy='single defector')
        outcome = model.run(savefig=True, fname='exp_1_single_def')

        model = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=0.75, strategy='random')
        outcome = model.run(savefig=True, fname='exp_1_random_strategy')


    ### SIMULATION ###

    else:

        # Number of nodes in the graph (a list ranging from 6 to 20).
        N = np.arange(start=6, stop=21, step=2).tolist()

        # Number of runs for each parameter set.
        runs = 1000

        # Given ratios around the critical value of 7 and the cost (denominator of b/c ratio), 
        # calculate the benefit coefficient.
        ratios = [4, 5, 6, 7, 8, 9, 10]
        C = [1, 2, 3]
        BC = [((r * c), c) for c in C for r in ratios] # (benefit, cost) tuple

        # Probability of remaining in the same network state.
        P = [0.25, 0.5, 0.75]

        results = []

        for n in N:

        # Generate a list of network structures (n must be an even number).
            Graphs = [
                g.star_complete_barbell_graph(size=n, first='star'),
                g.star_complete_barbell_graph(size=n, first='complete')]

            print(f"\nN: {n}\n")

            for p in P:

                for b, c in BC:

                    # Run the model.
                    tot_c = 0
                    tot_d = 0

                    for i in range(runs):

                        model_c = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p, strategy='single cooperator') 
                        outcome_c = model_c.run() 
                        tot_c += 1 if outcome_c == 1 else 0

                        model_d = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p, strategy='single defector') 
                        outcome_d = model_d.run() 
                        tot_d += 1 if outcome_d == -1 else 0

                        pC = tot_c / 1000
                        pD = tot_d / 1000

                    # Save results.
                    results.append({'n': n, 'p': p, 'b': b, 'c': c, 'b/c': b/c, 
                                    'pC': pC, 
                                    'pD': pD, 
                                    'pC > pD': 1 if pC > pD else 0})

        # Export results.
        pd.DataFrame(results).to_csv('results/exp_1.csv', index=False)