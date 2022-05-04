
## Plot
The fit class has a function to plot

```
fit.plot(ax, label=True, x=None, **kwargs)
```

- ax is the axis object from matplotlib
- label is either a bool or a string. If True, the regression function will be written in the legend
- x is a numpy array of x values used to plot the regression. If None, then 100 points will be plotted
- **kwargs are key word arguments for matplotlib.pyplot.plot  

## Plot differential
The fit class has a function to plot the differential

```
fit.plotDifferential(ax, label=True, x=None, **kwargs)
```

- ax is the axis object from matplotlib
- label is either a bool or a string. If True, the regression function will be written in the legend
- x is a numpy array of x values used to plot the regression. If None, then 100 points will be plotted
- **kwargs are key word arguments for matplotlib.pyplot.plot  

## Scatter
The fit class has a function to scatter the data used to generate the fit.

```
fit.scatter(ax, label=True, showUncert=True, **kwargs)
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