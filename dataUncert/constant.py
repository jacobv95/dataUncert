from dataUncert.variable import variable


class constant(variable):
    def __init__(self, value, unit) -> None:
        super().__init__(value, unit)

    def __imul__(self, _):
        raise ValueError('You cannot use the method *= on a constant')

    def __iadd__(self, _):
        raise ValueError('You cannot use the method += on a constant')

    def __isub__(self, _):
        raise ValueError('You cannot use the method -= on a constant')

    def __itruediv__(self, _):
        raise ValueError('You cannot use the method /= on a constant')


# g = constant(9.81, 'm/s2')
# c = constant(299792458, 'm/s')
