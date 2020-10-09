# arbi

# Terminology:

## Exchange:
An exchange is anything that has basic exchange functionality-- get a buy price, get a sell price, set a buy order, set a sell order, cancel an order, etc.

## Strategy:
A strategy is the logic that you use to trade. For example: "set a buy order 1% below current price, and a sell order 1% above current price"

# Current Architecture:

The test_strategy.py file pulls in a conifg with exchanges authenticated. It sets up some trades depending on the strategy using the clients. Then it waits for the trades to finish before starting another one.

# Proposed Future Architecture:

Strategy execution should be abstracted and event based. When an event comes in the strategy executor evaluates the event against the conditions of the strategy and if the conditions are met, it executes the action specified in the strategy.

Strategies have the following components:

1. Exchanges
2. Conditions
3. Actions
4. Custom attributes relevant to the specific strategy

Strategy executor should process events from a queue and should use a recvWindow to determine event validity.


# Running:

Right now I'm still working on refactoring, so currently you run this from the project dir like this `python3 -m strategy.steps.test_strategy`

# Explanation of strategies:

## Paired Trade Strategy:

This strategy sets a limit buy and a limit sell above and below the current price. It waits for both trades to execute before starting a new pair. This model assumes the prices fluctuates up and down, but remains relatively stable overall. In the event that the price changes dramatically and doesn't return, there is cancellation logic. Currently I think the cancellation timeout is set to 1 week. In the event that only 1 of the paired trades is executed, and the other doesn't execute withint the cancellation timeout, the remaining open trade will be cancelled and the strategy will restart at the current price.

## Stop Trade Strategy:

This strategy watches for large price movements. When the price moves significantly, it will place a stop loss (if the price has moved up) or a take profit (if the price has moved down) either below (stop loss) or above (take profit) the price. It will wait for the order to execute. If the order does not execute and the price continues moving, the strategy will move the order so that it stays a at most x% away from the current price (where x is a defined threshhold). This strategy does not have cancellation logic. It will continue until the trade executes.