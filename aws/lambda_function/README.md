# Backend LAMBDA Function

## Setup

### VSCODE

- install aws toolkit

  - create credentials profile
  - enter AWS IAM access key + secret access key
  - make sure the default region is region = eu-central-1
  - choose aws profile -> select the created profile

- python: create environment (3.9)
- python: select interpreter (the created one)
- run pip3 install -r requirements.txt

## Selling logic

- selling price holds --> if buyer's valuation/ask price is >= seller price -> gets item
- order only partially met --> close orginal entry and open new order with delta amount

## Order logic

- look for cheapest offer(s) until demand is met (maybe multiple small orders -> focus on cheapest buyer price)
- you may find cheaper offers than your valuation/ask price

## Possible Additional Features

- Add logic for choosing between limit prices, market price, stop price

## Development approach

We used test-driven development for developing our environment

### Used tests

- 1:1 match (BUY -> SELL; SELL -> BUY) (same price + qty)

  - sell -> buy 1:1 --> match
  - buy -> sell 1:1 --> match

  - sell -> buy 1:1 --> match
  - buy -> sell 1:1 --> match

  - price different, qty same

    - sell x, with price > x; buy with price < x
    - buy price x -> sell price y < x --> match
    - buy price x -> sell price y > x --> no match

    - sell price x -> buy price y > x --> match
    - sell price x -> buy price y < x --> no match

  - price same, qty different (INCLUDES SPLIT CASES)
    BUY PERSPECTIVE

    - qty buy < qty sell √
    - qty buy > qty sell √
    - qty buy > qty sell -> partly fill √

    SELL PERSPECTIVE

    - qty buy < qty sell √
    - qty buy < qty sqll -> partly fill √
    - qty buy > qty sell √

  - price different, qty different (INCLUDES SPLIT CASES)

    - sell x qt y -> buy u > x qt v > y
    - sell x qt y -> buy u < x qt v < y

    - sell x qt y -> buy u > x qt v < y
    - sell x qt y -> buy u < x qt v > y

    - buy x qt y -> sell u > x qt v > y
    - buy x qt y -> sell u < x qt v < y

    - buy x qt y -> sell u > x qt v < y
    - buy x qt y -> sell u < x qt v > y

- 0:0 match (buy price more expensive than sell price)
