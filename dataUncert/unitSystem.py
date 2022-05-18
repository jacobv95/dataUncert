import numpy as np


class _unitConversion():

    def __init__(self, scale, offset) -> None:
        self.scale = scale
        self.offset = offset

    def convertToSI(self, upper=True, isComposite=False):
        if upper:
            if isComposite:
                return [self.scale, 0]
            else:
                return [self.scale, self.offset]
        else:
            return self.convertFromSI(not upper, isComposite)

    def convertFromSI(self, upper=True, isComposite=False):
        if upper:
            if isComposite:
                return [1 / self.scale, 0]
            else:
                return [1 / self.scale, -self.offset / self.scale]
        else:
            return self.convertToSI(not upper, isComposite)


class unit():
    def __init__(self) -> None:

        unit = {
            '1': _unitConversion(1, 0),
            "": _unitConversion(1, 0)
        }

        force = {
            'N': _unitConversion(1, 0)
        }

        mass = {
            'g': _unitConversion(1 / 1000, 0)
        }

        energy = {
            'J': _unitConversion(1, 0),
        }

        power = {
            'W': _unitConversion(1, 0)
        }

        pressure = {
            'Pa': _unitConversion(1, 0),
            'bar': _unitConversion(1e5, 0)
        }

        temperature = {
            'K': _unitConversion(1, 0),
            'C': _unitConversion(1, 273.15),
            'F': _unitConversion(5 / 9, 273.15 - 32 * 5 / 9)
        }

        time = {
            's': _unitConversion(1, 0),
            'min': _unitConversion(60, 0),
            'h': _unitConversion(60 * 60, 0),
            'yr': _unitConversion(60 * 60 * 24 * 365, 0)
        }

        volume = {
            'm3': _unitConversion(1, 0),
            'L': _unitConversion(1 / 1000, 0)
        }

        length = {
            'm': _unitConversion(1, 0)
        }

        current = {
            'A': _unitConversion(1, 0)
        }

        voltage = {
            'V': _unitConversion(1, 0)
        }

        self.units = {
            'kg-m/s2': force,
            'kg/m-s2': pressure,
            's': time,
            'K': temperature,
            'm3': volume,
            'm': length,
            'kg-m2/s2': energy,
            'kg-m2/s3': power,
            'kg': mass,
            'A': current,
            'V': voltage,
            '1': unit
        }

        self.prefixes = {
            'µ': 1e-6,
            'm': 1e-3,
            'k': 1e3,
            'M': 1e6
        }

    def _isUnitKnown(self, unit):
        upper, lower = self._splitCompositeUnit(unit)
        units = upper + lower
        if len(units) > 1:
            for unit in units:
                self._isUnitKnown(unit)
        else:
            unit = units[0]

        unit, _ = self._removeExponentFromUnit(unit)

        # search for the unit
        for _, unitDict in self.units.items():
            if unit in unitDict:
                return

        # The unit was not found. This must be because the unit has a prefix
        prefix = unit[0:1]
        unit = unit[1:]
        if prefix not in self.prefixes:
            raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')

        # look for the unit without the prefix
        for _, unitDict in self.units.items():
            if unit in unitDict:
                return

        # The unit was not found
        raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')

    def convertToSI(self, value, unit, isUncert=False):

        upper, lower = self._splitCompositeUnit(unit)

        if isUncert:
            isComposite = True
        else:
            isComposite = not (len(lower) == 0 and len(upper) == 1)

        unitUpper = []
        unitLower = []
        for unit in upper:
            conversion, u, exp = self._convert(unit, toSI=True, upper=True, isComposite=isComposite)
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]

            siUpper, siLower = self._splitCompositeUnit(u)
            siUpperExp = []
            siLowerExp = []
            for i, up in enumerate(siUpper):
                u, siExp = self._removeExponentFromUnit(up)
                siUpper[i] = u
                siUpperExp.append(siExp * exp)
            for i, low in enumerate(siLower):
                u, siExp = self._removeExponentFromUnit(low)
                siLower[i] = u
                siLowerExp.append(siExp * exp)

            for up, upExp in zip(siUpper, siUpperExp):
                if upExp != 1:
                    up += str(upExp)
                unitUpper.append(up)
            for low, lowExp in zip(siLower, siLowerExp):
                if lowExp != 1:
                    low += str(lowExp)
                unitLower.append(low)

        for unit in lower:
            conversion, u, exp = self._convert(unit, toSI=True, upper=False, isComposite=isComposite)
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]

            siUpper, siLower = self._splitCompositeUnit(u)
            siUpperExp = []
            siLowerExp = []
            for i, up in enumerate(siUpper):
                u, siExp = self._removeExponentFromUnit(up)
                siUpper[i] = u
                siUpperExp.append(siExp * exp)
            for i, low in enumerate(siLower):
                u, siExp = self._removeExponentFromUnit(low)
                siLower[i] = u
                siLowerExp.append(siExp * exp)

            for up, upExp in zip(siUpper, siUpperExp):
                if upExp != 1:
                    up += str(upExp)
                unitLower.append(up)
            for low, lowExp in zip(siLower, siLowerExp):
                if lowExp != 1:
                    low += str(lowExp)
                unitUpper.append(low)

        upperUpper = []
        upperLower = []
        lowerUpper = []
        lowerLower = []
        for u in unitUpper:
            up, low = self._splitCompositeUnit(u)
            upperUpper += up
            upperLower += low
        for u in unitLower:
            up, low = self._splitCompositeUnit(u)
            lowerUpper += up
            lowerLower += low
        unitUpper = upperUpper + lowerLower
        unitLower = upperLower + lowerUpper

        # cancle out upper and lower
        unitUpper, unitLower = self._cancleUnits(unitUpper, unitLower)

        # combine the upper and lower
        outUnit = self._combineUpperAndLower(unitUpper, unitLower)

        return value, outUnit

    def convertFromSI(self, value, unit, isUncert=False):

        upper, lower = self._splitCompositeUnit(unit)
        if isUncert:
            isComposite = True
        else:
            isComposite = not (len(lower) == 0 and len(upper) == 1)

        for u in upper:
            conversion, u, exp = self._convert(u, toSI=False, upper=True, isComposite=isComposite)
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]
        for u in lower:
            conversion, u, exp = self._convert(u, toSI=False, upper=False, isComposite=isComposite)
            for _ in range(exp):
                value = value * conversion[0] + conversion[1]

        return value, unit

    def _splitCompositeUnit(self, compositeUnit):

        special_characters = """!@#$%^&*()+?_=.,<>\\"""
        if any(s in compositeUnit for s in special_characters):
            raise ValueError('The unit can only contain slashes (/), hyphens (-)')

        # remove spaces
        compositeUnit = compositeUnit.replace(' ', '')
        slash = '/'
        if slash in compositeUnit:
            index = compositeUnit.find('/')
            upper = compositeUnit[0:index]
            lower = compositeUnit[index + 1:]

            # check for multiple slashes
            if slash in upper or slash in lower:
                raise ValueError('A unit can only have a single slash (/)')

            # split the upper and lower
            upper = upper.split('-')
            lower = lower.split('-')

        else:
            upper = compositeUnit.split('-')
            lower = []
        return upper, lower

    def _removeExponentFromUnit(self, unit):

        # find any integers in the unit
        num = []
        num_indexes = []
        for i, s in enumerate(unit):
            if s.isdigit():
                num.append(s)
                num_indexes.append(i)

        # determine if all integers are placed consequtively
        for i in range(len(num_indexes) - 1):
            elem_curr = num_indexes[i]
            elem_next = num_indexes[i + 1]
            if not elem_next == elem_curr + 1:
                raise ValueError('All numbers in the unit has to be grouped together')

        # determien if the last integer is placed at the end of the unit
        if len(num) != 0:
            if max(num_indexes) != len(unit) - 1:
                raise ValueError('Any number has to be placed at the end of the unit')

        # remove the inters from the unit
        if len(num) != 0:
            for i in reversed(num_indexes):
                unit = unit[0:i] + unit[i + 1:]

       # combine the exponent
        if len(num) != 0:
            exponent = int(''.join(num))
        else:
            exponent = 1

        # check if the intire unit has been removed by the integers.
        if len(unit) == 0:
            # check if the exponent is equal to 1
            if exponent == 1:
                unit = '1'
        return unit, exponent

    def _convert(self, unit, toSI=True, upper=True, isComposite=False):
        unit, exponent = self._removeExponentFromUnit(unit)

        # search for the unit
        isFound = False
        for siUnit, unitDict in self.units.items():
            if unit in unitDict:
                conversion = unitDict[unit]
                isFound = True
                break

        # check if the unit is found
        if isFound:
            # retrun the conversion if it is found
            if toSI:
                out = conversion.convertToSI(upper, isComposite)
            else:
                out = conversion.convertFromSI(upper, isComposite)

            # the unti was found without looking for the prefix. Therefore the prefix must be 1
            prefix = 1
        else:
            # The unit was not found. This must be because the unit has a prefix

            prefix = unit[0:1]
            unit = unit[1:]
            if prefix not in self.prefixes:
                raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')

            # look for the unit without the prefix
            isFound = False
            for siUnit, unitDict in self.units.items():
                if unit in unitDict:
                    conversion = unitDict[unit]
                    isFound = True
                    break

            # check if the unit was found
            if not isFound:
                raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')

            # create the conversion
            if toSI:
                out = conversion.convertToSI(upper, isComposite)
            else:
                out = conversion.convertFromSI(upper, isComposite)

            # The prefix is inverted if the conversion is not to SI
            prefix = self.prefixes[prefix]
            if not upper:
                prefix = 1 / prefix
            if not toSI:
                prefix = 1 / prefix

        out[0] *= prefix

        return out, siUnit, exponent

    def assertEqual(self, unit1, unit2):
        # determine the upper and lower units of unit 1
        upperUnit1, lowerUnit1 = self._splitCompositeUnit(unit1)

        # determine the upper and lower units of unit 2
        upperUnit2, lowerUnit2 = self._splitCompositeUnit(unit2)

        upperUnit1 = set(upperUnit1)
        upperUnit2 = set(upperUnit2)
        lowerUnit1 = set(lowerUnit1)
        lowerUnit2 = set(lowerUnit2)

        if upperUnit1 == upperUnit2 and lowerUnit1 == lowerUnit2:
            return True
        else:
            return False

    def _divide(self, unit1, unit2):
        # determine the upper and lower units of unit 2
        upperUnit2, lowerUnit2 = self._splitCompositeUnit(unit2)

        # flip unit 2
        lowerUnit2, upperUnit2 = upperUnit2, lowerUnit2

        unit2 = ''
        if len(upperUnit2) != 0:
            unit2 += '-'.join(upperUnit2)
        else:
            unit2 += '1'

        if len(lowerUnit2) != 0:
            if len(lowerUnit2) == 1:
                if lowerUnit2[0] == '1':
                    pass
                else:
                    unit2 += '/' + '-'.join(lowerUnit2)
            else:
                unit2 += '/' + '-'.join(lowerUnit2)

        return self._multiply(unit1, unit2)

    def _multiply(self, unit1, unit2):

        # determine the upper and lower units of unit 1
        upperUnit1, lowerUnit1 = self._splitCompositeUnit(unit1)

        # determine the upper and lower units of unit 2
        upperUnit2, lowerUnit2 = self._splitCompositeUnit(unit2)

        # determine the combined upper and lower unit
        upper = upperUnit1 + upperUnit2
        lower = lowerUnit1 + lowerUnit2

        # cancle the upper and lower
        upper, lower = self._cancleUnits(upper, lower)

        # combine the upper and lower
        u = self._combineUpperAndLower(upper, lower)
        return u

    def _power(self, unit1, power):

        if not isinstance(power, int):
            if not power.is_integer():
                raise ValueError('The power has to be an integer')

        # determine the upper and lower units
        upperUnit1, lowerUnit1 = self._splitCompositeUnit(unit1)

        # increase the exponent of the upper and lower
        if upperUnit1[0] != '1':
            for i in range(len(upperUnit1)):
                u = upperUnit1[i]
                u, exponent = self._removeExponentFromUnit(u)
                exponent *= power
                if exponent != 1:
                    if exponent == 0:
                        upperUnit1[i] = '1'
                    else:
                        u = u + str(int(exponent))
                        upperUnit1[i] = u
        for i in range(len(lowerUnit1)):
            u = lowerUnit1[i]
            u, exponent = self._removeExponentFromUnit(u)
            exponent *= power
            if exponent != 1:
                if exponent == 0:
                    lowerUnit1[i] = '1'
                else:
                    u = u + str(int(exponent))
                    lowerUnit1[i] = u

        # combine the upper and lower
        u = self._combineUpperAndLower(upperUnit1, lowerUnit1)
        return u

    def _cancleUnits(self, upper, lower):

        # replace units with exponents with multiple occurances of the unit in upper
        unitsToRemove = []
        unitsToAdd = []
        for up in upper:
            u, e = self._removeExponentFromUnit(up)
            if e != 1:
                unitsToRemove.append(up)
                unitsToAdd += [u] * e

        for u in unitsToRemove:
            upper.remove(u)
        for u in unitsToAdd:
            upper.append(u)

        # replace units with exponents with multiple occurances of the unit in lower
        unitsToRemove = []
        unitsToAdd = []
        for low in lower:
            u, e = self._removeExponentFromUnit(low)
            if e != 1:
                unitsToRemove.append(low)
                unitsToAdd += [u] * e

        for u in unitsToRemove:
            lower.remove(u)
        for u in unitsToAdd:
            lower.append(u)

        # cancle the upper and lower units
        unitsToRemove = []
        done = False
        while not done:
            done = True
            for low in lower:
                if low in upper:
                    upper.remove(low)
                    lower.remove(low)
                    done = False
            if done:
                break

        # remove '1'
        if len(upper) > 1:
            if '1' in upper:
                upper.remove('1')

        if len(lower) > 1:
            if '1' in lower:
                lower.remove('1')

        # determine the exponents of each unit in the upper
        upperWithExponents = []
        if len(upper) != 0:
            done = False
            while not done:
                up = upper[0]
                exponent = upper.count(up)
                if exponent != 1:
                    upperWithExponents.append(up + str(exponent))
                else:
                    upperWithExponents.append(up)
                upper = list(filter((up).__ne__, upper))
                if len(upper) == 0:
                    done = True

        # determine the exponents of each unit in the lower
        lowerWithExponents = []
        if len(lower) != 0:
            done = False
            while not done:
                low = lower[0]
                exponent = lower.count(low)
                if exponent != 1:
                    lowerWithExponents.append(low + str(exponent))
                else:
                    lowerWithExponents.append(low)
                lower = list(filter((low).__ne__, lower))
                if len(lower) == 0:
                    done = True
        return upperWithExponents, lowerWithExponents

    def _combineUpperAndLower(self, upper, lower):

        # combine the upper and lower
        u = ''
        if len(upper) != 0:
            u += '-'.join(upper)
        else:
            u += '1'

        if len(lower) != 0:
            if len(lower) == 1:
                if lower[0] == '1':
                    pass
                else:
                    u += '/' + '-'.join(lower)
            else:
                u += '/' + '-'.join(lower)

        return u

    def assertUnitsSI(self, unit1, unit2):
        # split the units
        upper1, lower1 = self._splitCompositeUnit(unit1)
        upper2, lower2 = self._splitCompositeUnit(unit2)

        upper1SI = []
        for u in upper1:
            _, uSI, exponent = self._convert(u, toSI=True, upper=True, isComposite=False)
            uSI, exp = self._removeExponentFromUnit(uSI)
            exponent *= exp
            if exponent != 1:
                uSI += str(exponent)
            upper1SI.append(uSI)

        lower1SI = []
        for l in lower1:
            _, lSI, exponent = self._convert(l, toSI=True, upper=False, isComposite=False)
            lSI, exp = self._removeExponentFromUnit(lSI)
            exponent *= exp
            if exponent != 1:
                lSI += str(exponent)
            lower1SI.append(lSI)

        upper2SI = []
        for u in upper2:
            _, uSI, exponent = self._convert(u, toSI=True, upper=True, isComposite=False)
            uSI, exp = self._removeExponentFromUnit(uSI)
            exponent *= exp
            if exponent != 1:
                uSI += str(exponent)
            upper2SI.append(uSI)

        lower2SI = []
        for l in lower2:
            _, lSI, exponent = self._convert(l, toSI=True, upper=False, isComposite=False)
            lSI, exp = self._removeExponentFromUnit(lSI)
            exponent *= exp
            if exponent != 1:
                lSI += str(exponent)
            lower2SI.append(lSI)

        upper1SI, lower1SI = self._cancleUnits(upper1SI, lower1SI)
        upper2SI, lower2SI = self._cancleUnits(upper2SI, lower2SI)

        if upper1SI == upper2SI and lower1SI == lower2SI:
            return True
        else:
            return False

    def _nRoot(self, unit, power):

        upper, lower = self._splitCompositeUnit(unit)

        def isCloseToInteger(a, rel_tol=1e-9, abs_tol=0.0):
            b = np.around(a)
            return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

        # Test if the exponent of all units is divisible by the power
        for elem in upper + lower:
            elem, exp = self._removeExponentFromUnit(elem)
            # remainder = exp % int(np.around(1 / power))
            if not isCloseToInteger(exp * power):
                raise ValueError(f'You can not raise a variable with the unit {unit} to the power of {power}')

        # Determine the new exponent for all upper units
        for i, up in enumerate(upper):
            up, exp = self._removeExponentFromUnit(up)
            exp *= power
            exp = int(np.around(exp))
            if exp != 1:
                up += str(exp)
            upper[i] = up

        # Determine the new exponent for all lower units
        for i, low in enumerate(lower):
            low, exp = self._removeExponentFromUnit(low)
            exp *= power
            exp = int(np.around(exp))
            if exp != 1:
                low += str(exp)
            lower[i] = low

        unit = self._combineUpperAndLower(upper, lower)
        return unit


