import logging
logging.disable(logging.CRITICAL)
import unittest
from dataUncert.unit import unit


class test(unittest.TestCase):

    def testPower(self):
        A = unit('L-kg/min')
        with self.assertRaises(Exception) as context:
            A**1.5
        self.assertEqual('The power has to be an integer', str(context.exception))
        a = A**2
        self.assertEqual(str(a), 'L2-kg2/min2')

        B = unit('m/s2')
        b = B**0
        self.assertEqual(str(b), '1')

        C = unit('L2/h2')
        c = C**0.5
        self.assertEqual(str(c), 'L/h')

    def testMultiply(self):
        a = unit('L/min')
        b = unit('kg-m/L')
        """ (L/min) * (kg-m/L)
            L-kg-m/min-L
            kg-m/min    """
        c = a * b
        self.assertEqual(str(c), 'kg-m/min')

        a = unit('L/min')
        b = unit('L/min')
        c = a * b
        self.assertEqual(str(c), 'L2/min2')

        a = unit('km')
        b = unit('1/m')
        c = a * b
        self.assertEqual(str(c), '1')

    def testDivide(self):

        a = unit('L/min')
        b = unit('L/min')
        c = a / b
        self.assertEqual(str(c), '1')

        a = unit('L/min')
        b = unit('kg-m/L')
        """ L/min / (kg-m/L)
            L/min * L/kg-m
            L2 / min-kg-m """
        c = a / b
        self.assertEqual(str(c), 'L2/min-kg-m')

    def testAdd(self):
        a = unit('L/min')
        b = unit('kg-m/L')
        with self.assertRaises(Exception) as context:
            c = a + b
        self.assertEqual('You tried to add the unit L/min to the unit kg-m/L. These do not match', str(context.exception))
        a = unit('L/min')
        b = unit('L/min')
        c = a + b
        self.assertEqual(str(c), 'L/min')

        a = unit('m-K/L-bar')
        b = unit('K-m/bar-L')
        c = a + b
        self.assertEqual(str(c), 'm-K/L-bar')

    def testSub(self):
        a = unit('L/min')
        b = unit('kg-m/L')
        with self.assertRaises(Exception) as context:
            c = a - b
        self.assertEqual('You tried to add the unit L/min to the unit kg-m/L. These do not match', str(context.exception))
        a = unit('L/min')
        b = unit('L/min')
        c = a - b
        self.assertEqual(str(c), 'L/min')

    def testConvert(self):
        a = unit('L/min')
        converter = a.getConverter('m3/h')
        self.assertAlmostEqual(converter.convert(1), 0.06)

        a = unit('K')
        converter = a.getConverter('C')
        self.assertAlmostEqual(converter.convert(300), 26.85)

        a = unit('C')
        converter = a.getConverter('K')
        self.assertAlmostEqual(converter.convert(0), 273.15)

        a = unit('kJ/kg-C')
        converter = a.getConverter('J/kg-K')
        self.assertAlmostEqual(converter.convert(1, useOffset=False), 1000)

        a = unit('kJ/kg-K')
        converter = a.getConverter('J/kg-F')
        self.assertAlmostEqual(converter.convert(1, useOffset=False), 555.555555555555)

        a = unit('K')
        converter = a.getConverter('F')
        self.assertAlmostEqual(converter.convert(300, useOffset=True), 80.33)

        with self.assertRaises(Exception) as context:
            a = unit('µ')
        self.assertEqual('The unit (µ) was not found. Therefore it was interpreted as a prefix and a unit. Both the prefix and the unit were found. However, the unit "1" cannot have a prefix', str(context.exception))

        with self.assertRaises(Exception) as context:
            a = unit('1/M')
        self.assertEqual('The unit (M) was not found. Therefore it was interpreted as a prefix and a unit. Both the prefix and the unit were found. However, the unit "1" cannot have a prefix', str(context.exception))

        with self.assertRaises(Exception) as context:
            a = unit('1/k')
        self.assertEqual('The unit (k) was not found. Therefore it was interpreted as a prefix and a unit. Both the prefix and the unit were found. However, the unit "1" cannot have a prefix', str(context.exception))

        a = unit('L/min')
        with self.assertRaises(Exception) as context:
            converter = a.getConverter('m')
        self.assertEqual('You tried to convert from L/min to m. But these do not have the same base units', str(context.exception))

    def testInput(self):

        a = unit('m / s')
        self.assertEqual(str(a), 'm/s')

        with self.assertRaises(Exception) as context:
            a = unit('m!/s')
        self.assertEqual('The unit can only contain slashes (/), hyphens (-)', str(context.exception))

        with self.assertRaises(Exception) as context:
            a = unit('m/s/bar')
        self.assertEqual('A unit can only have a single slash (/)', str(context.exception))


if __name__ == '__main__':
    unittest.main()