import logging
logger = logging.getLogger(__name__)
import numpy as np
from copy import deepcopy


class _unitConversion():

    def __init__(self, scale, offset) -> None:
        self.scale = scale
        self.offset = offset

    def __mul__(self, other):
        if isinstance(other, _unitConversion):
            scale = self.scale * other.scale
            offset = self.offset * other.scale + other.offset
        else:
            scale = self.scale * other
            offset = self.offset
        return _unitConversion(scale, offset)

    def __imul__(self, other):
        if isinstance(other, _unitConversion):
            scale = self.scale * other.scale
            offset = self.offset * other.scale + other.offset
        else:
            scale = self.scale * other
            offset = self.offset
        return _unitConversion(scale, offset)

    def __truediv__(self, other):
        if isinstance(other, _unitConversion):
            scale = self.scale / other.scale
            offset = self.offset - other.offset / other.scale
        else:
            scale = self.scale / other.scale
            offset = self.offset
        return _unitConversion(scale, offset)

    def __itruediv__(self, other):
        if isinstance(other, _unitConversion):
            scale = self.scale / other.scale
            offset = self.offset - other.offset / other.scale
        else:
            scale = self.scale / other.scale
            offset = self.offset
        return _unitConversion(scale, offset)

    def convert(self, value, useOffset=True):
        if useOffset:
            return self.scale * value + self.offset
        else:
            return self.scale * value


baseUnit = {
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

angle = {
    'rad': _unitConversion(1, 0),
    '°': _unitConversion(np.pi / 180, 0)
}

current = {
    'A': _unitConversion(1, 0)
}

voltage = {
    'V': _unitConversion(1, 0)
}

frequency = {
    'Hz': _unitConversion(1, 0)
}

knownUnitsDict = {
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
    'kg-m2/s3-A': voltage,
    '1': baseUnit,
    'Hz': frequency,
    'rad': angle
}

knownPrefixes = {
    'µ': 1e-6,
    'm': 1e-3,
    'k': 1e3,
    'M': 1e6
}


knownUnits = {}
for key, d in knownUnitsDict.items():
    for item, _ in d.items():
        if item not in knownUnits:
            knownUnits[item] = [key, knownUnitsDict[key][item]]
        else:
            raise Warning(f'The unit {item} known in more than one unit system')


class unit():
    def __init__(self, unitStr) -> None:
        if unitStr == '':
            unitStr = '1'

        # split the unit in upper and lower
        self.unitStr = self._formatUnit(unitStr)

        self.upper, self.upperPrefix, self.upperExp, self.lower, self.lowerPrefix, self.lowerExp = self._getLists(self.unitStr)

        self._SIBaseUnit = self._getSIBaseUnit(self.upper, self.upperExp, self.lower, self.lowerExp)
        self._converterToSI = self.getConverter(self._SIBaseUnit)

    @staticmethod
    def _cancleUnits(upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp):
        # cancle the units
        for indexUpper, up in enumerate(upper):
            if up in lower:
                indexLower = lower.index(up)

                expUpper = upperExp[indexUpper]
                expLower = lowerExp[indexLower]

                # set the unit to '1'
                if expUpper == expLower:
                    upper[indexUpper] = '1'
                    lower[indexLower] = '1'
                elif expUpper < expLower:
                    upper[indexUpper] = '1'
                else:
                    lower[indexLower] = '1'

                # reduce the exponent
                minExp = np.min([expUpper, expLower])
                lowerExp[indexLower] -= minExp
                upperExp[indexUpper] -= minExp

        # remove '1' if the upper or lower is longer than 1
        if len(upper) > 1:
            indexesToRemove = [i for i, elem in enumerate(upper) if elem == '1']
            upper = [elem for i, elem in enumerate(upper) if i not in indexesToRemove]
            upperPrefix = [elem for i, elem in enumerate(upperPrefix) if i not in indexesToRemove]
            upperExp = [elem for i, elem in enumerate(upperExp) if i not in indexesToRemove]
        if len(lower) > 1:
            indexesToRemove = [i for i, elem in enumerate(lower) if elem == '1']
            lower = [elem for i, elem in enumerate(lower) if i not in indexesToRemove]
            lowerPrefix = [elem for i, elem in enumerate(lowerPrefix) if i not in indexesToRemove]
            lowerExp = [elem for i, elem in enumerate(lowerExp) if i not in indexesToRemove]

        # return the list ['1'] if there are no more units
        if not upper:
            upper = ['1']
            upperExp = ['1']
        if not lower:
            lower = ['1']
            lowerExp = ['1']
        return upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp

    @staticmethod
    def _combineUpperAndLower(upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp):

        upperPrefix = [elem if not elem is None else "" for elem in upperPrefix]
        lowerPrefix = [elem if not elem is None else "" for elem in lowerPrefix]
        upperExp = [str(elem) if elem != 1 else "" for elem in upperExp]
        lowerExp = [str(elem) if elem != 1 else "" for elem in lowerExp]
        upper = [pre + up + exp for pre, up, exp in zip(upperPrefix, upper, upperExp) if up != "1"]
        lower = [pre + low + exp for pre, low, exp in zip(lowerPrefix, lower, lowerExp) if low != "1"]

        # create a unit string
        u = '-'.join(upper) if upper else "1"
        if lower:
            lower = '-'.join(lower)
            u = u + '/' + lower

        return u

    def isCombinationUnit(self):
        if len(self.upper) > 1:
            return True
        if self.lower:
            return True
        return False

    def __str__(self, pretty=False):
        if not pretty:
            return self.unitStr
        else:
            if self.lower:
                # a fraction is needed
                out = rf'\frac{{'
                for i, (up, prefix, exp) in enumerate(zip(self.upper, self.upperPrefix, self.upperExp)):
                    if exp > 1:
                        up = rf'{up}^{exp}'
                    if prefix is None:
                        prefix = ''
                    out += rf'{prefix}{up}'
                    if i != len(self.upper) - 1:
                        out += rf' \cdot '
                out += rf'}}{{'
                for i, (low, prefix, exp) in enumerate(zip(self.lower, self.lowerPrefix, self.lowerExp)):
                    if exp > 1:
                        low = rf'{low}^{exp}'
                    if prefix is None:
                        prefix = ''
                    out += rf'{prefix}{low}'
                    if i != len(self.lower) - 1:
                        out += rf' \cdot '
                out += rf'}}'
            else:
                # no fraction
                out = r''
                for i, (up, prefix, exp) in enumerate(zip(self.upper, self.upperPrefix, self.upperExp)):
                    if exp > 1:
                        up = rf'{up}^{exp}'
                    if prefix is None:
                        prefix = ''
                    out += rf'{prefix}{up}'
                    if i != len(self.upper) - 1:
                        out += rf' \cdot '
            return out

    @staticmethod
    def _getLists(unitStr):
        upper, lower = unit._splitCompositeUnit(unitStr)

        def splitUnitExponentAndPrefix(unitList):
            tmp = [unit._removeExponentFromUnit(elem) for elem in unitList]
            exponent = [elem[1] for elem in tmp]
            tmp = [elem[0]for elem in tmp]
            tmp = [unit._removePrefixFromUnit(elem) for elem in tmp]
            u = [elem[0] for elem in tmp]
            prefix = [elem[1] for elem in tmp]
            return u, prefix, exponent
        upper, upperPrefix, upperExp = splitUnitExponentAndPrefix(upper)
        lower, lowerPrefix, lowerExp = splitUnitExponentAndPrefix(lower)
        return upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp

    @ staticmethod
    def _formatUnit(unitStr):
        # Removing any illegal symbols
        special_characters = """!@#$%^&*()+?_=.,<>\\"""
        if any(s in unitStr for s in special_characters):
            logger.error('The unit can only contain slashes (/), hyphens (-)')
            raise ValueError('The unit can only contain slashes (/), hyphens (-)')

        # Removing any spaces
        unitStr = unitStr.replace(' ', '')

        return unitStr

    @ staticmethod
    def _splitCompositeUnit(compositeUnit):
        compositeUnit = compositeUnit.split('/')

        if len(compositeUnit) > 2:
            logger.error('A unit can only have a single slash (/)')
            raise ValueError('A unit can only have a single slash (/)')

        upper = compositeUnit[0].split('-')
        lower = compositeUnit[1].split('-') if len(compositeUnit) > 1 else []

        return upper, lower

    @ staticmethod
    def _removeExponentFromUnit(u):
        u = list(u)
        lenU = len(u)
        exponent = 1
        integerIndexes = [i for i, char in enumerate(u) if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']]

        # override the exponent if there are any integerindexes
        if integerIndexes:
            # determine if all integers are consectutive together
            # sum(a, a+1, ... b-1, b) = (b * (b-1) - a * (a-1)) / 2
            minIndex, maxIndex = integerIndexes[0] - 1, integerIndexes[-1]
            if sum(integerIndexes) != (maxIndex * (maxIndex + 1) - minIndex * (minIndex + 1)) / 2:
                logger.error('All numbers in the unit has to be grouped together')
                raise ValueError('All numbers in the unit has to be grouped together')

            # Determien if the last integer is placed at the end of the unit
            if integerIndexes[-1] != lenU - 1:
                logger.error('Any number has to be placed at the end of the unit')
                raise ValueError('Any number has to be placed at the end of the unit')

            # join the integers
            exponent = int(''.join([u[i] for i in integerIndexes]))

        # join the unit
        u = ''.join([u[i] for i in range(lenU) if i not in integerIndexes])

        # Ensure that the entire use was not removed by removing the integers
        if not u:
            # No symbols are left after removing the integers
            if exponent != 1:
                logger.error(f'The unit {u} was stripped of all integers which left no symbols in the unit. This is normally due to the integers removed being equal to 1, as the unit is THE unit. Howver, the intergers removed was not equal to 1. The unit is therefore not known.')
                raise ValueError(
                    f'The unit {u} was stripped of all integers which left no symbols in the unit. This is normally due to the integers removed being equal to 1, as the unit is THE unit. Howver, the intergers removed was not equal to 1. The unit is therefore not known.')
            u = '1'

        return u, exponent

    @staticmethod
    def _assertEqualStatic(a, b):

        aUpper, aUpperPrefix, aUpperExp, aLower, aLowerPrefix, aLowerExp = unit._getLists(a)
        bUpper, bUpperPrefix, bUpperExp, bLower, bLowerPrefix, bLowerExp = unit._getLists(b)

        if bool(aLower) != bool(bLower):
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')

        aUpperIndexes = np.argsort(aUpper)
        aLowerIndexes = np.argsort(aLower)
        bUpperIndexes = np.argsort(bUpper)
        bLowerIndexes = np.argsort(bLower)

        aUpperSorted = list(np.sort(aUpper))
        aLowerSorted = list(np.sort(aLower))
        bUpperSorted = list(np.sort(bUpper))
        bLowerSorted = list(np.sort(bLower))

        aUpperExpSorted = [aUpperExp[elem] for elem in aUpperIndexes]
        aLowerExpSorted = [aLowerExp[elem] for elem in aLowerIndexes]
        bUpperExpSorted = [bUpperExp[elem] for elem in bUpperIndexes]
        bLowerExpSorted = [bLowerExp[elem] for elem in bLowerIndexes]

        aUpperPrefixSorted = [aUpperPrefix[elem] for elem in aUpperIndexes]
        aLowerPrefixSorted = [aLowerPrefix[elem] for elem in aLowerIndexes]
        bUpperPrefixSorted = [bUpperPrefix[elem] for elem in bUpperIndexes]
        bLowerPrefixSorted = [bLowerPrefix[elem] for elem in bLowerIndexes]

        if aUpperSorted != bUpperSorted:
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')
        if aLowerSorted != bLowerSorted:
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')
        if aUpperExpSorted != bUpperExpSorted:
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')
        if aLowerExpSorted != bLowerExpSorted:
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')
        if aUpperPrefixSorted != bUpperPrefixSorted:
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')
        if aLowerPrefixSorted != bLowerPrefixSorted:
            raise ValueError(f'You tried to add the unit {a} to the unit {b}. These do not match')

    def _assertEqual(self, other):
        self._assertEqualStatic(self.unitStr, other.unitStr)

    def __add__(self, other):
        self._assertEqual(other)
        return deepcopy(self)

    def __sub__(self, other):
        self._assertEqual(other)
        return deepcopy(self)

    def __mul__(self, other):

        upper = self.upper + other.upper
        lower = self.lower + other.lower

        upperExp = self.upperExp + other.upperExp
        lowerExp = self.lowerExp + other.lowerExp

        upperPrefix = self.upperPrefix + other.upperPrefix
        lowerPrefix = self.lowerPrefix + other.lowerPrefix

        # TODO optimize
        # reduce the upper units and combine their exponents
        upperReduced = []
        upperPrefixReduced = []
        upperExpReduced = []
        done = False
        while not done:
            # get the next unit
            up = upper[0]

            # find all indexes where that unit is in the upper
            indexes = [i for i, elem in enumerate(upper) if elem == up]

            # append the unit to the reduced upper
            upperReduced.append(up)

            # initialize a new element in the reduced upper exponent and prefix
            upperExpReduced.append(0)
            upperPrefixReduced.append('')

            # for each index with the same unit as "up", add the exponents and the prefixes
            # the prefixes are hyphen seperated
            for i in indexes:
                upperExpReduced[-1] += upperExp[i]
                if not upperPrefix[i] is None:
                    if upperPrefixReduced[-1]:
                        upperPrefixReduced[-1] += '-'
                    upperPrefixReduced[-1] += upperPrefix[i]

            upper = [elem for i, elem in enumerate(upper) if i not in indexes]
            upperExp = [elem for i, elem in enumerate(upperExp) if i not in indexes]
            upperPrefix = [elem for i, elem in enumerate(upperPrefix) if i not in indexes]

            if not upper:
                done = True
        upper, upperPrefix, upperExp = upperReduced, upperPrefixReduced, upperExpReduced
        upperPrefix = [elem if elem != '' else None for elem in upperPrefix]

        # reduce the lower units and combine their exponents
        lowerReduced = []
        lowerPrefixReduced = []
        lowerExpReduced = []
        done = not lower
        while not done:
            # get the next unit
            low = lower[0]

            # find all indexes where that unit is in the lower
            indexes = [i for i, elem in enumerate(lower) if elem == low]

            # append the unit to the reduced lower
            lowerReduced.append(low)

            # initialize a new element in the reduced lower exponent and prefix
            lowerExpReduced.append(0)
            lowerPrefixReduced.append('')

            # for each index with the same unit as "low", add the exponents and the prefixes
            # the prefixes are hyphen seperated
            for i in indexes:
                lowerExpReduced[-1] += lowerExp[i]
                if not lowerPrefix[i] is None:
                    if lowerPrefixReduced[-1]:
                        lowerPrefixReduced[-1] += '-'
                    lowerPrefixReduced[-1] += lowerPrefix[i]

            lower = [elem for i, elem in enumerate(lower) if i not in indexes]
            lowerExp = [elem for i, elem in enumerate(lowerExp) if i not in indexes]
            lowerPrefix = [elem for i, elem in enumerate(lowerPrefix) if i not in indexes]

            if not lower:
                done = True
        lower, lowerPrefix, lowerExp = lowerReduced, lowerPrefixReduced, lowerExpReduced
        lowerPrefix = [elem if elem != '' else None for elem in lowerPrefix]

        upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp = self._cancleUnits(
            upper,
            upperPrefix,
            upperExp,
            lower,
            lowerPrefix,
            lowerExp
        )

        out = self._combineUpperAndLower(upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp)

        return out

    def __truediv__(self, other):

        other = self._combineUpperAndLower(
            upper=other.lower,
            upperPrefix=other.lowerPrefix,
            upperExp=other.lowerExp,
            lower=other.upper,
            lowerPrefix=other.upperPrefix,
            lowerExp=other.upperExp
        )
        other = unit(other)

        return self * other

    def __pow__(self, power):

        if power == 0:
            return '1'

        elif power > 1:

            if self.unitStr == '1':
                # self is '1'. Therefore the power does not matter
                return self.unitStr

            else:
                # self is not '1'. Therefore all exponents are multiplied by the power

                if not (isinstance(power, int) or power.is_integer()):
                    logger.error('The power has to be an integer')
                    raise ValueError('The power has to be an integer')

                upperExp = [int(elem * power) for elem in self.upperExp]
                lowerExp = [int(elem * power) for elem in self.lowerExp]

                return self._combineUpperAndLower(self.upper, self.upperPrefix, upperExp, self.lower, self.lowerPrefix, lowerExp)

        else:
            # the power is smaller than 1.
            # Therefore it is necessary to determine if all exponents are divisible by the recibricol of the power

            if self.unitStr == '1':
                # self is '1'. Therefore the power does not matter
                return self.unitStr
            else:
                # self is not '1'.
                # Therefore it is necessary to determine if all exponents are divisible by the recibricol of the power

                def isCloseToInteger(a, rel_tol=1e-9, abs_tol=0.0):
                    b = np.around(a)
                    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

                # Test if the exponent of all units is divisible by the power
                for exp in self.upperExp + self.lowerExp:
                    if not isCloseToInteger(exp * power):
                        logger.error(f'You can not raise a variable with the unit {self.unitStr} to the power of {power}')
                        raise ValueError(f'You can not raise a variable with the unit {self.unitStr} to the power of {power}')

                upperExp = [int(elem * power) for elem in self.upperExp]
                lowerExp = [int(elem * power) for elem in self.lowerExp]

                return self._combineUpperAndLower(self.upper, self.upperPrefix, upperExp, self.lower, self.lowerPrefix, lowerExp)

    @staticmethod
    def _removePrefixFromUnit(unit):

        if unit in knownUnits:
            return unit, None

        # The unit was not found. This must be because the unit has a prefix
        prefix = unit[0:1]
        unit = unit[1:]

        if prefix not in knownPrefixes:
            logger.error(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')
            raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix ({prefix}) was not found')

        if unit in baseUnit:
            logger.error(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. Both the prefix and the unit were found. However, the unit "1" cannot have a prefix')
            raise ValueError(
                f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. Both the prefix and the unit were found. However, the unit "1" cannot have a prefix')

        # look for the unit without the prefix
        if not unit in knownUnits:
            logger.error(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')
            raise ValueError(f'The unit ({prefix}{unit}) was not found. Therefore it was interpreted as a prefix and a unit. However the unit ({unit}) was not found')
        return unit, prefix

    @staticmethod
    def _getSIBaseUnit(upper, upperExp, lower, lowerExp):

        def addUnitsMultipleTimes(units, unitExps):
            out = []
            for unit, unitExp in zip(units, unitExps):
                for _ in range(unitExp):
                    out.append(unit)
            return out

        upper = addUnitsMultipleTimes(upper, upperExp)
        lower = addUnitsMultipleTimes(lower, lowerExp)

        # remove the prefix - this is just a scaling so this does not change the SI base unit
        upper = [unit._removePrefixFromUnit(elem)[0] for elem in upper]
        lower = [unit._removePrefixFromUnit(elem)[0] for elem in lower]

        # return the splitted version of the base unit
        upper = [unit._splitCompositeUnit(knownUnits[elem][0]) for elem in upper]
        lower = [unit._splitCompositeUnit(knownUnits[elem][0]) for elem in lower]
        # combine the upper and lower
        tmpUpper = [elem[0] for elem in upper] + [elem[1] for elem in lower]
        tmpLower = [elem[1] for elem in upper] + [elem[0] for elem in lower]
        upper = [elem for L in tmpUpper for elem in L]
        lower = [elem for L in tmpLower for elem in L]

        # remove the exponents
        tmpUpper = [unit._removeExponentFromUnit(elem) for elem in upper]
        tmpLower = [unit._removeExponentFromUnit(elem) for elem in lower]
        upper = [elem[0] for elem in tmpUpper]
        tmpUpperExp = [elem[1]for elem in tmpUpper]
        lower = [elem[0] for elem in tmpLower]
        tmpLowerExp = [elem[1]for elem in tmpLower]

        upperSet = list(set(upper))
        lowerSet = list(set(lower))
        lenUpperSet = len(upperSet)
        lenLowerSet = len(lowerSet)
        upperExp = [0] * lenUpperSet
        lowerExp = [0] * lenLowerSet
        upperPrefix = [None] * lenUpperSet
        lowerPrefix = [None] * lenLowerSet
        for i, u in enumerate(upperSet):
            indexes = [_ for _, elem in enumerate(upper) if elem == u]
            upperExp[i] = sum([tmpUpperExp[elem] for elem in indexes])
        for i, l in enumerate(lowerSet):
            indexes = [_ for _, elem in enumerate(lower) if elem == l]
            lowerExp[i] = sum([tmpLowerExp[elem] for elem in indexes])
        upper, lower = upperSet, lowerSet

        upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp = unit._cancleUnits(
            upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp
        )

        return unit._combineUpperAndLower(upper, upperPrefix, upperExp, lower, lowerPrefix, lowerExp)

    def getConverter(self, newUnit):
        newUnit = unit._formatUnit(newUnit)

        # get the upper, upperExp, lower and lowerExp of the newUnit without creating a unit
        otherUpper, otherUpperPrefix, otherUpperExp, otherLower, otherLowerPrefix, otherLowerExp = self._getLists(newUnit)

        # determine if the SI bases are identical
        otherSIBase = self._getSIBaseUnit(otherUpper, otherUpperExp, otherLower, otherLowerExp)
        try:
            unit._assertEqualStatic(self._SIBaseUnit, otherSIBase)
        except ValueError:
            raise ValueError(f'You tried to convert from {self} to {newUnit}. But these do not have the same base units')

        # initialize the scale and offset
        out = _unitConversion(1, 0)

        # get conversions for all upper and lower units in self
        upperConversions = [knownUnits[elem][1] for elem in self.upper]
        lowerConversions = [knownUnits[elem][1] for elem in self.lower]

        # modify the scale and offset using the conversions
        conversions = upperConversions + lowerConversions
        conversionBool = [True] * len(upperConversions) + [False] * len(lowerConversions)
        prefixes = self.upperPrefix + self.lowerPrefix
        exponents = self.upperExp + self.lowerExp
        for conv, prefix, exp, upperBool in zip(conversions, prefixes, exponents, conversionBool):
            if not prefix is None:
                conv *= knownPrefixes[prefix]
            for _ in range(exp):
                if upperBool:
                    out *= conv
                else:
                    out /= conv

        # get all conversions from the upper and lower units in the new unit
        upperConversions = [knownUnits[elem][1] for elem in otherUpper]
        lowerConversions = [knownUnits[elem][1] for elem in otherLower]

        # modify the scale and offset based on the conversions
        conversions = upperConversions + lowerConversions
        conversionBool = [True] * len(upperConversions) + [False] * len(lowerConversions)
        prefixes = otherUpperPrefix + otherLowerPrefix
        exponents = otherUpperExp + otherLowerExp
        for conv, prefix, exp, upperBool in zip(conversions, prefixes, exponents, conversionBool):
            if not prefix is None:
                conv *= knownPrefixes[prefix]

            for _ in range(exp):
                # the multiply and divisions are swapped because the conversion is away from the SI unit system
                if upperBool:
                    out /= conv
                else:
                    out *= conv

        return out


if __name__ == '__main__':
    a = unit('m')
    b = a**2
    print(type(b))
