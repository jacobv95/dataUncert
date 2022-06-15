import logging
logger = logging.getLogger(__name__)
import numpy as np
from dataUncert.unit import unit


HANDLED_FUNCTIONS = {}


class variable():
    def __init__(self, value, unitStr, uncert=None, nDigits=3) -> None:

        logger.info(f'Creating variable with a value of {value}, a unit of "{unitStr}" and an uncertanty of {uncert}')

        if isinstance(unitStr, unit):
            self._unitObject = unitStr
        else:
            self._unitObject = unit(unitStr)

        self.nDigits = nDigits

        # uncertanty
        self.dependsOn = {}
        self.covariance = {}

        try:
            # the value is a single number
            self.value = float(value)

            if uncert is None:
                self.uncert = 0
            else:
                try:
                    # the uncertanty is a number
                    self.uncert = float(uncert)
                except TypeError:
                    logger.error(f'The value is a number but the uncertanty is a {type(uncert)}')
                    raise ValueError(f'The value is a number but the uncertanty is a {type(uncert)}')
        except TypeError:
            # the value contains multiple elements
            if uncert is None:
                self.value = np.array(value, dtype=float)
                self.uncert = np.zeros(len(value), dtype=float)
            else:
                try:
                    float(uncert)
                    logger.error(f'The value is a list-like object but the uncertanty is a number')
                    raise ValueError(f'The value is a list-like object but the uncertanty is a number')
                except TypeError:
                    if len(value) != len(uncert):
                        logger.error('The number of elements in the value is not equal to the number of elements in the uncertanty')
                        raise ValueError('The number of elements in the value is not equal to the number of elements in the uncertanty')
                    self.value = np.array(value, dtype=float)
                    self.uncert = np.array(uncert, dtype=float)

        # uncertanty
        self.dependsOn = {}
        self.covariance = {}

    @property
    def unit(self):
        return str(self._unitObject)

    def convert(self, newUnit):
        oldUnit = self._unitObject
        oldValue = self.value
        oldUncert = self.uncert

        converter = self._unitObject.getConverter(newUnit)
        self.value = converter.convert(self.value, useOffset=not self._unitObject.isCombinationUnit())
        self.uncert = converter.convert(self.uncert, useOffset=False)
        self._unitObject = unit(newUnit)

        logger.info(f'Converted the varible from {oldValue} +/- {oldUncert} [{oldUnit}] to {self.value} +/- {self.uncert} [{self.unit}]')

    def __getitem__(self, items):
        if isinstance(self.value, np.ndarray):
            if isinstance(items, int):
                items = [items]
            vals = [self.value[i] for i in items]
            uncert = [self.uncert[i]for i in items]
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
            value = f'{value:.{self.nDigits}g}'
            uncert = None
        else:
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
                    value += '.'
                    for i in range(digitsUncert):
                        value += '0'
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

        if isinstance(self.value, float) or isinstance(self.value, int):
            # print a single value
            value = self.value
            if self.uncert != 0:
                uncert = self.uncert

            value, uncert = self.printUncertanty(value, uncert)
            if uncert is None:
                return rf'{value}{space}{squareBracketLeft}{unitStr}{squareBracketRight}'
            else:
                return rf'{value} {pm} {uncert}{space}{squareBracketLeft}{unitStr}{squareBracketRight}'

        else:
            # print array of values
            valStr = []
            uncStr = []
            for v, u in zip(self.value, self.uncert):
                v, u = self.printUncertanty(v, u)
                valStr.append(v)
                uncStr.append(u)

            if all(self.uncert == 0) or all(elem is None for elem in self.uncert):
                out = rf''
                out += rf'['
                for i, elem in enumerate(valStr):
                    out += rf'{elem}'
                    if i != len(valStr) - 1:
                        out += rf', '
                out += rf']'
                out += rf'{space}{squareBracketLeft}{unitStr}{squareBracketRight}'
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
                out += rf'{space}{squareBracketLeft}{unitStr}{squareBracketRight}'
                return out

    def _addDependents(self, L, grad):
        for i, elem in enumerate(L):
            logger.debug(f'Adding dependency of {elem} with a gradient of {grad[i]} to {self}')
            if elem.dependsOn:
                logger.debug(f'The variable {elem} has dependencies. These are iterated over and added to {self}')
                for key, item in elem.dependsOn.items():
                    if key in self.dependsOn:
                        logger.debug(
                            f'The variable {elem} depends on {key}, which {self} also depends on. The dependency of {self} on {elem} is increased with the new gradient in order to follow the chain rule')
                        self.dependsOn[key] += item * grad[i]
                    else:
                        logger.debug(f'The variable {elem} depends on {key}, which {self} does not depend on. The variable {key} is added to the dependencies of {self}')
                        self.dependsOn[key] = item * grad[i]
            else:
                logger.debug(f'The variable {elem} has an empty dependency list')
                if elem in self.dependsOn:
                    logger.debug(f'The variable {self} already depends on the variable {elem}. The dependency of {self} on {elem} is increased with the new gradient in order to follow the chain rule')
                    self.dependsOn[elem] += grad[i]
                else:
                    logger.debug(f'The variable {self} does not depend on the variable {elem}. The variable {elem} is added to the dependencies of {self}')
                    self.dependsOn[elem] = grad[i]

    def _addCovariance(self, var, covariance):
        logger.debug(f'Added covariance of {covariance} between {var} and {self}')
        self.covariance[var] = covariance

    def _calculateUncertanty(self):

        # uncertanty from each measurement
        variance = sum([(gi * var.uncert)**2 for gi, var in zip(self.dependsOn.values(), self.dependsOn.keys())])
        logger.debug(f'Calculated the variance without covariance to {self.uncert}')

        # uncertanty from the corralation between measurements
        logger.debug('Start calculation of uncertanty from covariance')
        n = len(self.dependsOn.keys())
        for i in range(n):
            var_i = list(self.dependsOn.keys())[i]
            logger.debug(f'Set variable i to {var_i}')
            for j in range(i + 1, n):
                if i != j:
                    var_j = list(self.dependsOn.keys())[j]
                    logger.debug(f'Set variable j to {var_j}')
                    if var_j in var_i.covariance.keys():
                        if not var_i in var_j.covariance.keys():
                            logger.error(
                                f'The variable {var_i} is correlated with the varaible {var_j}. However the variable {var_j} not not correlated with the variable {var_i}. Something is wrong.')
                            raise ValueError(
                                f'The variable {var_i} is correlated with the varaible {var_j}. However the variable {var_j} not not correlated with the variable {var_i}. Something is wrong.')
                        varianceContribution = 2 * self.dependsOn[var_i] * self.dependsOn[var_j] * var_i.covariance[var_j][0]
                        variance += varianceContribution
                        logger.debug(f'The covariance between variable i and variable j added {varianceContribution} to the variance.')
                    else:
                        logger.debug('No information about the covariance between variable i and variable j')

        self.uncert = np.sqrt(variance)
        logger.info(f'Calculated uncertanty to {self.uncert}')

    def __add__(self, other):
        logger.info(f'Adding together {self} and {other}')
        logger.debug(f'Begin adding {self} and {other}')
        if isinstance(other, variable):
            try:
                outputUnit = self._unitObject + other._unitObject
            except ValueError:
                logger.error(f'You tried to add a variable in [{self.unit}] to a variable in [{other.unit}], but the units does not match')
                raise ValueError(f'You tried to add a variable in [{self.unit}] to a variable in [{other.unit}], but the units does not match')

            val = self.value + other.value
            grad = [1, 1]
            vars = [self, other]

            var = variable(val, outputUnit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            logger.debug(f'Finished adding {self} and {other}')
            return var
        else:
            logger.debug(f'{other} is converted to a variable')
            other = variable(other, self.unit)
            return self + other

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        logger.info(f'Subtracting {other} from {self}')
        logger.debug(f'Begin subtracting {other} from {self}')
        if isinstance(other, variable):
            try:
                outputUnit = self._unitObject - other._unitObject
            except ValueError:
                logger.error(f'You tried to subtract a variable in [{other.unit}] from a variable in [{self.unit}], but the units does not match')
                raise ValueError(f'You tried to subtract a variable in [{other.unit}] from a variable in [{self.unit}], but the units does not match')

            val = self.value - other.value
            grad = [1, -1]
            vars = [self, other]

            var = variable(val, outputUnit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            logger.debug(f'Finished subtracting {other} from {self}')
            return var
        else:
            logger.debug(f'{other} is converted to a variable')
            other = variable(other, self.unit)
            return self - other

    def __rsub__(self, other):
        return - self + other

    def __mul__(self, other):
        logger.info(f'Multiplying {self} and {other}')
        logger.debug(f'Begining to multiply {self} and {other}')
        if isinstance(other, variable):
            outputUnit = self._unitObject * other._unitObject

            val = self.value * other.value
            grad = [other.value, self.value]
            vars = [self, other]

            var = variable(val, outputUnit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            logger.debug(f'Finished multiplying {self} and {other}')
            return var
        else:
            logger.debug(f'{other} is converted to a variable')
            other = variable(other, '1')
            return self * other

    def __rmul__(self, other):
        return self * other

    def __pow__(self, other):
        logger.info(f'Raising {self} to the power of {other}')

        if isinstance(other, variable):
            if isinstance(other.value, np.ndarray):
                logger.error('The exponent has to be a single number')
                raise ValueError('The exponent has to be a single number')
            if str(other.unit) != '1':
                logger.error('The exponent can not have a unit')
                raise ValueError('The exponent can not have a unit')

            val = self.value ** other.value
            outputUnit = self._unitObject ** other.value

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

            gradSelf = np.vectorize(gradSelf)(self.value, other.value, self.uncert)
            gradOther = np.vectorize(gradOther)(self.value, other.value, other.uncert)

            grad = [gradSelf, gradOther]
            vars = [self, other]

            var = variable(val, outputUnit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            logger.debug(f'Finished raising {self} to the power of {other}')
            return var
        else:
            logger.debug(f'{other} is converted to a variable')
            other = variable(other, '1')
            return self ** other

    def __rpow__(self, other):
        logger.debug(f'{other} is converted to a variable')
        other = variable(other, '1')
        return other ** self

    def __truediv__(self, other):
        logger.info(f'Dividing {self} with {other}')
        logger.debug(f'Beginning to divide {self} with {other}')
        if isinstance(other, variable):

            val = self.value / other.value
            outputUnit = self._unitObject / other._unitObject
            grad = [1 / other.value, self.value / (other.value**2)]
            vars = [self, other]

            var = variable(val, outputUnit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            logger.debug(f'Finished dividing {self} with {other}')
            return var
        else:
            logger.debug(f'{other} is converted to a variable')
            other = variable(other, '1')
            return self / other

    def __rtruediv__(self, other):
        logger.info(f'Dividing {other} with {self}')
        logger.debug(f'Begginig to divide {other} with {self}')
        if isinstance(other, variable):

            val = other.value / self.value
            outputUnit = other._unitObject / self._unitObject
            grad = [other.value / (self.value**2), 1 / (self.value)]
            vars = [self, other]

            var = variable(val, outputUnit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            logger.debug('Finished dividing {other} with {self}')
            return var
        else:
            logger.debug(f'{other} is converted to a variable')
            other = variable(other, '1')
            return other / self

    def __neg__(self):
        logger.info(f'Negating {self}')
        return -1 * self

    def log(self):
        logger.info(f'Taking the natural log of {self}')
        logger.debug(f'Beginning to take the natural log of {self}')
        if self.unit != '1':
            logger.error('You can only take the natural log of a variable if it has no unit')
            raise ValueError('You can only take the natural log of a variable if it has no unit')
        val = np.log(self.value)

        vars = [self]
        grad = [1 / self.value]

        var = variable(val, '1')
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        logger.debug(f'Finished taking the natural log of {self}')
        return var

    def log10(self):
        logger.info(f'Taking the base 10 log of {self}')
        logger.debug(f'Beginning to take the base 10 log of {self}')
        if self.unit != '1':
            logger.error('You can only take the base 10 log of a variable if it has no unit')
            raise ValueError('You can only take the base 10 log of a variable if it has no unit')
        val = np.log10(self.value)

        vars = [self]
        grad = [1 / (self.value * np.log10(self.value))]

        var = variable(val, '1')
        var._addDependents(vars, grad)
        var._calculateUncertanty()

        logger.debug(f'Finished taking the base 10 log of {self}')
        return var

    def exp(self):
        return np.e**self

    def sqrt(self):
        return self**(1 / 2)

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


if __name__ == '__main__':
    a = variable([10, 11], 'm', uncert=None)
    a = np.mean(a)
    print(a)
