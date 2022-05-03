import autograd.numpy as np
try:
    from dataUncert.unitSystem import unit as unitConversion
except ModuleNotFoundError:
    from unitSystem import unit as unitConversion


class variable():
    def __init__(self, value, unit, uncert=None, nDigits=3) -> None:

        self.unit = unit
        self.unitConversion = unitConversion()
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
                    raise ValueError(f'The value is a number but the uncertanty is a {type(uncert)}')
        except TypeError:
            # the value contains multiple elements
            if uncert is None:
                self.value = np.array(value, dtype=float)
                self.uncert = np.zeros(len(value), dtype=float)
            else:
                try:
                    float(uncert)
                    raise ValueError(f'The value is a list-like object but the uncertanty is a number')
                except TypeError:
                    if len(value) != len(uncert):
                        raise ValueError('The number of elements in the value is not equal to the number of elements in the uncertanty')
                    self.value = np.array(value, dtype=float)
                    self.uncert = np.array(uncert, dtype=float)

        # uncertanty
        self.dependsOn = {}
        self.covariance = {}

    def convert(self, newUnit):
        # determine if the base unit of the variable is equal to the base unit of the new unit
        if not self.unitConversion.assertUnitsSI(self.unit, newUnit):
            raise ValueError(f'You cannot convert from [{self.unit}] to [{newUnit}]')

        # convert the variable to the base unit
        self.value, _ = self.unitConversion.convertToSI(self.value, self.unit)
        self.uncert, self.unit = self.unitConversion.convertToSI(self.uncert, self.unit, isUncert=True)

        # convert the variable to the new unit
        self.value, _ = self.unitConversion.convertFromSI(self.value, newUnit)
        self.uncert, _ = self.unitConversion.convertFromSI(self.uncert, newUnit, isUncert=True)

        u, l = self.unitConversion._splitCompositeUnit(newUnit)
        self.unit = self.unitConversion._combineUpperAndLower(u, l)

    def __getitem__(self, items):
        if isinstance(self.value, np.ndarray):
            vals = [self.value[i] for i in items]
            uncert = [self.uncert[i]for i in items]
            return variable(vals, self.unit, uncert)
        else:
            if items == 0:
                return self
            else:
                L = np.array([0])
                L[items]

    def __str__(self) -> str:

        # function to print number
        def printUncertanty(value, uncert):
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
        # standard values
        uncert = None
        unit = self.unit if self.unit != '1' else ''

        if isinstance(self.value, float) or isinstance(self.value, int):
            # print a single value
            value = self.value
            if self.uncert != 0:
                uncert = self.uncert

            if uncert is None:
                value = f'{value:.{self.nDigits}g}'
                return f'{value} [{unit}]'
            else:
                # find number of significant digits in uncertanty
                value, uncert = printUncertanty(value, uncert)
                return f'{value} +/- {uncert} [{unit}]'

        else:
            # print array of values
            value = self.value
            if any(self.uncert != 0):
                uncert = self.uncert

            if uncert is None:
                value = [f'{elem:.{self.nDigits}g}' for elem in value]
                return f'{value} [{unit}]'
            else:
                # find number of significant digits in uncertanty
                for i in range(len(value)):
                    value[i], uncert[i] = printUncertanty(value[i], uncert[i])

                return f'{value} +/- {uncert} [{unit}]'

    def _addDependents(self, L, grad):
        for i, elem in enumerate(L):
            if elem.dependsOn:
                for key, item in elem.dependsOn.items():
                    if key in self.dependsOn:
                        self.dependsOn[key] += item * grad[i]
                    else:
                        self.dependsOn[key] = item * grad[i]
            else:
                if elem in self.dependsOn:
                    self.dependsOn[elem] += grad[i]
                else:
                    self.dependsOn[elem] = grad[i]

    def _addCovariance(self, var, covariance):
        self.covariance[var] = covariance

    def _calculateUncertanty(self):
        
        # uncertanty from each measurement
        self.uncert = sum([(gi * var.uncert)**2 for gi, var in zip(self.dependsOn.values(), self.dependsOn.keys())])

        # uncertanty from the corralation between measurements
        n = len(self.dependsOn.keys())
        for i in range(n):
            var_i = list(self.dependsOn.keys())[i]
            for j in range(i + 1, n):
                if i != j:
                    var_j = list(self.dependsOn.keys())[j]
                    if var_j in var_i.covariance.keys():
                        if not var_i in var_j.covariance.keys():
                            raise ValueError(
                                f'The variable {var_i} is correlated with the varaible {var_j}. However the variable {var_j} not not correlated with the variable {var_i}. Something is wrong.')
                        self.uncert += (2 * self.dependsOn[var_i] * self.dependsOn[var_j] * var_i.covariance[var_j][0])

        self.uncert = np.sqrt(self.uncert)

    def __add__(self, other):
        if isinstance(other, variable):
            if not self.unitConversion.assertEqual(self.unit, other.unit):
                raise ValueError(f'You tried to add a variable in [{self.unit}] to a variable in [{other.unit}], but the units does not match')

            valSelf = self.value
            valOther = other.value
            unit = self.unit

            val = valSelf + valOther
            grad = [1, 1]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()
            return var
        else:
            other = variable(other, self.unit)
            return self + other

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, variable):
            if not self.unitConversion.assertEqual(self.unit, other.unit):
                raise ValueError(f'You tried to subtract a variable in [{other.unit}] from a variable in [{self.unit}], but the units does not match')

            valSelf = self.value
            valOther = other.value
            unit = self.unit

            val = valSelf - valOther
            grad = [1, -1]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            return var
        else:
            other = variable(other, self.unit)
            return self - other

    def __rsub__(self, other):
        return - self + other

    def __mul__(self, other):
        if isinstance(other, variable):
            valSelf = self.value
            valOther = other.value
            unitSelf = self.unit
            unitOther = other.unit
            unit = self.unitConversion._multiply(unitSelf, unitOther)

            val = valSelf * valOther
            grad = [valOther, valSelf]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            return var
        else:
            other = variable(other, '1')
            return self * other

    def __rmul__(self, other):
        return self * other

    def __pow__(self, other):
        if isinstance(other, variable):
            valSelf = self.value
            valOther = other.value
            unitSelf = self.unit
            unitOther = other.unit
            if unitOther != '1':
                raise ValueError('The exponent can not have a unit')

            if unitSelf != '1':
                if valOther < 1:
                    unit = self.unitConversion._nRoot(unitSelf, valOther)
                else:
                    unit = self.unitConversion._power(unitSelf, valOther)
            else:
                unit = '1'

            val = valSelf ** valOther
            grad = [valOther * valSelf ** (valOther - 1), valSelf ** valOther * np.log(np.abs(valSelf))]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            return var
        else:
            other = variable(other, '1')
            return self ** other

    def __rpow__(self, other):
        if isinstance(other, variable):
            valSelf = self.value
            valOther = other.value
            valSelf, unitSelf = self.unitConversion.convertFromSI(valSelf, self.unit)
            valOther, unitOther = other.unitConversion.convertFromSI(valOther, other.unit)
            if unitSelf != '1':
                raise ValueError('The exponent can not have a unit')
            if unitOther != '1' and not valSelf.is_integer():
                raise ValueError('A measurement with a unit can only be raised to an integer power')
            if unitOther != '1':
                unit = unitConversion()._power(unitOther, valSelf)
            else:
                unit = '1'
            val = valOther ** valSelf
            grad = [valSelf * valOther ** (valSelf - 1), valOther ** valSelf * np.log(valOther)]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            return var
        else:
            other = variable(other, '1')
            return other ** self

    def __truediv__(self, other):
        if isinstance(other, variable):
            valSelf = self.value
            valOther = other.value
            unitSelf = self.unit
            unitOther = other.unit
            unit = self.unitConversion._divide(unitSelf, unitOther)

            val = valSelf / valOther
            grad = [1 / valOther, valSelf / (valOther**2)]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            return var
        else:
            other = variable(other, '1')
            return self / other

    def __rtruediv__(self, other):
        if isinstance(other, variable):
            valSelf = self.value
            valOther = other.value
            valSelf, unitSelf = self.unitConversion.convertFromSI(valSelf, self.unit)
            valOther, unitOther = other.unitConversion.convertFromSI(valOther, other.unit)
            unit = self.unitConversion._divide(unitOther, unitSelf)

            val = valOther / valSelf
            grad = [valOther / (valSelf**2), 1 / (valSelf)]
            vars = [self, other]

            var = variable(val, unit)
            var._addDependents(vars, grad)
            var._calculateUncertanty()

            return var
        else:
            other = variable(other, '1')
            return other / self

    def __neg__(self):
        return -1 * self

    def log(self):
        if self.unit != '1':
            raise ValueError('You can only take the natural log of a variable if it has no unit')
        val = np.log(self.value)

        vars = [self]
        grad = [1 / self.value]

        var = variable(val, '1')
        var._addDependents(vars, grad)
        var._calculateUncertanty()
        return var

    def log10(self):
        if self.unit != '1':
            raise ValueError('You can only take the base 10 log of a variable if it has no unit')
        val = np.log10(self.value)

        vars = [self]
        grad = [1 / (self.value * np.log10(self.value))]

        var = variable(val, '1')
        var._addDependents(vars, grad)
        var._calculateUncertanty()
        return var

    def exp(self):
        return np.e**self

    def sqrt(self):
        return self**(1 / 2)
