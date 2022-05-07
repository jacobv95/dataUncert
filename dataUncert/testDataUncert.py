import unittest
from testFit import test as testFit
from testReadData import test as testReadData
from testUnitSystem import test as testUnitSystem
from testVariable import test as testVariable


def main():
    tests = [
        testFit,
        testReadData,
        testUnitSystem,
        testVariable
    ]

    suites = []
    for test in tests:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    suite = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()