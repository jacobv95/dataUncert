# dataUncert
Python package to perform data processing with uncertanties.

## Example
We would like to calculate <img src="https://render.githubusercontent.com/render/math?math=C=A\cdot B"> given to measurements <img src="https://render.githubusercontent.com/render/math?math=A=12.3"> and <img src="https://render.githubusercontent.com/render/math?math=B=35.1"> both with uncertanties <img src="https://render.githubusercontent.com/render/math?math=\sigma_A=2.6"> and <img src="https://render.githubusercontent.com/render/math?math=\sigma_B=8.9">. The value of <img src="https://render.githubusercontent.com/render/math?math=C"> is simply computed as <img src="https://render.githubusercontent.com/render/math?math=C=12.3\cdot 35.1 = 431.73">. The uncertanty of <img src="https://render.githubusercontent.com/render/math?math=C"> is determined using the following equation

![Figure](https://render.githubusercontent.com/render/math?math=\sigma_C = \sqrt{  \left(\frac{\partial C}{\partial A} \sigma_A\right)^2 + \left(\frac{\partial C}{\partial B} \sigma_B\right)^2 + 2\frac{\partial C}{\partial A}\frac{\partial C}{\partial B}\sigma_{AB}})




# How to install
Just run ```pip install dataUncert```