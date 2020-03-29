# How To Use
![GUI Connected](https://github.com/tobigs/FunViz/blob/master/FunViz_example.gif)
# FunViz - Style Description 

#### For multiple calculation the expected growth rate is used<br/>
Current Year to (Curren Year + 2 Years)<br/>
#### In case there is no earnings forecast, the growth rate of the last two years is used<br/>
(Current Year - 2 Years) to Current Year

## Base
#### Plots earnings per share, normal multiple, dividend, stock price
If exp. growth rate < 15% -> Earnings Multiple = 15<br/>
If exp. growth rate > 15% -> Earnings Multiple = exp. growth rate
## PE(15)
#### Analogous to Base
Earnings Multiple = 15<br/>
## PEG(8.5)
#### Analogous to Base, inspired by the Benjamin Graham formula
If exp. growth rate < 0% -> Earnings Multiple = 8.5<br/>
If exp. growth rate > 0% -> Earnings Multiple = exp. growth rate + 8.5
## PE-Plot
#### Plots the PE-Ratio over the last 10 years
## FFO/OCF
#### Plots Operating Cash Flow (FFO), currently no forecasting data
OCF Multiple = 15
