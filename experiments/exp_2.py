"""
This Python script runs the second experiment of the dynamic network model.
It generates 100_000 simulations for each parameter set of 
        
        n: number of nodes,
        p: probability of remaining in the same state, 
        b: benefit coefficient, 
        c: cost coefficient, and
        b/c: benefit-to-cost ratio,

and calculates 

        pC: the average probability of a single cooperator overtaking a population of defectors,
        pD: the average probability of a single defector overtaking a population of cooperators, and
        pC > pD: whether pC is greater than pD.

Experiment 2 is different from Experiment 1 in that it investigates more deeply the behavior of the model
given a broader range of p and a smaller range of other parameters, as Experiment 1 could not conclude
whether increasing p leads to higher pC values (which is the conclusion given by the original study).

Additionally, Experiment 2 runs the same model for a given number of runs, instead of generating a new 
model each time.

QUESTION: Does increasing p lead to higher pC values?

The results are saved in a csv file that can be accessed in results/exp_2.csv. 
The visualizations of the results are made in visualizations/exp_2.ipynb.

"""

import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import model as ce
import graphs as g

if __name__ == "__main__":

    sample_run = False


    ### SAMPLE RUN ###

    if sample_run:

        # Specify values for a sample run.
        runs = 1000

        n = 6
        b, c = 8, 1
        P = [0.2, 0.4, 0.6, 0.8]
        
        # Generate graphs.
        Graphs = [
            g.star_complete_barbell_graph(size=n, first='star'),
            g.star_complete_barbell_graph(size=n, first='complete')
        ]

        results = []
        
        for p in P:

            print(f"Running for p = {p}...")
            start_time = time.time()

            # Initialize the two models.
            model_c = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p, strategy='single cooperator')
            model_d = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p, strategy='single defector')

            tot_c, tot_d = 0, 0

            # Run the simulation for the specified number of runs, and count the outcomes.
            for _ in range(runs):

                # Reset the models to the initial state before each run.
                model_c.reset()
                model_d.reset()

                outcome_c = model_c.run() 
                tot_c += 1 if outcome_c == 1 else 0

                outcome_d = model_d.run() 
                tot_d += 1 if outcome_d == -1 else 0

            pC = tot_c / runs
            pD = tot_d / runs

            elapsed = time.time() - start_time
            print(f"Total c: {tot_c},\tTotal d: {tot_d}")
            print(f"Time (min): {int(elapsed//60)}:{int(elapsed%60):02d}\n")

            # Save results.
            results.append({'n': n, 'p': p, 'b': b, 'c': c, 'b/c': b/c, 
                            'pC': pC, 
                            'pD': pD, 
                            'pC > pD': 1 if pC > pD else 0})

        # Export results.
        pd.DataFrame(results).to_csv('results/exp_2_sample.csv', index=False)


    ### FULL SIMULATION ###

    else:

        runs = 100_000

        N = [6, 8, 10, 12]
        P = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        # Since Experiment 1 showed that the magnitude of b and c does not affect the outcomes,
        # only a small range is needed (see visualizations/exp_1.ipynb).
        BC = [(6, 1), (7, 1), (8, 1), (9, 1)]
    
        results = []

        for n in N:

            Graphs = [
                g.star_complete_barbell_graph(size=n, first='star'),
                g.star_complete_barbell_graph(size=n, first='complete')
            ]

            for p in P:

                print(f"Running for n = {n}\tp = {p}...")
                start_time = time.time()

                for b, c in BC:

                    model_c = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p, strategy='single cooperator')
                    model_d = ce.CooperationEvolution(L=Graphs, b=b, c=c, p=p, strategy='single defector')

                    tot_c, tot_d = 0, 0

                    for _ in range(runs):
                        
                        model_c.reset()
                        model_d.reset()

                        outcome_c = model_c.run() 
                        tot_c += 1 if outcome_c == 1 else 0

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
        pd.DataFrame(results).to_csv('results/exp_2_full.csv', index=False)