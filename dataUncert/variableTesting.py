import unittest
import numpy as np
try:
    from dataProcessing.variable import variable
except ModuleNotFoundError:
    from variable import variable


class test(unittest.TestCase):

    def test_add(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'L/min', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'L/min', uncert=[53.9, 24.75, 6.4])

        C = A + B
        self.assertAlmostEqual(C.value, 12.3 + 745.1)
        self.assertEqual(C.unit, 'L/min')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2))

        C.convert('m3/s')
        self.assertAlmostEqual(C.value, (12.3 + 745.1) / 1000 / 60)
        self.assertEqual(C.unit, 'm3/s')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6 / 1000 / 60)**2 + (1 * 53.9 / 1000 / 60)**2))

        C_vec = A_vec + B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 + 745.1, 54.3 + 496.13, 91.3 + 120.54]))
        self.assertEqual(C_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 24.75)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 6.4)**2),
            ]))

        C_vec.convert('mL/h')
        np.testing.assert_almost_equal(C_vec.value, np.array([(12.3 + 745.1) * 1000 * 60, (54.3 + 496.13) * 1000 * 60, (91.3 + 120.54) * 1000 * 60]))
        self.assertEqual(C_vec.unit, 'mL/h')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6 * 1000 * 60)**2 + (1 * 53.9 * 1000 * 60)**2),
                np.sqrt((1 * 5.4 * 1000 * 60)**2 + (1 * 24.75 * 1000 * 60)**2),
                np.sqrt((1 * 10.56 * 1000 * 60)**2 + (1 * 6.4 * 1000 * 60)**2),
            ]))

    def test_sub(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'L/min', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'L/min', uncert=[53.9, 24.75, 6.4])

        C = A - B
        self.assertAlmostEqual(C.value, 12.3 - 745.1)
        self.assertEqual(C.unit, 'L/min')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2))

        C.convert('kL/s')
        self.assertAlmostEqual(C.value, (12.3 - 745.1) / 1000 / 60)
        self.assertEqual(C.unit, 'kL/s')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 * 2.6 / 1000 / 60)**2 + (1 * 53.9 / 1000 / 60)**2))

        C_vec = A_vec - B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 - 745.1, 54.3 - 496.13, 91.3 - 120.54]))
        self.assertEqual(C_vec.unit, 'L/min')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6)**2 + (1 * 53.9)**2),
                np.sqrt((1 * 5.4)**2 + (1 * 24.75)**2),
                np.sqrt((1 * 10.56)**2 + (1 * 6.4)**2),
            ]))

        C_vec.convert('mm3 / h')
        np.testing.assert_almost_equal(C_vec.value, np.array([12.3 - 745.1, 54.3 - 496.13, 91.3 - 120.54]) * 1000000 * 60, decimal=5)
        self.assertEqual(C_vec.unit, 'mm3/h')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 * 2.6 * 1000000 * 60)**2 + (1 * 53.9 * 1000000 * 60)**2),
                np.sqrt((1 * 5.4 * 1000000 * 60)**2 + (1 * 24.75 * 1000000 * 60)**2),
                np.sqrt((1 * 10.56 * 1000000 * 60)**2 + (1 * 6.4 * 1000000 * 60)**2),
            ]), decimal=5)

        with self.assertRaises(Exception) as context:
            A.convert('m')
        self.assertTrue('You cannot convert from [L/min] to [m]' in str(context.exception))

    def test_add_with_different_units(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            A + B
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec + B_vec
        self.assertTrue('You tried to add a variable in [L/min] to a variable in [m], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A.convert('m')
        self.assertTrue('You cannot convert from [L/min] to [m]' in str(context.exception))

    def test_sub_with_different_units(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            A - B
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec - B_vec
        self.assertTrue('You tried to subtract a variable in [m] from a variable in [L/min], but the units does not match' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A.convert('m')
        self.assertTrue('You cannot convert from [L/min] to [m]' in str(context.exception))

    def test_multiply(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        C = A * B

        self.assertAlmostEqual(C.value, 12.3 * 745.1)
        self.assertEqual(C.unit, 'L-m/min')
        self.assertAlmostEqual(C.uncert, np.sqrt((745.1 * 2.6)**2 + (12.3 * 53.9)**2))

        C_vec = A_vec * B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 * 745.1, 54.3 * 496.13, 91.3 * 120.54]))
        self.assertEqual(C_vec.unit, 'L-m/min')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((745.1 * 2.6)**2 + (12.3 * 53.9)**2),
                np.sqrt((496.13 * 5.4)**2 + (54.3 * 24.75)**2),
                np.sqrt((120.54 * 10.56)**2 + (91.3 * 6.4)**2),
            ]))

        C_vec.convert('m3-km / s')
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 * 745.1, 54.3 * 496.13, 91.3 * 120.54]) / 1000 / 1000 / 60)
        self.assertEqual(C_vec.unit, 'm3-km/s')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((745.1 / 1000 * 2.6 / 1000 / 60)**2 + (12.3 / 1000 / 60 * 53.9 / 1000)**2),
                np.sqrt((496.13 / 1000 * 5.4 / 1000 / 60)**2 + (54.3 / 1000 / 60 * 24.75 / 1000)**2),
                np.sqrt((120.54 / 1000 * 10.56 / 1000 / 60)**2 + (91.3 / 1000 / 60 * 6.4 / 1000)**2),
            ]), decimal=7)

    def test_divide(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])

        C = A / B
        self.assertAlmostEqual(C.value, 12.3 / 745.1)
        self.assertEqual(C.unit, 'L/min-m')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 / 745.1 * 2.6)**2 + (12.3 / (745.1**2) * 53.9)**2))

        C.convert('m3/h-mm')
        self.assertAlmostEqual(C.value, 12.3 / 745.1 / 1000 * 60 / 1000)
        self.assertEqual(C.unit, 'm3/h-mm')
        self.assertAlmostEqual(C.uncert, np.sqrt((1 / (745.1 * 1000) * 2.6 / 1000 * 60)**2 + (12.3 / ((745.1)**2) * 53.9 / 1000 * 60 / 1000)**2))

        C_vec = A_vec / B_vec
        np.testing.assert_array_equal(C_vec.value, np.array([12.3 / 745.1, 54.3 / 496.13, 91.3 / 120.54]))
        self.assertEqual(C_vec.unit, 'L/min-m')
        np.testing.assert_array_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 / 745.1 * 2.6)**2 + (12.3 / (745.1)**2 * 53.9)**2),
                np.sqrt((1 / 496.13 * 5.4)**2 + (54.3 / (496.13)**2 * 24.75)**2),
                np.sqrt((1 / 120.54 * 10.56)**2 + (91.3 / (120.54)**2 * 6.4)**2),
            ]))

        C_vec.convert('m3 / h -mm')
        np.testing.assert_almost_equal(C_vec.value, np.array([12.3 / 745.1, 54.3 / 496.13, 91.3 / 120.54]) / 1000 * 60 / 1000)
        self.assertEqual(C_vec.unit, 'm3/h-mm')
        np.testing.assert_almost_equal(
            C_vec.uncert,
            np.array([
                np.sqrt((1 / 745.1 * 2.6 / 1000 * 60 / 1000)**2 + (12.3 / (745.1)**2 * 53.9 / 1000 * 60 / 1000)**2),
                np.sqrt((1 / 496.13 * 5.4 / 1000 * 60 / 1000)**2 + (54.3 / (496.13)**2 * 24.75 / 1000 * 60 / 1000)**2),
                np.sqrt((1 / 120.54 * 10.56 / 1000 * 60 / 1000)**2 + (91.3 / (120.54)**2 * 6.4 / 1000 * 60 / 1000)**2),
            ]))

    def test_add_unit_order(self):
        A = variable(10, 'm-K')
        B = variable(3, 'K-m')
        A_vec = variable([12.3, 54.3, 91.3], 'K-m', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm-K', uncert=[53.9, 24.75, 6.4])
        C = A + B
        C_vec = A_vec + B_vec

    def test_sub_unit_order(self):
        A = variable(10, 'm-K')
        B = variable(3, 'K-m')
        A_vec = variable([12.3, 54.3, 91.3], 'K-m', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm-K', uncert=[53.9, 24.75, 6.4])
        C = A - B
        C_vec = A_vec - B_vec

    def test_pow(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        B = variable(745.1, 'm', uncert=53.9)
        C = variable(745.1, '1', uncert=53.9)
        D = variable(0.34, '1', uncert=0.01)

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        B_vec = variable([745.1, 496.13, 120.54], 'm', uncert=[53.9, 24.75, 6.4])
        C_vec = variable([745.1, 496.13, 120.54], '1', uncert=[53.9, 24.75, 6.4])
        D_vec = variable([0.34, 0.64, 0.87], '1', uncert=[0.01, 0.084, 0.12])

        with self.assertRaises(Exception) as context:
            A ** B
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            A_vec ** B_vec
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        E = C**D
        self.assertAlmostEqual(E.value, 745.1**0.34)
        self.assertEqual(E.unit, '1')
        self.assertAlmostEqual(E.uncert, np.sqrt((0.34 * 745.1**(0.34 - 1) * 53.9)**2 + (745.1**0.34 * np.log(745.1) * 0.01)**2))

        E_vec = C_vec**D_vec
        np.testing.assert_array_equal(E_vec.value, np.array([745.1**0.34, 496.13**0.64, 120.54**0.87]))
        self.assertEqual(E_vec.unit, '1')
        np.testing.assert_array_equal(
            E_vec.uncert,
            np.array([
                np.sqrt((0.34 * 745.1**(0.34 - 1) * 53.9)**2 + (745.1**0.34 * np.log(745.1) * 0.01)**2),
                np.sqrt((0.64 * 496.13**(0.64 - 1) * 24.75)**2 + (496.13**0.64 * np.log(496.13) * 0.084)**2),
                np.sqrt((0.87 * 120.54**(0.87 - 1) * 6.4)**2 + (120.54**0.87 * np.log(120.54) * 0.12)**2)
            ]))

        F = A**2
        self.assertAlmostEqual(F.value, (12.3)**2)
        self.assertEqual(F.unit, 'L2/min2')
        self.assertAlmostEqual(F.uncert, np.sqrt((2 * 12.3**(2 - 1) * 2.6)**2))

        F.convert('m6/s2')
        self.assertAlmostEqual(F.value, (12.3 / 1000 / 60)**2)
        self.assertEqual(F.unit, 'm6/s2')
        self.assertAlmostEqual(F.uncert, np.sqrt((2 * (12.3 / 1000 / 60)**(2 - 1) * 2.6 / 1000 / 60)**2))

        F_vec = A_vec**2
        np.testing.assert_array_equal(F_vec.value, np.array([(12.3)**2, 54.3**2, 91.3**2]))
        self.assertEqual(F_vec.unit, 'L2/min2')
        np.testing.assert_array_equal(
            F_vec.uncert,
            np.array([
                np.sqrt((2 * 12.3**(2 - 1) * 2.6)**2),
                np.sqrt((2 * 54.3**(2 - 1) * 5.4)**2),
                np.sqrt((2 * 91.3**(2 - 1) * 10.56)**2)
            ]))

        F_vec.convert('m6 / s2')
        np.testing.assert_almost_equal(F_vec.value, np.array([(12.3 / 1000 / 60)**2, (54.3 / 1000 / 60)**2, (91.3 / 1000 / 60)**2]))
        self.assertEqual(F_vec.unit, 'm6/s2')
        np.testing.assert_almost_equal(
            F_vec.uncert,
            np.array([
                np.sqrt((2 * 12.3 / 1000 / 60**(2 - 1) * 2.6 / 1000 / 60)**2),
                np.sqrt((2 * 54.3 / 1000 / 60**(2 - 1) * 5.4 / 1000 / 60)**2),
                np.sqrt((2 * 91.3 / 1000 / 60**(2 - 1) * 10.56 / 1000 / 60)**2)
            ]))

        G = 2.54**D
        self.assertAlmostEqual(G.value, 2.54**0.34)
        self.assertEqual(G.unit, '1')
        self.assertAlmostEqual(G.uncert, np.sqrt((2.54**0.34 * np.log(2.54) * 0.01)**2))

        G_vec = 2.54**D_vec
        np.testing.assert_array_equal(G_vec.value, np.array([2.54**0.34, 2.54**0.64, 2.54**0.87]))
        self.assertEqual(G_vec.unit, '1')
        np.testing.assert_array_equal(
            G_vec.uncert,
            np.array([
                2.54**0.34 * np.log(2.54) * 0.01,
                2.54**0.64 * np.log(2.54) * 0.084,
                2.54**0.87 * np.log(2.54) * 0.12
            ]))

    def test_log(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        C = variable(745.1, '1', uncert=53.9)

        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        C_vec = variable([745.1, 496.13, 120.54], '1', uncert=[53.9, 24.75, 6.4])

        with self.assertRaises(Exception) as context:
            np.log(A)
        self.assertTrue('You can only take the natural log of a variable if it has no unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.log10(A)
        self.assertTrue('You can only take the base 10 log of a variable if it has no unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.log(A_vec)
        self.assertTrue('You can only take the natural log of a variable if it has no unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.log10(A_vec)
        self.assertTrue('You can only take the base 10 log of a variable if it has no unit' in str(context.exception))

        D = np.log(C)
        self.assertAlmostEqual(D.value, np.log(745.1))
        self.assertEqual(D.unit, '1')
        self.assertAlmostEqual(D.uncert, np.sqrt((1 / 745.1) * 53.9)**2)

        D_vec = np.log(C_vec)
        np.testing.assert_array_equal(D_vec.value, np.array([np.log(745.1), np.log(496.13), np.log(120.54)]))
        self.assertEqual(D_vec.unit, '1')
        np.testing.assert_array_equal(
            D_vec.uncert,
            np.array([
                np.sqrt(((1 / 745.1) * 53.9)**2),
                np.sqrt(((1 / 496.13) * 24.75)**2),
                np.sqrt(((1 / 120.54) * 6.4)**2)
            ]))

        E = np.log10(C)
        self.assertAlmostEqual(E.value, np.log10(745.1))
        self.assertEqual(E.unit, '1')
        self.assertAlmostEqual(E.uncert, np.sqrt((1 / (745.1 * np.log10(745.1))) * 53.9)**2)

        E_vec = np.log10(C_vec)
        np.testing.assert_array_equal(E_vec.value, np.array([np.log10(745.1), np.log10(496.13), np.log10(120.54)]))
        self.assertEqual(E_vec.unit, '1')
        np.testing.assert_array_equal(
            E_vec.uncert,
            np.array([
                np.sqrt(((1 / (745.1 * np.log10(745.1))) * 53.9)**2),
                np.sqrt(((1 / (496.13 * np.log10(496.13))) * 24.75)**2),
                np.sqrt(((1 / (120.54 * np.log10(120.54))) * 6.4)**2)
            ]))

    def test_exp(self):
        A = variable(12.3, 'L/min', uncert=2.6)
        C = variable(12.3, '1', uncert=5.39)
        A_vec = variable([12.3, 54.3, 91.3], 'L/min', uncert=[2.6, 5.4, 10.56])
        C_vec = variable([12.3, 54.3, 91.3], '1', uncert=[2.6, 5.4, 10.56])

        with self.assertRaises(Exception) as context:
            np.exp(A)
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        with self.assertRaises(Exception) as context:
            np.exp(A_vec)
        self.assertTrue('The exponent can not have a unit' in str(context.exception))

        D = np.exp(C)
        self.assertAlmostEqual(D.value, np.e**12.3)
        self.assertEqual(D.unit, '1')
        self.assertAlmostEqual(D.uncert, np.sqrt((np.e**12.3 * np.log(np.e) * 5.39)**2))

        D_vec = np.exp(C_vec)
        np.testing.assert_array_equal(D_vec.value, np.array([np.e**12.3, np.e**54.3, np.e**91.3]))
        self.assertEqual(D_vec.unit, '1')
        np.testing.assert_array_equal(
            D_vec.uncert,
            np.array([
                np.sqrt((np.e**12.3 * np.log(np.e) * 2.6)**2),
                np.sqrt((np.e**54.3 * np.log(np.e) * 5.4)**2),
                np.sqrt((np.e**91.3 * np.log(np.e) * 10.56)**2)
            ]))


if __name__ == '__main__':
    unittest.main()
