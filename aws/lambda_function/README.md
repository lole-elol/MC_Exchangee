# matchmaking_server

## VSCODE

- install aws toolkit

  - create credentials profile
  - enter access key + secret access key from discord
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