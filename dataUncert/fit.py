import numpy as np
import math
import scipy.odr as odr
from copy import copy
import string
try:
    from dataUncert.variable import variable
except ModuleNotFoundError:
    from variable import variable
try:
    from dataUncert.unitSystem import unit as unitConversion
except ModuleNotFoundError:
    from unitSystem import unit as unitConversion


class _fit():
    def __init__(self, func, x, y, p0, n_significant=3) -> None:
        self.n_significant = n_significant
        self.func = func

        self.x = copy(x)
        self.y = copy(y)

        # uncertanties can not be 0
        sx = [elem if elem != 0 else 1e-10 for elem in self.x.uncert]
        sy = [elem if elem != 0 else 1e-10 for elem in self.y.uncert]

        # add pertubation to initial guess. This helps if the initial guess is the solution
        p0 = [elem + np.random.rand() * 1e-5 for elem in p0]

        # create the regression
        data = odr.RealData(self.x.value, self.y.value, sx=sx, sy=sy)
        regression = odr.ODR(data, odr.Model(self.func), beta0=p0)
        regression = regression.run()
        self.popt = regression.beta
        self.conv = regression.cov_beta
        self.uPopt = np.sqrt(np.diag(regression.cov_beta))

        # turn the elements of popt in to pyees variables
        self.getPoptVariables()

        # determine r-squared
        residuals = self.y.value - self.pred(self.x.value)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((self.y.value - np.mean(self.y.value))**2)
        if ss_tot != 0:
            self.r_squared = 1 - (ss_res / ss_tot)
        else:
            self.r_squared = 1

    def __str__(self):
        return self.func_name() + ',  ' + self.r2_name()

    def r2_name(self):
        return f'$R^2 = {self.r_squared:.5f}$'

    def scatter(self, ax, label=True, showUncert=True, **kwargs):

        if all(self.x.uncert == 0) and all(self.y.uncert == 0):
            showUncert = False

        # parse label
        if isinstance(label, str):
            label = label
        elif label == True:
            label = 'Data'
        elif label == False:
            label = None
        elif label is None:
            label = None
        else:
            raise ValueError('The label has to be a string, a bool or None')

        # scatter
        if showUncert:
            ax.errorbar(self.x.value, self.y.value, xerr=self.x.uncert, yerr=self.y.uncert, linestyle='None', label=label, **kwargs)
        else:
            ax.scatter(self.x.value, self.y.value, label=label, **kwargs)

    def pred(self, x):
        return self.func([elem.value for elem in self.popt], x)

    def plot(self, ax, label=True, x=None, **kwargs):

        # parse label
        if isinstance(label, str):
            label = label
        elif label == True:
            label = self.__str__()
        elif label == False:
            label = None
        elif label is None:
            label = None
        else:
            raise ValueError('The label has to be a string, a bool or None')

        if x is None:
            x = np.linspace(np.min(self.x.value), np.max(self.x.value), 100)
        ax.plot(x, self.pred(x), label=label, **kwargs)

    def decimalString(self, x, includeSign):
        n_zeros = math.ceil(-math.log10(np.abs(x)))
        if includeSign:
            return f'{x:+.{n_zeros + self.n_significant-1:d}f}'
        else:
            return f'{x:.{n_zeros + self.n_significant-1:d}f}'

    def addUnitToLabels(self, ax):
        self.addUnitToXLabel(ax)
        self.addUnitToYLabel(ax)

    def addUnitToXLabel(self, ax):
        xLabel = ax.get_xlabel()
        if xLabel:
            xLabel += ' '
        xLabel += f'[{self.x.unit}]'
        ax.set_xlabel(xLabel)

    def addUnitToYLabel(self, ax):
        yLabel = ax.get_ylabel()
        if yLabel:
            yLabel += ' '
        yLabel += f'[{self.y.unit}]'
        ax.set_ylabel(yLabel)


class exp_fit(_fit):
    def __init__(self, x, y, p0=[1, 1], n_sifnificant=3):
        if len(p0) != 2:
            raise ValueError('You have to provide initial guesses for 2 parameters')
        if x.unit != '1':
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0, n_significant=n_sifnificant)

    def getPoptVariables(self):
        a = self.popt[0]
        b = self.popt[1]

        uA = self.uPopt[0]
        uB = self.uPopt[1]

        unitA = self.y.unit
        unitB = '1'

        a = variable(a, unitA, uA)
        b = variable(b, unitB, uB)

        self.popt = [a, b]

    def func(self, B, x):
        a = B[0]
        b = B[1]
        return a * b**x

    def d_func(self, B, x):
        a = B[0]
        b = B[1]
        return a * b**x * np.log(b)

    def func_name(self):
        return f'$a\cdot b^x,\quad a=${self.popt[0]}$, \quad b=${self.popt[1]}'


class pow_fit(_fit):
    def __init__(self, x, y, p0=[0, 0], n_sifnificant=3):
        if len(p0) != 2:
            raise ValueError('You have to provide initial guesses for 2 parameters')
        if x.unit != '1':
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0, n_significant=n_sifnificant)

    def getPoptVariables(self):
        a = self.popt[0]
        b = self.popt[1]

        uA = self.uPopt[0]
        uB = self.uPopt[1]

        unitA = self.y.unit
        unitB = '1'

        a = variable(a, unitA, uA)
        b = variable(b, unitB, uB)

        self.popt = [a, b]

    def func(self, B, x):
        a = B[0]
        b = B[1]
        return a * x**b

    def d_func(self, x, a, b):
        return a * b * x**(b - 1)

    def func_name(self):
        return f'$a\cdot x^b,\quad a=${self.popt[0]}$, \quad b=${self.popt[1]}'


def lin_fit(x, y, p0=[0, 0], n_sifnificant=3):
    return pol_fit(x, y, deg=1, p0=p0, n_sifnificant=n_sifnificant)


class pol_fit(_fit):
    def __init__(self, x, y, deg=2, p0=None, n_sifnificant=3):
        if p0 is None:
            p0 = [0] * (deg + 1)
        if deg + 1 != len(p0):
            raise ValueError('The length of the initial guess has to have one more element than the polynomial degree')
        self.deg = deg
        _fit.__init__(self, self.func, x, y, p0=p0, n_significant=n_sifnificant)

    def getPoptVariables(self):
        popt = []
        n = self.deg
        u = unitConversion()
        unitY = self.y.unit
        unitX = self.x.unit
        for i in range(n + 1):
            value = self.popt[i]
            uncert = self.uPopt[i]
            lower = u._power(unitX, n - i)
            unit = u._divide(unitY, lower)
            var = variable(value, unit, uncert)
            popt.append(var)
        self.popt = popt

    def func(self, B, x):
        out = 0
        n = self.deg
        for i in range(self.deg + 1):
            out += B[i] * x**(n - i)
        return out

    def d_func(self, B, x):  # TODO
        a = B[0]
        b = B[1]
        return a

    def func_name(self):  # TODO
        out = ''
        n = self.deg
        for i in range(n + 1):
            exponent = n - i
            if not out:
                out += f'{string.ascii_lowercase[i]}'
            else:
                out += f'+{string.ascii_lowercase[i]}'
            if exponent != 0:
                out += f'$x$'
            if exponent > 1:
                out += f'$^{exponent}$'

        for i in range(n + 1):
            out += f', {string.ascii_lowercase[i]}={self.popt[i]}'
        return out


class logistic_fit(_fit):
    def __init__(self, x, y, p0=[0, 0, 0], n_sifnificant=3):
        if len(p0) != 3:
            raise ValueError('You have to provide initial guesses for 3 parameters')
        if x.unit != '1':
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0, n_significant=n_sifnificant)

    def getPoptVariables(self):
        L = self.popt[0]
        k = self.popt[1]
        x0 = self.popt[2]

        uL = self.uPopt[0]
        uK = self.uPopt[1]
        uX0 = self.uPopt[2]

        unitL = self.y.unit
        unitK = '1'
        unitX0 = '1'

        L = variable(L, unitL, uL)
        k = variable(k, unitK, uK)
        x0 = variable(x0, unitX0, uX0)

        self.popt = [L, k, x0]

    def func(self, B, x):
        L = B[0]
        k = B[1]
        x0 = B[2]
        return L / (1 + np.exp(-k * (x - x0)))

    def d_func(self, B, x):
        L = B[0]
        k = B[1]
        x0 = B[2]
        return k * L * np.exp(-k * (x - x0)) / ((np.exp(-k * (x - x0)) + 1)**2)

    def func_name(self):
        L = self.popt[0]
        k = self.popt[1]
        x0 = self.popt[2]

        out = f'$\\frac{{L}}{{1 + e^{{-k\cdot (x-x_0)}}}}$'
        out += f'$\quad L={L}$'
        out += f'$\quad k={k}$'
        out += f'$\quad x_0={x0}$'
        return out


class logistic_100_fit(_fit):
    def __init__(self, x, y, p0=[0, 0], n_sifnificant=3):
        if len(p0) != 2:
            raise ValueError('You have to provide initial guesses for 2 parameters')
        if x.unit != '1':
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0, n_significant=n_sifnificant)

    def getPoptVariables(self):
        k = self.popt[0]
        x0 = self.popt[1]

        uK = self.uPopt[0]
        uX0 = self.uPopt[1]

        unitK = '1'
        unitX0 = '1'

        k = variable(k, unitK, uK)
        x0 = variable(x0, unitX0, uX0)

        self.popt = [k, x0]

    def func(self, B, x):
        L = 100
        k = B[0]
        x0 = B[1]
        return L / (1 + np.exp(-k * (x - x0)))

    def d_func(self, B, x):
        L = 100
        k = B[0]
        x0 = B[1]
        return k * L * np.exp(-k * (x - x0)) / ((np.exp(-k * (x - x0)) + 1)**2)

    def func_name(self):
        k = self.popt[0]
        x0 = self.popt[1]

        out = f'$\\frac{{100}}{{1 + e^{{-k\cdot (x-x_0)}}}}$'
        out += f'$\quad k={k}$'
        out += f'$\quad x_0={x0}$'
        return out
