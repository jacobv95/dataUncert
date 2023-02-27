from dataUncert import variable
from scipy.optimize import minimize, Bounds
import numpy as np


def solve(_func, x, *args, bounds = None, constraints = None,**kwargs):
    np.seterr('ignore')
    isVariableList = isinstance(x,list)
    if not isVariableList:
        x = [x]
        n = 1
    else:
        n = len(x)
    
    def func(*x):
        out = _func(*x)
        if not isinstance(out[0], list):
            return [out]
        return out
    
    ## TODO use constraints
    
    if not bounds is None:
        try:
            bbounds = []
            if not isinstance(bounds[0], list):
                bounds = [bounds]
            for xi, b in zip(x, bounds):
                bound = []
                for elem in b:
                    if isinstance(elem, variable):
                        elem.convert(xi.unit)
                        bound.append(elem.value)
                    else:
                        bound.append(elem)
                bbounds.append(bound)
            bounds = bbounds
        except TypeError:           
            pass
    
    ## test if the right number of variables were supplied for the function
    try:
        out = func(*x)
    except TypeError:
        raise ValueError('You supplied the wrong amount of variables for the system of equations')
    
    ## test the equations
    for o in out:
        if (len(o) != 2):
            raise ValueError('Each equation has to be a list of 2 elements')
        for elem in o:
            if not isinstance(elem, variable):
                raise ValueError('Each side of each equation has to be a variable')
    
    ## test if the units match
    for elem in out:
        elem[0] - elem[1]
    
    ## test then number of equations are variables
    if (len(out) != len(x)):
        raise ValueError('You have to supply the same number of equations and variables')

    def convertOutputToSIUnits(out):
        for o in out:
            for elem in o:
                elem.convert(elem._unitObject._SIBaseUnit) 
    
    if n != 1:
        convertOutputToSIUnits(out)
        scales = [(elem[0].value - elem[1].value)**2 for elem in out]
    else:
        scales = [1]
    
    def updateValues(xx):
        for xi, xxi in zip(x,xx):
            xi._value = np.array([xxi],dtype=float)

    def solveValues(xx):
        updateValues(xx)
        out = func(*x)
        convertOutputToSIUnits(out)
        return sum([(elem[0].value - elem[1].value)**2 / s for elem, s in zip(out, scales)])
    
  
    out = minimize(
        solveValues,
        [elem.value for elem in x],
        *args,
        **kwargs,
        bounds = bounds,
        constraints=constraints
    )
    updateValues(out.x)

    # determine the uncertanties
    out = func(*x)
    if not isinstance(out[0],list):
        out = [out]

    if n == 1:   
        ## calculate the residual as the difference between both sides of the equaiton
        residual = out[0][0] - out[0][1]

        ## determine the gradent d(xi)/d(residual) as the inverse of d(residual)/d(xi)
        grad = 1 / residual.dependsOn[x[0]]
        
        ## add the residual as a dependency of the variable and calculate the uncertanty of the varialbe           
        x[0]._addDependents([residual], [grad])
        x[0]._calculateUncertanty()
    else:
        ## create a list of the residuals and the jacobian matrix
        residuals = []
        J = np.zeros([n,n])
        
        ## loop over each equation
        for i, equation in enumerate(out):

            ## add the residual
            residuals.append(equation[0]- equation[1])

            ## loop over the variables
            for j, xj in enumerate(x):
                
                ## add the gradient d(residual)/d(xj) to the jacobian matrix
                if not xj in residuals[i].dependsOn.keys():
                    J[i,j] = 0
                else:
                    J[i,j] = residuals[i].dependsOn[xj]

        # inverse the jacobian
        Jinv = np.linalg.inv(J)
        
        ## add the residuals and a row of the inverse jacobian to each variable and calculate the uncertanty
        for i, xi in enumerate(x):
            grads = Jinv[i,:]
            xi._addDependents(residuals, grads)
            xi._calculateUncertanty()
    
    np.seterr('warn')
    if not isVariableList:
        return x[0]
    return x
