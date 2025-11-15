"""
Package Import
"""
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import quantstats as qs
import gurobipy as gp
import warnings
import argparse
import sys

"""
Project Setup
"""
warnings.simplefilter(action="ignore", category=FutureWarning)

assets = [
    "SPY",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
]

# Initialize Bdf and df
Bdf = pd.DataFrame()
for asset in assets:
    raw = yf.download(asset, start="2012-01-01", end="2024-04-01", auto_adjust = False)
    Bdf[asset] = raw['Adj Close']

df = Bdf.loc["2019-01-01":"2024-04-01"]

"""
Strategy Creation

Create your own strategy, you can add parameter but please remain "price" and "exclude" unchanged
"""


class MyPortfolio:
    """
    NOTE: You can modify the initialization function
    """

    def __init__(self, price, exclude, lookback=50, gamma=100):
        self.price = price
        self.returns = price.pct_change().fillna(0)
        self.exclude = exclude
        self.lookback = lookback
        self.gamma = gamma

    def calculate_weights(self):
        # Get the assets by excluding the specified column
        assets = self.price.columns[self.price.columns != self.exclude]

        # Calculate the portfolio weights
        self.portfolio_weights = pd.DataFrame(
            index=self.price.index, columns=self.price.columns
        )

        """
        TODO: Complete Task 4 Below
        """
        
        for i in range(self.lookback + 1, len(self.price)):
            # Get the historical returns for the lookback period
            R_n = self.returns.copy()[assets].iloc[i - self.lookback : i]
            
            # Calculate mean returns and covariance matrix
            mu = R_n.mean().values
            Sigma = R_n.cov().values
            n = len(assets)
            
            # Use Gurobi for mean-variance optimization
            with gp.Env(empty=True) as env:
                env.setParam("OutputFlag", 0)
                env.setParam("DualReductions", 0)
                env.start()
                with gp.Model(env=env, name="portfolio") as model:
                    # Decision variable: portfolio weights
                    w = model.addMVar(n, name="w", lb=0, ub=1)
                    
                    # Objective: maximize Sharpe-like ratio (return/risk)
                    # Using a higher gamma for risk penalty to achieve better Sharpe ratio
                    portfolio_return = mu @ w
                    portfolio_variance = w @ Sigma @ w
                    
                    # Set gamma to balance risk and return for better Sharpe ratio
                    model.setObjective(
                        portfolio_return - self.gamma * portfolio_variance, 
                        gp.GRB.MAXIMIZE
                    )
                    
                    # Constraint: weights sum to 1 (no leverage)
                    model.addConstr(w.sum() == 1, "budget")
                    
                    model.optimize()
                    
                    if model.status == gp.GRB.OPTIMAL or model.status == gp.GRB.SUBOPTIMAL:
                        solution = []
                        for j in range(n):
                            var = model.getVarByName(f"w[{j}]")
                            solution.append(var.X)
                        self.portfolio_weights.loc[self.price.index[i], assets] = solution
        
        """
        TODO: Complete Task 4 Above
        """

        self.portfolio_weights.ffill(inplace=True)
        self.portfolio_weights.fillna(0, inplace=True)

    def calculate_portfolio_returns(self):
        # Ensure weights are calculated
        if not hasattr(self, "portfolio_weights"):
            self.calculate_weights()

        # Calculate the portfolio returns
        self.portfolio_returns = self.returns.copy()
        assets = self.price.columns[self.price.columns != self.exclude]
        self.portfolio_returns["Portfolio"] = (
            self.portfolio_returns[assets]
            .mul(self.portfolio_weights[assets])
            .sum(axis=1)
        )

    def get_results(self):
        # Ensure portfolio returns are calculated
        if not hasattr(self, "portfolio_returns"):
            self.calculate_portfolio_returns()

        return self.portfolio_weights, self.portfolio_returns


if __name__ == "__main__":
    # Import grading system (protected file in GitHub Classroom)
    from grader_2 import AssignmentJudge
    
    parser = argparse.ArgumentParser(
        description="Introduction to Fintech Assignment 3 Part 12"
    )

    parser.add_argument(
        "--score",
        action="append",
        help="Score for assignment",
    )

    parser.add_argument(
        "--allocation",
        action="append",
        help="Allocation for asset",
    )

    parser.add_argument(
        "--performance",
        action="append",
        help="Performance for portfolio",
    )

    parser.add_argument(
        "--report", action="append", help="Report for evaluation metric"
    )

    parser.add_argument(
        "--cumulative", action="append", help="Cumulative product result"
    )

    args = parser.parse_args()

    judge = AssignmentJudge()
    
    # All grading logic is protected in grader_2.py
    judge.run_grading(args)
