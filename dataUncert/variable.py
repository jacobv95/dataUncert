import logging
logger = logging.getLogger(__name__)
import numpy as np
from dataUncert.unit import unit

HANDLED_FUNCTIONS = {}


class variable():
    def __init__(self, value, unitStr='', uncert=None, nDigits=3) -> None:

        logger.info(f'Creating variable with a value of {value}, a unit of "{unitStr}" and an uncertanty of {uncert}')

        # create a unit object
        self._unitObject = unitStr if isinstance(unitStr, unit) else unit(unitStr)

        # number of digits to show
        self.nDigits = nDigits

        # parse the value and the uncertaty
        try:
            # the value is a single number
            self._value = float(value)

            if uncert is None:
                self._uncert = 0
            else:
                try:
                    # the uncertanty is a number
                    self._uncert = float(uncert)
                except TypeError:
                    logger.error(f'The value is a number but the uncertanty is a {type(uncert)}')
                    raise ValueError(f'The value is a number but the uncertanty is a {type(uncert)}')
        except TypeError:
            # the value contains multiple elements
            if uncert is None:
                self._value = np.array(value, dtype=float)
                self._uncert = np.zeros(len(value), dtype=float)
            else:
                try:
                    float(uncert)
                    logger.error(f'The value is a list-like object but the uncertanty is a number')
                    raise ValueError(f'The value is a list-like object but the uncertanty is a number')
                except TypeError:
                    if len(value) != len(uncert):
                        logger.error('The number of elements in the value is not equal to the number of elements in the uncertanty')
                        raise ValueError('The number of elements in the value is not equal to the number of elements in the uncertanty')
                    self._value = np.array(value, dtype=float)
                    self._uncert = np.array(uncert, dtype=float)

        # value and unit in SI. This is used when determining the gradient in the uncertanty expression
        self._getConverterToSI()

        # uncertanty
        self.dependsOn = {}
        self.covariance = {}

    def _getConverterToSI(self):
        self._converterToSI = self._unitObject._converterToSI

    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return str(self._unitObject)

    @property
    def uncert(self):
        return self._uncert

    def convert(self, newUnit):
        oldUnit = self._unitObject
        oldValue = self._value
        oldUncert = self._uncert

        converter = self._unitObject.getConverter(newUnit)
        self._value = converter.convert(self._value, useOffset=not self._unitObject.isCombinationUnit())
        self._uncert = converter.convert(self._uncert, useOffset=False)
        self._unitObject = unit(newUnit)

        # update the converter to SI
        self._getConverterToSI()

        logger.info(f'Converted the varible from {oldValue} +/- {oldUncert} [{oldUnit}] to {self._value} +/- {self._uncert} [{self.unit}]')

    def __getitem__(self, items):
        if isinstance(self._value, np.ndarray):
            if isinstance(items, int):
                items = [items]
            vals = [self._value[i] for i in items]
            uncert = [self._uncert[i]for i in items]
            return variable(vals, self.unit, uncert)
        else:
            if items == 0:
                return self
            else:
                L = np.array([0])
                L[items]

    def printUncertanty(self, value, uncert):
        # function to print number
        if uncert == 0 or uncert is None:
            return f'{value:.{self.nDigits}g}', None

        digitsUncert = -int(np.floor(np.log10(np.abs(uncert))))
        digitsValue = -int(np.floor(np.log10(np.abs(value))))

        # uncertanty
        if digitsUncert > 0:
            uncert = f'{uncert:.{1}g}'
        else:
            nDecimals = len(str(int(uncert)))
            uncert = int(np.around(uncert, -nDecimals + 1))

        # value
        if digitsValue <= digitsUncert:
            if digitsUncert > 0:
                value = f'{value:.{digitsUncert}f}'
            else:
                value = int(np.around(value, - nDecimals + 1))
        else:
            value = '0'
            if digitsUncert > 0:
                value += '.' + ''.join(['0'] * digitsUncert)

        return value, uncert

    def __str__(self, pretty=None) -> str:

        # standard values
        uncert = None
        unitStr = self._unitObject.__str__(pretty=pretty)

        if pretty:
            pm = r'\pm'
            space = r'\ '
            squareBracketLeft = r'\left ['
            squareBracketRight = r'\right ]'

        else:
            pm = '+/-'
            squareBracketLeft = '['
            squareBracketRight = ']'
            space = ' '

        if unitStr == '1':
            unitStr = ''
        else:
            unitStr = rf'{squareBracketLeft}{unitStr}{squareBracketRight}'

        if isinstance(self._value, float) or isinstance(self._value, int):
            # print a single value
            value = self._value
            if self._uncert != 0:
                uncert = self._uncert

            value, uncert = self.printUncertanty(value, uncert)
            if uncert is None:
                return rf'{value}{space}{unitStr}'
            else:
                return rf'{value} {pm} {uncert}{space}{unitStr}'

        else:
            # print array of values
            valStr = []
            uncStr = []
            for v, u in zip(self._value, self._uncert):
                v, u = self.printUncertanty(v, u)
                valStr.append(v)
                uncStr.append(u)

            if all(self._uncert == 0) or all(elem is None for elem in self._uncert):
                out = rf''
                out += rf'['
                for i, elem in enumerate(valStr):
                    out += rf'{elem}'
                    if i != len(valStr) - 1:
                        out += rf', '
                out += rf']'
                out += rf'{space}{unitStr}'
                return out
            else:
                # find number of significant digits in uncertanty
                out = rf''
                out += rf'['
                for i, elem in enumerate(valStr):
                    out += rf'{elem}'
                    if i != len(valStr) - 1:
                        out += r', '
                out += rf']'
                out += rf' {pm} '
                out += rf'['
                for i, elem in enumerate(uncStr):
                    out += rf'{elem}'
                    if i != len(uncStr) - 1:
                        out += r', '
                out += rf']'
                out += rf'{space}{unitStr}'
                return out

    def _addDependents(self, vars, grads):
        # loop over the variables and their gradients
        for var, grad in zip(vars, grads):
            # scale the gradient to SI units. This is necessary if one of the variables are converted after the dependency has been noted
            scale = self._converterToSI.convert(1, useOffset=False) / var._converterToSI.convert(1, useOffset=False)
            grad *= scale

            # check if the variable depends on other variables
            if var.dependsOn:

                # loop over the dependencies of the variables and add them to the dependencies of self.
                # this ensures that the product rule is used
                for key, item in var.dependsOn.items():
                    if key in self.dependsOn:
                        self.dependsOn[key] += item * grad
                    else:
                        self.dependsOn[key] = item * grad
            else:

                # the variable did not have any dependecies. Therefore the the varaible is added to the dependencies of self
                if var in self.dependsOn:
                    self.dependsOn[var] += grad
                else:
                    self.dependsOn[var] = grad

    def _addCovariance(self, var, covariance):
        self.covariance[var] = covariance

    def _calculateUncertanty(self):

        # variance from each measurement
        variance = 0
        selfScaleToSI = self._converterToSI.convert(1, useOffset=False)
        for var, grad in self.dependsOn.items():
            # the gradient is scaled with the inverse of the conversion of the unit to SI units.
            # This is necessary if the variable "var" has been converted after the dependency has been noted
            scale = var._converterToSI.convert(1, useOffset=False) / selfScaleToSI
            variance += (grad * scale * var.uncert)**2

        # variance from the corralation between measurements
        n = len(self.dependsOn.keys())
        for i in range(n):
            var_i = list(self.dependsOn.keys())[i]
            for j in range(i + 1, n):
                if i != j:
                    var_j = list(self.dependsOn.keys())[j]
                    if var_j in var_i.covariance.keys():
                        if not var_i in var_j.covariance.keys():
                            logger.error(
                                f'The variable {var_i} is correlated with the varaible {var_j}. However the variable {var_j} not not correlated with the variable {var_i}. Something is wrong.')
                            raise ValueError(
                                f'The variable {var_i} is correlated with the varaible {var_j}. However the variable {var_j} not not correlated with the variable {var_i}. Something is wrong.')
                        scale_i = var_i._converterToSI.convert(1, useOffset=False) / selfScaleToSI
                        scale_j = var_j._converterToSI.convert(1, useOffset=False) / selfScaleToSI
                        varianceContribution = 2 * scale_i * self.dependsOn[var_i] * scale_j * self.dependsOn[var_j] * var_i.covariance[var_j][0]
                        variance += varianceContribution

        self._uncert = np.sqrt(variance)
        logger.info(f'Calculated uncertanty to {self._uncert}')

    def __add__(self, other):
        logger.info(f'Adding together {self} and {other}')

        if not isinstance(other, variable):
            return self + variable(other, self.unit)

        try:
            outputUnit = self._unitObject + other._unitObject
        except ValueError:
            logger.error(f'You tried to add a variable in [{self.unit}] to a variable in [{other.unit}], but the units does not match')
            raise ValueError(f'You tried to add a variable in [{self.unit}] to a variable in [{other.unit}], but the units does not match')

        val = self._value + other._value
        grad = [1, 1]
        vars = [self, other]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        logger.info(f'Subtracting {other} from {self}')

        if not isinstance(other, variable):
            return self - variable(other, self.unit)

        try:
            outputUnit = self._unitObject - other._unitObject
        except ValueError:
            logger.error(f'You tried to subtract a variable in [{other.unit}] from a variable in [{self.unit}], but the units does not match')
            raise ValueError(f'You tried to subtract a variable in [{other.unit}] from a variable in [{self.unit}], but the units does not match')

        val = self._value - other._value
        grad = [1, -1]
        vars = [self, other]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def __rsub__(self, other):
        return - self + other

    def __mul__(self, other):
        logger.info(f'Multiplying {self} and {other}')

        if not isinstance(other, variable):
            return self * variable(other)

        outputUnit = self._unitObject * other._unitObject

        val = self._value * other._value
        grad = [other._value, self._value]
        vars = [self, other]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def __rmul__(self, other):
        return self * other

    def __pow__(self, other):
        logger.info(f'Raising {self} to the power of {other}')

        if not isinstance(other, variable):
            return self ** variable(other)

        if isinstance(other._value, np.ndarray):
            logger.error('The exponent has to be a single number')
            raise ValueError('The exponent has to be a single number')
        if str(other.unit) != '1':
            logger.error('The exponent can not have a unit')
            raise ValueError('The exponent can not have a unit')

        val = self._value ** other._value
        outputUnit = self._unitObject ** other._value

        def gradSelf(valSelf, valOther, uncertSelf):
            if uncertSelf != 0:
                return valOther * valSelf ** (valOther - 1)
            else:
                return 0

        def gradOther(valSelf, valOther, uncertOther):
            if uncertOther != 0:
                return valSelf ** valOther * np.log(valSelf)
            else:
                return 0

        gradSelf = np.vectorize(gradSelf, otypes=[float])(self._value, other._value, self._uncert)
        gradOther = np.vectorize(gradOther, otypes=[float])(self._value, other._value, other._uncert)

        grad = [gradSelf, gradOther]
        vars = [self, other]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()
        return var

    def __rpow__(self, other):
        return variable(other, '1') ** self

    def __truediv__(self, other):
        logger.info(f'Dividing {self} with {other}')
        if not isinstance(other, variable):
            return self / variable(other)

        val = self._value / other._value
        outputUnit = self._unitObject / other._unitObject
        grad = [1 / other._value, -self._value / (other._value**2)]
        vars = [self, other]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def __rtruediv__(self, other):
        logger.info(f'Dividing {other} with {self}')
        if not isinstance(other, variable):
            return variable(other) / self

        val = other._value / self._value
        outputUnit = other._unitObject / self._unitObject
        grad = [-other._value / (self._value**2), 1 / (self._value)]
        vars = [self, other]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def __neg__(self):
        logger.info(f'Negating {self}')
        return -1 * self

    def log(self):
        logger.info(f'Taking the natural log of {self}')
        if self.unit != '1':
            logger.error('You can only take the natural log of a variable if it has no unit')
            raise ValueError('You can only take the natural log of a variable if it has no unit')
        val = np.log(self._value)

        vars = [self]
        grad = [1 / self._value]

        var = variable(val, '1')
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def log10(self):
        logger.info(f'Taking the base 10 log of {self}')

        if self.unit != '1':
            logger.error('You can only take the base 10 log of a variable if it has no unit')
            raise ValueError('You can only take the base 10 log of a variable if it has no unit')
        val = np.log10(self._value)

        vars = [self]
        grad = [1 / (self._value * np.log10(self._value))]

        var = variable(val, '1')
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def exp(self):
        return np.e**self

    def sqrt(self):
        return self**(1 / 2)

    def sin(self):
        if str(self._unitObject._SIBaseUnit) != 'rad':
            logger.error('You can only take sin of an angle')
            raise ValueError('You can only take sin of an angle')

        outputUnit = '1'
        if self.unit == 'rad':
            val = np.sin(self._value)
            grad = [np.cos(self._value)]
        else:
            val = np.sin(np.pi / 180 * self._value)
            grad = [np.pi / 180 * np.cos(np.pi / 180 * self._value)]

        vars = [self]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def cos(self):
        if str(self._unitObject._SIBaseUnit) != 'rad':
            logger.error('You can only take cos of an angle')
            raise ValueError('You can only take cos of an angle')

        outputUnit = '1'
        if self.unit == 'rad':
            val = np.cos(self._value)
            grad = [-np.sin(self._value)]
        else:
            val = np.cos(np.pi / 180 * self._value)
            grad = [-np.pi / 180 * np.sin(np.pi / 180 * self._value)]

        vars = [self]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def tan(self):
        if str(self._unitObject._SIBaseUnit) != 'rad':
            logger.error('You can only take tan of an angle')
            raise ValueError('You can only take tan of an angle')

        outputUnit = '1'
        if self.unit == 'rad':
            val = np.tan(self._value)
            grad = [2 / (np.cos(2 * self._value) + 1)]
        else:
            val = np.tan(np.pi / 180 * self._value)
            grad = [np.pi / (90 * (np.cos(np.pi / 90 * self._value) + 1))]

        vars = [self]

        var = variable(val, outputUnit)
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        return var

    def __array_function__(self, func, types, args, kwargs):
        if func not in HANDLED_FUNCTIONS:
            return NotImplemented
        # Note: this allows subclasses that don't override
        # __array_function__ to handle Physical objects
        if not all(issubclass(t, variable) for t in types):
            return NotImplemented
        return HANDLED_FUNCTIONS[func](*args, **kwargs)


def implements(numpy_function):
    """Register an __array_function__ implementation for Physical objects."""
    def decorator(func):
        HANDLED_FUNCTIONS[numpy_function] = func
        return func
    return decorator


@implements(np.max)
def np_max_for_variable(x, *args, **kwargs):
    if isinstance(x.value, np.ndarray):
        index = np.argmax(x.value)
        val = x.value[index]
        if not x.uncert is None:
            unc = x.uncert[index]
        else:
            unc = None
    else:
        val = x.value
        if not x.uncert is None:
            unc = x.uncert
        else:
            unc = None
    return variable(val, x.unit, unc)


@implements(np.min)
def np_max_for_variable(x, *args, **kwargs):
    if isinstance(x.value, np.ndarray):
        index = np.argmin(x.value)
        val = x.value[index]
        if not x.uncert is None:
            unc = x.uncert[index]
        else:
            unc = None
    else:
        val = x.value
        if not x.uncert is None:
            unc = x.uncert
        else:
            unc = None
    return variable(val, x.unit, unc)


@implements(np.mean)
def np_mean_for_variable(x, *args, **kwargs):
    if isinstance(x.value, np.ndarray):
        val = np.mean(x.value)
        if not x.uncert is None:
            n = len(x.uncert)
            unc = np.sqrt(sum([(1 / n * elem)**2 for elem in x.uncert]))
        else:
            unc = None
    else:
        val = x.value
        if not x.uncert is None:
            unc = x.uncert
        else:
            unc = None
    return variable(val, x.unit, unc)
