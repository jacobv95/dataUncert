from dataUncert import prop, variable
import unittest


class test(unittest.TestCase):

    def testAll(self):

        knownFluids = ['water', 'MEG']
        knownProperties = ['rho', 'cp', 'mu']
        concentrations = [None, variable(0.528, '', 0.01)]
        T = variable(30, 'C', 1)
        P = variable(1, 'bar', 0.01)

        ListOfEESvalues = [
            [995.6488633254202760, 4.179823274031803420, 0.000797345918032034399],
            [1062.741908437654730, 3.307943137955305390, 0.00293852572194204309]
        ]

        ListOfEESuncerts = [
            [0.305326939921925818, 0.000335853428220185829, 0.0000169611257895675437],
            [1.322901611941038380, 0.0206790990882194932, 0.000113742449145449859]
        ]

        EESunits = ['kg/m3', 'kJ/kg-K', 'kg/m-s']

        for fluid, concentration, EESvalues, EESuncerts in zip(knownFluids, concentrations, ListOfEESvalues, ListOfEESuncerts):
            for property, EESvalue, EESunit, EESuncert in zip(knownProperties, EESvalues, EESunits, EESuncerts):
                var = prop(property, fluid, T, P, concentration)
                var.convert(EESunit)
                self.assertAlmostEqual(var.value, EESvalue, 6)
                self.assertAlmostEqual(var.uncert, EESuncert, 2)


if __name__ == '__main__':
    unittest.main()
