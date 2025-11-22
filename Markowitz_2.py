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

    def __init__(self, price, exclude, lookback=50, gamma=0):
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
        # Lookback and construction settings
        momentum_lookback = 126          # 126 trading days (~6 months) for momentum
        min_lookback      = 126          # Minimum data requirement
        rebalance_period  = 21           # Monthly rebalance
        top_k             = 5            # Hold top 5 performing sectors

        for i in range(len(self.price)):
            # 1. Check data length
            if i < min_lookback:
                continue

            # 2. Only execute on rebalance days
            if i % rebalance_period != 0:
                continue

            current_date = self.price.index[i]

            # 3. Synchronize the calculation window for Return and Volatility
            window = self.returns.iloc[i - momentum_lookback + 1 : i + 1][assets]
            
            # Calculate cumulative return (Momentum)
            momentum = (1 + window).cumprod().iloc[-1] - 1
            
            # Calculate volatility
            volatility = window.std()

            # 4. Absolute Momentum filter, exclude assets with negative returns
            valid_assets = momentum[momentum > 0].index

            if len(valid_assets) == 0:
                self.portfolio_weights.loc[current_date] = 0.0
                continue

            # 5. Second layer stock selection: Risk-Adjusted Return (Sharpe)
            scores = momentum[valid_assets] / volatility[valid_assets]
            
            # Select the top_k with the highest CP value
            selected_assets = scores.sort_values(ascending=False).head(top_k).index

            # 6. Weight allocation: Inverse Volatility, allocate more weight to safer assets
            recent_vol = volatility[selected_assets]
            inv_vol = 1.0 / (recent_vol + 1e-8)
            weights = inv_vol / inv_vol.sum()

            # Fill in weights
            row = pd.Series(0.0, index=self.price.columns)
            for asset in selected_assets:
                row[asset] = weights[asset]

            self.portfolio_weights.loc[current_date] = row
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
