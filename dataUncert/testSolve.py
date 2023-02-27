from dataUncert import solve, variable
import unittest
import numpy as np
from scipy.optimize import Bounds

tol = 1e-3
solveTol = 1e-12

class test(unittest.TestCase):
    
    def assertRelativeDifference(self, a, b, r):
        assert abs(a-b) < abs(b * r), f"The value {a} and {b} has a greater relative difference than {r}. The difference was {abs(a-b)} and was allowed to be {b*r}"
        


    def testSolveOneLinearEquation(self):
        a = variable(23.7, '', 0.1)
        b = variable(943, '', 12.5)
        def func(x):
            return [a * x, b]
        
        x = solve(func, variable(1,''), tol = solveTol)
        correct = b / a

        self.assertRelativeDifference(x.value, correct.value, tol)
        self.assertRelativeDifference(x.uncert, correct.uncert, tol)
    
    def testSolveOneNonlinearEquation(self):
        a = variable(23.7, '', 0.1)
        b = variable(943, '', 12.5)
        
        def func(x):
            return [a * x**2, b]
        
        x = solve(func, variable(1,''), tol = solveTol)
        correct = (b / a)**(1/2)
        
        self.assertRelativeDifference(x.value, correct.value, tol)
        self.assertRelativeDifference(x.uncert, correct.uncert, tol)
    
    def testSolveTwoLinearEquations(self):
        a = variable(23.7, '', 0.1)
        b = variable(943, '', 12.5)
        c = variable(7.5, '', 0.05)
        d = variable(638, '', 19.7)
        e = variable(293.4, '', 0.3)
        f = variable(156.2, '', 4.2)

        correctY = (f - d*c/a) / (e - d*b/a)
        correctX = (c - b*correctY) / a
        
        def func(x,y):
            eqs = []
            eq1 = [a * x + b * y, c]
            eq2 = [d * x + e * y, f]
            eqs = [eq1, eq2]
            return eqs
        
        x0 = [variable(1,''), variable(1,'')]
        x,y = solve(func, x0, tol = solveTol)
                
        self.assertRelativeDifference(x.value, correctX.value, tol)
        self.assertRelativeDifference(y.value, correctY.value, tol)
        self.assertRelativeDifference(x.uncert, correctX.uncert, tol)
        self.assertRelativeDifference(y.uncert, correctY.uncert, tol)

    def testSolveTwoNonlinearEquations(self):
        a = variable(23.7, '', 0.1)
        b = variable(943, '', 12.5)
        c = variable(7.5, '', 0.05)
        d = variable(638, '', 19.7)
        e = variable(293.4, '', 0.3)
        f = variable(156.2, '', 4.2)

        ## correct values were found in EES
        correctX=variable(0.244808471375732378, '' ,0.0100245696158427206) 
        correctY=variable(0.0064471164978235798 , '', 0.000159290537914747218) 

        def func(x,y):
            eqs = []
            eq1 = [a * x**2 + b * y, c]
            eq2 = [d * x + e * y**2, f]
            eqs = [eq1, eq2]
            return eqs
        
        x0 = [variable(1,''), variable(1,'')]
        x,y = solve(func, x0, tol = solveTol)
                
        self.assertRelativeDifference(x.value, correctX.value, tol)
        self.assertRelativeDifference(y.value, correctY.value, tol)
        self.assertRelativeDifference(x.uncert, correctX.uncert, tol)
        self.assertRelativeDifference(y.uncert, correctY.uncert, tol)
        
    def testSolveOneLinearEquationWithDifferentUnits(self):
        a = variable(23.7, 'L/min', 0.1)
        b = variable(943, 'm3/h', 12.5)
        def func(x):
            return [a * x, b]
        
        x = solve(func, variable(1,''), tol = solveTol)
        correct = b / a
        
        self.assertRelativeDifference(x.value, correct.value, tol)
        self.assertRelativeDifference(x.uncert, correct.uncert, tol)

    def testSolveOneNonlinearEquationWithDifferentUnits(self):
        a = variable(23.7, 'L/min', 0.1)
        b = variable(943, 'm3/h', 12.5)
        
        def func(x):
            return [a * x**2, b]
        
        x = solve(func, variable(1,''), tol = solveTol)
        correct = (b / a)**(1/2)
        
        self.assertRelativeDifference(x.value, correct.value, tol)
        self.assertRelativeDifference(x.uncert, correct.uncert, tol)
    
    def testSolveTwoLinearEquationsWithDifferentUnits(self):
        a = variable(23.7, 'L/min', 0.1)
        b = variable(943, 'm3/h', 12.5)
        c = variable(7.5, 'L/s', 0.05)
        d = variable(638, 'L/h', 19.7)
        e = variable(293.4, 'm3/s', 0.3)
        f = variable(156.2, 'm3/min', 4.2)
        
        
        def func(x,y):
            eqs = []
            eq1 = [a * x + b * y, c]
            eq2 = [d * x + e * y, f]
            eqs = [eq1, eq2]
            return eqs
        
        x0 = [variable(14,''), variable(1,'')]
        x,y = solve(func, x0, tol = 1e-10)

        correctY = (f - d*c/a) / (e - d*b/a)
        correctX = (c - b*correctY) / a
            
        self.assertRelativeDifference(x.value, correctX.value, 1e1 * tol)
        self.assertRelativeDifference(y.value, correctY.value, tol)
        self.assertRelativeDifference(x.uncert, correctX.uncert, tol)
        self.assertRelativeDifference(y.uncert, correctY.uncert, tol)

    def testSolveTwoNonlinearEquationsWithDifferentUnits(self):
        a = variable(0.237, 'L/min', 0.1)
        b = variable(943, 'm3/h', 12.5)
        c = variable(7.5, 'L/s', 0.05)
        d = variable(638, 'L/h', 19.7)
        e = variable(0.2934, 'm3/s', 0.3)
        f = variable(156.2, 'm3/min', 4.2)

        ## correct values were found in EES
        correctX=variable(443.2067798094616700,'',144.9960332892821860) 
        correctY=variable(-2.93347464506229083,'',1.48884088824273296) 

        def func(x,y):
            eqs = []
            eq1 = [a * x**2 + b * y, c]
            eq2 = [d * x + e * y**2, f]
            eqs = [eq1, eq2]
            return eqs
        
        x0 = [variable(1,''), variable(1,'')]
        x,y = solve(func, x0, tol = solveTol)
                
        self.assertRelativeDifference(x.value, correctX.value, tol)
        self.assertRelativeDifference(y.value, correctY.value, tol)
        self.assertRelativeDifference(x.uncert, correctX.uncert, tol)
        self.assertRelativeDifference(y.uncert, correctY.uncert, tol)


    def testSolveOneNonlinearEquationWithBounds1(self):
        a = variable(23.7, 'mbar-min2/L2', 0.1)
        b = variable(943, 'mbar', 12.5)
        correct = (b / a)**(1/2)

        def func(x):
            return [a * x**2, b]
        
        lb = variable(10, 'L/min')
        up = np.inf
        bounds = [[lb, up]]
        
        if lb > correct:
            correct = lb
        if up < correct:
            correct = up
        
        x = solve(func, variable(100,'L/min'), bounds = bounds, tol = solveTol)
        
        self.assertRelativeDifference(x.value, correct.value, tol)

    def testSolveOneNonlinearEquationWithBounds2(self):
        a = variable(23.7, 'mbar-min2/L2', 0.1)
        b = variable(943, 'mbar', 12.5)
        correct = (b / a)**(1/2)

        def func(x):
            return [a * x**2, b]
        
        lb = variable(-10, 'L/min')
        up = variable(4, 'L/min')
        bounds = [[lb, up]]
        
        if lb > correct:
            correct = lb
        if up < correct:
            correct = up
        
        x = solve(func, variable(100,'L/min'), bounds = bounds, tol = solveTol)
        
        self.assertRelativeDifference(x.value, correct.value, tol)

    def testSolveOneNonlinearEquationWithBounds3(self):
        a = variable(23.7, 'mbar-min2/L2', 0.1)
        b = variable(943, 'mbar', 12.5)
        correct = (b / a)**(1/2)

        def func(x):
            return [a * x**2, b]
        
        lb = variable(-10, 'L/min')
        up = variable(4, 'L/min')
        bounds = [lb, up]
        
        if lb > correct:
            correct = lb
        if up < correct:
            correct = up
        
        x = solve(func, variable(100,'L/min'), bounds = bounds, tol = solveTol)
        
        self.assertRelativeDifference(x.value, correct.value, tol)

    def testSolveOneNonlinearEquationWithBounds4(self):
        lbs = [-10, 10]
        ubs = [5, 100]
        
        for lb in lbs:
            for ub in ubs:
                lb, ub = min([lb, ub]), max([lb,ub])
                
                a = variable(23.7, 'mbar-min2/L2', 0.1)
                b = variable(943, 'mbar', 12.5)
                correct = (b / a)**(1/2)
                correct = [correct, -correct]
                
                def func(x):
                    return [a * x**2, b]

                bounds = Bounds([lb], [ub])
                for i in range(len(correct)):
                    if lb > correct[i]:
                        correct[i] = variable(lb, correct[i].unit)
                    if ub < correct[i]:
                        correct[i] = variable(ub, correct[i].unit)
                    
                x = solve(func, variable(100,'L/min'), bounds = bounds, tol = solveTol)
                
                minIndex = np.argmin([abs((elem - x).value) for elem in correct])
                correct = correct[minIndex]
                self.assertRelativeDifference(x.value, correct.value, tol)




## TODO test constraints

if __name__ == '__main__':
    unittest.main()