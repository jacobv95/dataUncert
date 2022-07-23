import numpy as np

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

# determine the known characters within the unit system
knownCharacters = ''.join(list(knownUnits.keys()))
knownCharacters += ''.join(list(knownPrefixes.keys()))
knownCharacters += '-/'
knownCharacters += '0123456789'
knownCharacters = ''.join(list(set(knownCharacters)))
