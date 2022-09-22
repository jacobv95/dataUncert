import logging
logging.disable(logging.CRITICAL)
import unittest
from testFit import test as testFit
from testReadData import test as testReadData
from testUnit import test as testUnit
from testVariable import test as testVariable
from testProp import test as testProp


def main():
    tests = [
        testFit,
        testReadData,
        testUnit,
        testVariable,
        testProp
    ]

    suites = []
    for test in tests:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    suite = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()
