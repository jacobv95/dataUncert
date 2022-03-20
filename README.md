# dataUncer
Python package to perform data processing with uncertanties.

# Importing data

Data can be imported using the function "readData"

```
dat = readData(xlFile: str, dataStartCol: str, dataEndCol: str, uncertStartCol=None, uncertEndCol=None)
```
 - xlFile - path to the excel file to be read
 - dataStartCol - The name of the first coloumn with the data
 - dataEndCol - The name of the last coloumn with the data
 - uncertStartCol - The name of the first coloumn with the data
 - uncertEndCol - The name of the last coloumn with the data

The excel file has to follow the following structure:
 - The first row is the header
 - The second row is the unit of the data
 - If uncertanty data is given, there has to be an equal number of coloums in the uncertanty range as there is in the data range

The uncertanty can follow one of two structures:
 1. There is one row of uncertanty per row in the range of data.
 2. There is one matrix of size nxn for each row in the range of data, where n is the number of different measurements

Structure 1 is used if only the uncertanty of the measurement is known. Structure 2 is unsed if covariance between the measurements are known as well.

Two examples are given:
![Example 1](/examples/example1.png)
![Example 2](/examples/example2.png)

```
from dataUncert import *

dat1 = readData('example1.xlsx', 'A', 'B', 'C', 'D')
q1 = dat1.s1.a + dat1.s1.b
print(q1)
>> [85.0] +/- [0.632] [m]

dat2 = readData('example2.xlsx', 'A', 'B', 'C', 'D')
q2 = dat2.s1.a + dat2.s1.b
print(q2)
>> [85.0] +/- [2.28] [m]
```

Notice that the uncertanty of q2 is larger than the uncertanty of q1. This is because example1.xlsx includes information about the covariance of the measurement of a and b.

Notice that both dat1 and dat2 has an object called s1. That is because the data for a and b are both located on sheet 1 of the .xlsx file.


# Variables

You can create a variables as follows

```
var = variable(val: float, unit: str, uncert=None)
```

The units work as expected:
 - Two variables can be added together if their units are identical
 - Any two units can be multiplied or divided
 - Exponents cannot have any units

The denominator and the numerator of the unit is seperated using a dash (/).
The in the denominator or numerator are sperated using a hyphen (-)

Here are some examples:
 - milli Liters per minute:               'mL/min'
 - Cubicmeter-kilogram per second:  'm3-kg/s

The following units are known:
 - unitless: 1
 - force: N
 - mass: g
 - Energy: J
 - power: W
 - pressure: Pa, bar
 - Temperature: K, C, F
 - time: s, min, h, yr
 - volume: m3, L
 - length: m
 - current: A
 - Voltage: V

The following prefixes are known:
 - µ: 1e-6 (ASCII 230)
 - m: 1e-3
 - k: 1e3
 - M: 1e6

# Fitting
The package includes a tool to produce fits. The following fits are known
 - Linear fit
 - Polynomial fit
 - Power fit
 - Exponential fit
 - Logistic fit
 - Logistic fit with a fixed maximum value of 100

```
F_lin = lin_fit(x: variable,y: variable)
F_pol = pol_fit(x: variable,y: variable, deg:int = 2)
F_pow = pow_fit(x: variable,y: variable)
F_exp = exp_fit(x: variable,y: variable)
F_logistic = logistic_fit(x: variable,y: variable)
F_logistic_100 = logistic_100_fit(x: variable,y: variable)
```



## Plot
The fit class has a function to plot

```
F = lin_fit(x: variable,y: variable)
F.plot(ax, label=True, x=None, **kwargs)
```

- ax is the axis object from matplotlib
- label is either a bool or a string. If True, the regression function will be written in the legend
- x is a numpy array of x values used to plot the regression. If None, then 100 points will be plotted
- **kwargs are key word arguments for matplotlib.pyplot.plot  


## Scatter
The fit class has a function to scatter

```
F = lin_fit(x: variable,y: variable)
F.scatter(ax, label=True, showUncert=True, **kwargs)
```

- ax is the axis object from matplotlib
- label is either a bool or a string. If True, the word "Data" is printed in the legend
- showUncert is a bool. Errorbars are shown if true
- **kwargs are key word arguments for matplotlib.pyplot.scatter  

## Axis labels
The fit class has a function to set the units of the axis

```
F = lin_fit(x: variable,y: variable)
F.addUnitToLabels(ax)
F.addUnitToXLabel(ax)
F.addUnitToYLabel(ax)
```

The unit of the data parsed when initializing the fit object will be appended to the axis labels

## Example
```
import matplotlib.pyplot as plt
from dataUncert import variable

fig, ax = plt.subplots()
x = variable([10,20,30,40], 'm', uncert = [1,2,3,4])
y = variable([1,2,3,4], 'C', uncert = [0.2, 0.4, 0.6, 0.8])
F_pol = pol_fit(x, y, deg = 2)
fig, ax = plt.subplots()
F_pol.plot(ax)
F_pol.scatter(ax)
F_pol.addUnitToLabels(ax)
ax.legend()
plt.show()
```

![Fitting example](/examples/fitExample.png)