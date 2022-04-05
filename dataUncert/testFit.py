import unittest
import numpy as np
from fit import *


class test(unittest.TestCase):

    def testConstFit(self):

        # no noise no uncertanty
        x = [1, 2, 3]
        y = [10, 10, 10]
        x = variable(x, 'm')
        y = variable(y, 'C')
        F = pol_fit(x, y, deg=0)
        Fa = F.popt[0]
        self.assertAlmostEqual(Fa.value, 10)
        self.assertEqual(Fa.unit, 'C')
        self.assertAlmostEqual(Fa.uncert, 0)
        self.assertAlmostEqual(F.r_squared, 1)

        # uncertanty
        x = [1, 2, 3]
        y = [10, 10, 10]
        x = variable(x, 'm')
        y = variable(y, 'C', uncert=[1, 1, 1])
        F = pol_fit(x, y, deg=0)
        Fa = F.popt[0]
        self.assertAlmostEqual(Fa.value, 10)
        self.assertEqual(Fa.unit, 'C')
        self.assertAlmostEqual(Fa.uncert, 1 / np.sqrt(3))
        self.assertAlmostEqual(F.r_squared, 1)

        # noise
        x = [1, 2, 3]
        y = [10.1, 9.8, 10.2]
        x = variable(x, 'm')
        y = variable(y, 'C')
        F = pol_fit(x, y, deg=0)
        Fa = F.popt[0]
        self.assertAlmostEqual(Fa.value, 10.03333333)
        self.assertEqual(Fa.unit, 'C')
        self.assertAlmostEqual(Fa.uncert, 0.12018504251)
        self.assertAlmostEqual(F.r_squared, 0)

        # # uncertanty and noise
        x = [1, 2, 3]
        y = [10.1, 9.8, 10.2]
        x = variable(x, 'm')
        y = variable(y, 'C', uncert=[1, 1, 1])
        F = pol_fit(x, y, deg=0)
        Fa = F.popt[0]
        F = pol_fit(x, y, deg=0)
        Fa = F.popt[0]
        self.assertAlmostEqual(Fa.value, 10.03333333)
        self.assertEqual(Fa.unit, 'C')
        # TODO where does 0.12018504251 come from ????
        self.assertAlmostEqual(Fa.uncert, np.sqrt((1 / np.sqrt(3))**2 + (0.12018504251)**2))
        self.assertAlmostEqual(F.r_squared, 0)

    def testLinFit(self):
        a = 2
        b = 10
        n = 100
        x = np.linspace(0, 100, n)
        y = a * x + b
        # y += 10 * np.random.rand(n)

        x = variable(x, 'm')
        y = variable(y, 'C')

        F = lin_fit(x, y)
        Fa = F.popt[0]
        Fb = F.popt[1]

        self.assertAlmostEqual(Fa.value, 2)
        self.assertEqual(Fa.unit, 'C/m')
        self.assertAlmostEqual(Fa.uncert, 0)

        self.assertAlmostEqual(Fb.value, 10)
        self.assertEqual(Fb.unit, 'C')
        self.assertAlmostEqual(Fb.uncert, 0)

        self.assertAlmostEqual(F.r_squared, 1)

    def testPolFit2(self):
        a = 2
        b = 10
        c = 15
        n = 100
        x = np.linspace(0, 100, n)
        y = a * x**2 + b * x + c
        # y += 10 * np.random.rand(n)

        x = variable(x, 'm')
        y = variable(y, 'C')

        F = pol_fit(x, y)
        Fa = F.popt[0]
        Fb = F.popt[1]
        Fc = F.popt[2]

        self.assertAlmostEqual(Fa.value, 2)
        self.assertEqual(Fa.unit, 'C/m2')
        self.assertAlmostEqual(Fa.uncert, 0)

        self.assertAlmostEqual(Fb.value, 10)
        self.assertEqual(Fb.unit, 'C/m')
        self.assertAlmostEqual(Fb.uncert, 0)

        self.assertAlmostEqual(Fc.value, 15)
        self.assertEqual(Fc.unit, 'C')
        self.assertAlmostEqual(Fc.uncert, 0)

        self.assertAlmostEqual(F.r_squared, 1)

    def testPolFit3(self):
        a = 2
        b = 10
        c = 15
        d = 50
        n = 100
        x = np.linspace(0, 100, n)
        y = a * x**3 + b * x**2 + c * x + d
        # y += 10 * np.random.rand(n)

        x = variable(x, 'm')
        y = variable(y, 'C')

        F = pol_fit(x, y, deg=3)
        Fa = F.popt[0]
        Fb = F.popt[1]
        Fc = F.popt[2]
        Fd = F.popt[3]

        self.assertAlmostEqual(Fa.value, 2)
        self.assertEqual(Fa.unit, 'C/m3')
        self.assertAlmostEqual(Fa.uncert, 0)

        self.assertAlmostEqual(Fb.value, 10)
        self.assertEqual(Fb.unit, 'C/m2')
        self.assertAlmostEqual(Fb.uncert, 0)

        self.assertAlmostEqual(Fc.value, 15)
        self.assertEqual(Fc.unit, 'C/m')
        self.assertAlmostEqual(Fc.uncert, 0)

        self.assertAlmostEqual(Fd.value, 50)
        self.assertEqual(Fd.unit, 'C')
        self.assertAlmostEqual(Fd.uncert, 0)

        self.assertAlmostEqual(F.r_squared, 1)


if __name__ == '__main__':
    unittest.main()
