import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

if __name__ == "__main__":

    data = pd.read_csv("results/exp_1.csv")
    print(data.columns)

    sns.set_theme(style="whitegrid")

    ### Does pC > pD when b/c > 7? ###

    # Boxplot of pC > pD outcomes per b/c values
    # sns.boxplot(data=data, x="pC > pD", y="b/c", width=0.8, hue="pC > pD", legend=False, linewidth=1.6)


    ### Is 7 still the critical value for pC > pD when N ≥ 17? ###

    # Boxplot of b/c values per pC > pD outcomes for all n > 15
    # sns.boxplot(data=data[data["n"] > 15], x="n", y="b/c", width=0.6, gap = 0.1, hue="pC > pD", legend=True)


    ### Does pC > pD occur regardless of n? ###

    # Histogram of pC > pD outcomes per n
    # sns.countplot(data=data, x="n", hue="pC > pD")


    ### Does pC > pD = 1 increase with increasing p? ###

    # Total count comparison of pC > pD outcomes 0 and 1
    # sns.countplot(data=data, x="p", hue="pC > pD")

    # Frequencies of pC > pD = 1
    # sns.stripplot(data=data, x="p", y="pC > pD", alpha=0.1, size=5)
    # sns.pointplot(data=data, x="p", y="pC > pD", errorbar="ci")


    ### Other ###

    # Regression line of b/c values 
    # sns.lmplot(data=data, x="pC", y="pD", hue="b/c", scatter_kws={"s": 10, "alpha": 0.5})

    # Line plot of b/c values
    # sns.lineplot(data=data, x="pC", y="pD", hue="b/c")

    # Regression line of p values
    # sns.lmplot(data=data, x="pC", y="pD", hue="p", scatter_kws={"s": 10, "alpha": 0.5})


    plt.show()