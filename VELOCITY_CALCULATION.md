# Asset Velocity Calculation

## Overview

This document explains how asset velocity (volatility) is calculated and used in the portfolio strategies implemented in this project.

## What is Asset Velocity?

**Asset velocity** is measured as the **standard deviation of the asset's returns**. In financial literature, this is more commonly known as **volatility**. It represents the variability or dispersion of an asset's returns over time.

## Calculation Method

### Formula

```python
velocity = returns.std()
```

Where:
- `returns` is a time series of historical asset returns
- `.std()` calculates the standard deviation

### Implementation Details

The velocity is calculated using a **rolling lookback window** (default: 50 days):

```python
# Get historical returns for the lookback period
R_n = df_returns[assets].iloc[i - lookback : i]

# Calculate velocity (volatility) for each asset
velocity = R_n.std()
```

## Applications in Portfolio Strategies

### 1. Risk Parity Portfolio

The risk parity strategy uses velocity to allocate weights **inversely proportional** to each asset's volatility:

```python
# Calculate inverse volatility
inv_volatility = 1 / velocity

# Normalize weights to sum to 1
weights = inv_volatility / inv_volatility.sum()
```

**Key Insight**: Assets with lower velocity (lower risk) receive higher weights, and vice versa.

### 2. Mean-Variance Portfolio

The mean-variance optimization uses the covariance matrix (which includes volatility) to balance risk and return:

```python
# Objective: maximize return - gamma * variance
portfolio_return = mu @ w
portfolio_variance = w @ Sigma @ w
objective = portfolio_return - gamma * portfolio_variance
```

### 3. Custom Portfolio Strategy

Combines velocity considerations with optimization to achieve better risk-adjusted returns (Sharpe ratio).

## Example

Given historical returns with different volatilities:
- Asset A: velocity = 0.01 (1% std dev)
- Asset B: velocity = 0.02 (2% std dev)
- Asset C: velocity = 0.015 (1.5% std dev)

Risk Parity weights would be:
- Asset A: ~49.3% (highest weight, lowest velocity)
- Asset B: ~23.1% (lowest weight, highest velocity)
- Asset C: ~27.6% (middle weight, middle velocity)

## Benefits

1. **Risk Management**: Velocity helps quantify the risk of each asset
2. **Diversification**: Inverse volatility weighting provides natural diversification
3. **Stability**: Lower velocity assets tend to have more stable returns

## Code References

- Risk Parity Portfolio: `Markowitz.py` lines 116-130
- Mean-Variance Portfolio: `Markowitz.py` lines 176-221
- Custom Portfolio: `Markowitz_2.py` lines 74-119
