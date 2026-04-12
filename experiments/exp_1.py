"""
This Python script runs the first experiment of the dynamic network model.
It generates 10_000 simulations for each parameter set of 
        
        n: number of nodes from 6 to 20 (even numbers only),
        p: probability of remaining in the same state (0.2, 0.4, 0.6, 0.8),
        b: benefit coefficient , 
        c: cost coefficient, and
        b/c: benefit-to-cost ratio,

and calculates 

        pC: the average probability of a single cooperator overtaking a population of defectors,
        pD: the average probability of a single defector overtaking a population of cooperators, and
        pC > pD: whether pC is greater than pD.

The results are saved in a csv file that can be accessed in results/exp_1.csv. 
The visualizations of the results can be found in visualizations/exp_1.ipynb.
"""

import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import model as ce
import graphs as g

if __name__ == "__main__":

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
        runs = 10_000

        # Given ratios around the critical value of 7 and the cost (denominator of b/c ratio), 
        # calculate the benefit coefficient.
        ratios = [5, 6, 7, 8, 9]
        C = [1, 2, 3]
        BC = [((r * c), c) for c in C for r in ratios] # (benefit, cost) tuple

        # Probability of remaining in the same network state.
        P = [0.2, 0.4, 0.6, 0.8]

        results = []

        for n in N:

            start_time = time.time()

        # Generate a list of network structures (n must be an even number).
            Graphs = [
                g.star_complete_barbell_graph(size=n, first='star'),
                g.star_complete_barbell_graph(size=n, first='complete')]

            for p in P:

                print(f"\nN: {n}\tp: {p}\t", end='')

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

                    pC = tot_c / runs
                    pD = tot_d / runs

                    # Save results.
                    results.append({'n': n, 'p': p, 'b': b, 'c': c, 'b/c': b/c, 
                                    'pC': pC, 
                                    'pD': pD, 
                                    'pC > pD': 1 if pC > pD else 0})
                
                elapsed = time.time() - start_time
                print(f"Time (min): {int(elapsed//60)}:{int(elapsed%60):02d}\n")

        # Export results.
        pd.DataFrame(results).to_csv('results/exp_1.csv', index=False)