import logging
logger = logging.getLogger(__name__)
import numpy as np
import scipy.odr as odr
import string
from dataUncert.variable import variable
from dataUncert.unit import unit


class _fit():
    def __init__(self, func, x, y, p0) -> None:
        self.func = func

        if not (isinstance(x, variable) and isinstance(y, variable)):
            logger.error('The inputs has to be variables')
            raise ValueError('The inputs has to be variables')

        self.xVal = x.value
        self.yVal = y.value
        self.xUnit = x._unitObject
        self.yUnit = y._unitObject
        self.xUncert = x.uncert
        self.yUncert = y.uncert

        # uncertanties can not be 0
        if len(self.xVal) == 1:
            sx = self.xUncert if self.xUncert != 0 else 1e-10
        else:
            sx = [elem if elem != 0 else 1e-10 for elem in self.xUncert]
        if len(self.yVal) == 1:
            sy = self.yUncert if self.yUncert != 0 else 1e-10
        else:
            sy = [elem if elem != 0 else 1e-10 for elem in self.yUncert]

        # create the regression
        data = odr.RealData(self.xVal, self.yVal, sx=sx, sy=sy)
        regression = odr.ODR(data, odr.Model(self.func), beta0=p0)
        regression = regression.run()
        popt = regression.beta
        popt = [0.9 * elem for elem in popt]
        regression = odr.ODR(data, odr.Model(self.func), beta0=popt)
        regression = regression.run()
        self.popt = regression.beta

        cov = np.sqrt(np.diag(regression.cov_beta))
        self.uPopt = []
        for i in range(len(cov)):
            self.uPopt.append(np.sqrt(cov[i]**2 + regression.sd_beta[i]**2))

        self.getPoptVariables()

        # determine r-squared
        np.seterr('ignore')
        residuals = self.yVal - self.predict(self.xVal).value
        np.seterr('warn')
        y_bar = np.mean(self.yVal)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((self.yVal - y_bar)**2)
        if ss_tot != 0:
            self.r_squared = 1 - (ss_res / ss_tot)
        else:
            self.r_squared = 1

    def __str__(self):
        return self.func_name() + ',  ' + self._r2_name()

    def _r2_name(self):
        return f'$R^2 = {self.r_squared:.5f}$'

    def scatter(self, ax, label=True, showUncert=True, **kwargs):

        if all(self.xUncert == 0) and all(self.yUncert == 0):
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
            logger.error('The label has to be a string, a bool or None')
            raise ValueError('The label has to be a string, a bool or None')

        # scatter
        if showUncert:
            logger.info(f'Scattering the data on the axis {ax} with uncetanties. The label is "{label}"')
            ax.errorbar(self.xVal, self.yVal, xerr=self.xUncert, yerr=self.yUncert, linestyle='', label=label, **kwargs)
        else:
            logger.info(f'Scattering the data on the axis {ax} without uncetanties. The label is "{label}"')
            ax.scatter(self.xVal, self.yVal, label=label, **kwargs)

    def plotData(self, ax, label=True, **kwargs):

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
            logger.error('The label has to be a string, a bool or None')
            raise ValueError('The label has to be a string, a bool or None')

        logger.info(f'Plotting the data on the axis {ax}. The label is "{label}"')
        ax.plot(self.xVal, self.yVal, label=label, **kwargs)

    def predict(self, x):
        logger.info(f'Predicting the y-value using the input {x}')
        if not isinstance(x, variable):
            x = variable(x, self.xUnit)
        return self.func(self.popt, x)

    def predictDifferential(self, x):
        logger.info(f'Predicting the differential of the y-value using the input {x}')
        if not isinstance(x, variable):
            x = variable(x, self.xUnit)
        return self.d_func(self.popt, x)

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
            logger.error('The label has to be a string, a bool or None')
            raise ValueError('The label has to be a string, a bool or None')

        if x is None:
            x = np.linspace(np.min(self.xVal), np.max(self.xVal), 100)
        y = self.predict(x).value
        ax.plot(x, y, label=label, **kwargs)
        logger.info(f'Plotting the regression on the axis {ax}. The label is {label}')

    def plotDifferential(self, ax, label=True, x=None, **kwargs):

        # parse label
        if isinstance(label, str):
            label = label
        elif label == True:
            label = self.d_func_name()
        elif label == False:
            label = None
        elif label is None:
            label = None
        else:
            logger.error('The label has to be a string, a bool or None')
            raise ValueError('The label has to be a string, a bool or None')

        if x is None:
            x = np.linspace(np.min(self.xVal), np.max(self.xVal), 100)
        ax.plot(x, self.predDifferential(x), label=label, **kwargs)
        logger.info(f'Plotting the differential of the regression on the axis {ax}. The label is {label}')

    def addUnitToLabels(self, ax):
        self.addUnitToXLabel(ax)
        self.addUnitToYLabel(ax)

    def addUnitToXLabel(self, ax):
        logger.info(f'Adding the unit of the x-data to the xlabel of the axis {ax}')
        xLabel = ax.get_xlabel()
        if xLabel:
            xLabel += ' '
        xLabel += f'[{self.xUnit}]'
        ax.set_xlabel(xLabel)

    def addUnitToYLabel(self, ax):
        logger.info(f'Adding the unit of the y-data to the ylabel of the axis {ax}')
        yLabel = ax.get_ylabel()
        if yLabel:
            yLabel += ' '
        yLabel += f'[{self.yUnit}]'
        ax.set_ylabel(yLabel)


class dummy_fit(_fit):
    def __init__(self, x, y, p0=None):
        logger.info(f'Creating a dummy fitting object with the data {x} and {y}')

        if not (isinstance(x, variable) and isinstance(y, variable)):
            logger.error('The inputs has to be variables')
            raise ValueError('The inputs has to be variables')

        self.xVal = x.value
        self.yVal = y.value
        self.xUnit = x.unit
        self.yUnit = y.unit
        self.xUncert = x.uncert
        self.yUncert = y.uncert

        self.r_squared = 0
        self.popt = [variable(1, self.yUnit)]

    def func(self, B, x):
        val = self.popt[0].value
        val = [val] * len(x.value)
        return variable(val, self.yUnit)

    def d_func(self, B, x):
        val = [0] * len(x.value)
        unit = (self.popt[0] / variable(1, self.xUnit)).unit
        return variable(val, unit)

    def func_name(self):
        return f'{self.popt[0]}'

    def d_func_name(self):
        unit = (self.popt[0] / variable(1, self.xUnit)).unit
        return f'{variable(0, unit)}'


class exp_fit(_fit):
    def __init__(self, x, y, p0=[1, 1]):
        logger.info(f'Creating a exponential fitting object with the data {x} and {y} and the initial guess of {p0}')
        if len(p0) != 2:
            logger.error('You have to provide initial guesses for 2 parameters')
            raise ValueError('You have to provide initial guesses for 2 parameters')
        if x.unit != '1':
            logger.error('The variable "x" cannot have a unit')
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0)

    def getPoptVariables(self):
        logger.info('Converting the regression coefficients to variables')
        a = self.popt[0]
        b = self.popt[1]

        uA = self.uPopt[0]
        uB = self.uPopt[1]

        unitA = self.yUnit
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

    def d_func_name(self):
        return f'$a\cdot b^x\cdot \ln(b),\quad a=${self.popt[0]}$, \quad b=${self.popt[1]}'

    def func_name(self):
        return f'$a\cdot b^x,\quad a={self.popt[0].__str__(pretty = True)}, \quad b={self.popt[1].__str__(pretty = True)}$'


class pow_fit(_fit):
    def __init__(self, x, y, p0=[1, 1]):
        logger.info(f'Creating a power fitting object with the data {x} and {y} and the initial guess of {p0}')

        if len(p0) != 2:
            logger.error('You have to provide initial guesses for 2 parameters')
            raise ValueError('You have to provide initial guesses for 2 parameters')
        if x.unit != '1':
            logger.error('The variable "x" cannot have a unit')
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0)

    def getPoptVariables(self):
        logger.info('Converting the regression coefficients to variables')
        a = self.popt[0]
        b = self.popt[1]

        uA = self.uPopt[0]
        uB = self.uPopt[1]

        unitA = self.yUnit
        unitB = '1'

        a = variable(a, unitA, uA)
        b = variable(b, unitB, uB)

        self.popt = [a, b]

    def func(self, B, x):
        a = B[0]
        b = B[1]
        return a * x**b

    def d_func(self, B, x):
        a = B[0]
        b = B[1]
        return a * b * x**(b - 1)

    def d_func_name(self):
        return f'$a b x^{{b-1}},\quad a=${self.popt[0]}$, \quad b=${self.popt[1]}'

    def func_name(self):
        return f'$a x^b,\quad a={self.popt[0].__str__(pretty = True)}, \quad b={self.popt[1].__str__(pretty = True)}$'


def lin_fit(x, y, p0=None):
    return pol_fit(x, y, deg=1, p0=p0)


class pol_fit(_fit):
    def __init__(self, x, y, deg=2, terms=None, p0=None):
        if terms is None:
            terms = [True] * (deg + 1)
        else:
            for term in terms:
                if not str(type(term)) == "<class 'bool'>":
                    logger.error('All elements in "terms" has to be booleans')
                    raise ValueError('All elements in "terms" has to be booleans')
            if len(terms) > deg + 1:
                logger.error(f'You have specified to use {len(terms)} terms, but you can only use {deg+1} using a polynomial of degree {deg}')
                raise ValueError(f'You have specified to use {len(terms)} terms, but you can only use {deg+1} using a polynomial of degree {deg}')
        self.terms = terms

        if p0 is None:
            p0 = [1] * sum(1 for elem in self.terms if elem)

        self.deg = deg

        logger.info(f'Creating a polynomial fitting object with the data {x} and {y} and the initial guess of {p0}')
        _fit.__init__(self, self.func, x, y, p0=p0)

    def getPoptVariables(self):
        logger.info('Converting the regression coefficients to variables')
        popt = []
        n = self.deg
        index = 0
        for i in range(n + 1):
            if self.terms[i]:
                value = self.popt[index]
                uncert = self.uPopt[index]
                u = self.yUnit
                if i != n:
                    u /= unit(self.xUnit ** (n - i))
                var = variable(value, u, uncert)
                popt.append(var)
                index += 1

        self.popt = popt

    def func(self, B, x):
        out = 0
        n = self.deg
        index = 0
        for i in range(n + 1):
            if self.terms[i]:
                out += B[index] * x**(n - i)
                index += 1
        return out

    def d_func(self, B, x):
        out = 0
        n = self.deg
        index = 0
        for i in range(n):
            if self.terms[i]:
                out += (n - i) * B[index] * x**(n - i - 1)
        return out

    def d_func_name(self):
        out = ''
        n = self.deg
        for i in range(n):
            if self.terms[i]:
                exponent = n - i - 1
                coefficient = n - i
                if out:
                    out += '+'
                if coefficient != 1:
                    out += f'{coefficient}'

                out += f'{string.ascii_lowercase[i]}'

                if exponent != 0:
                    out += f'$x$'
                if exponent > 1:
                    out += f'$^{exponent}$'

        index = 0
        for i in range(n):
            if self.terms[i]:
                out += f', {string.ascii_lowercase[i]}={self.popt[index].__str__(pretty = True)}'
                index += 1
        return out

    def func_name(self):
        out = '$'
        n = self.deg
        for i in range(n + 1):
            if self.terms[i]:
                exponent = n - i
                if i == 0:
                    out += f'{string.ascii_lowercase[i]}'
                else:
                    out += f'+{string.ascii_lowercase[i]}'
                if exponent != 0:
                    out += f'x'
                if exponent > 1:
                    out += f'^{exponent}'
        index = 0
        for i in range(n + 1):
            if self.terms[i]:
                out += f', {string.ascii_lowercase[i]}={self.popt[index].__str__(pretty = True)}'
                index += 1
        out += '$'
        return out


class logistic_fit(_fit):
    def __init__(self, x, y, p0=[1, 1, 1]):
        logger.info(f'Creating a logistic fitting object with the data {x} and {y} and the initial guess of {p0}')
        if len(p0) != 3:
            logger.error('You have to provide initial guesses for 3 parameters')
            raise ValueError('You have to provide initial guesses for 3 parameters')
        if x.unit != '1':
            logger.error('The variable "x" cannot have a unit')
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0)

    def getPoptVariables(self):
        logger.info('Converting the regression coefficients to variables')
        L = self.popt[0]
        k = self.popt[1]
        x0 = self.popt[2]

        uL = self.uPopt[0]
        uK = self.uPopt[1]
        uX0 = self.uPopt[2]

        unitL = self.yUnit
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

    def d_func_name(self):
        L = self.popt[0]
        k = self.popt[1]
        x0 = self.popt[2]

        out = f'$\\frac{{k\cdot L \cdot e^{{-k\cdot (x-x_0)}}}}{{\\left(1 + e^{{-k\cdot (x-x_0)}}\\right)}}$'
        out += f'$\quad L={L}$, '
        out += f'$\quad k={k}$, '
        out += f'$\quad x_0={x0}$'
        return out

    def func_name(self):
        L = self.popt[0].__str__(pretty=True)
        k = self.popt[1].__str__(pretty=True)
        x0 = self.popt[2].__str__(pretty=True)

        out = f'$\\frac{{L}}{{1 + e^{{-k\cdot (x-x_0)}}}}'
        out += f'\quad L={L}'
        out += f'\quad k={k}'
        out += f'\quad x_0={x0}$'
        return out


class logistic_100_fit(_fit):
    def __init__(self, x, y, p0=[0, 0]):
        logger.info(f'Creating a logistic100 fitting object with the data {x} and {y} and the initial guess of {p0}')

        if len(p0) != 2:
            logger.error('You have to provide initial guesses for 2 parameters')
            raise ValueError('You have to provide initial guesses for 2 parameters')
        if x.unit != '1':
            logger.error('The variable "x" cannot have a unit')
            raise ValueError('The variable "x" cannot have a unit')
        _fit.__init__(self, self.func, x, y, p0=p0)

    def getPoptVariables(self):
        logger.info('Converting the regression coefficients to variables')
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
        k = B[0]
        x0 = B[1]
        if isinstance(k, variable):
            L = variable(100, self.yUnit)
        else:
            L = 100
        return L / (1 + np.exp(-k * (x - x0)))

    def d_func(self, B, x):
        L = 100
        k = B[0]
        x0 = B[1]
        return k * L * np.exp(-k * (x - x0)) / ((np.exp(-k * (x - x0)) + 1)**2)

    def d_func_name(self):
        k = self.popt[0]
        x0 = self.popt[1]

        out = f'$\\frac{{k\cdot 100 \cdot e^{{-k\cdot (x-x_0)}}}}{{\\left(1 + e^{{-k\cdot (x-x_0)}}\\right)}}$'
        out += f'$\quad k={k}$, '
        out += f'$\quad x_0={x0}$'
        return out

    def func_name(self):
        k = self.popt[0].__str__(pretty=True)
        x0 = self.popt[1].__str__(pretty=True)

        out = f'$\\frac{{100}}{{1 + e^{{-k\cdot (x-x_0)}}}}'
        out += f'\quad k={k}'
        out += f'\quad x_0={x0}$'
        return out

