
# Fitting
The package includes a tool to produce fits. The following fits are known
 - Linear fit
 - Polynomial fit
 - Power fit
 - Exponential fit
 - Logistic fit
 - Logistic fit with a fixed maximum value of 100

```
F_lin = lin_fit(x: variable,y: variable)
F_pol = pol_fit(x: variable,y: variable, deg:int = 2)
F_pow = pow_fit(x: variable,y: variable)
F_exp = exp_fit(x: variable,y: variable)
F_logistic = logistic_fit(x: variable,y: variable)
F_logistic_100 = logistic_100_fit(x: variable,y: variable)
```


## Priting
The fit can be printed. This is done in latex format. First the model is printed, and then the coefficients are printed.

```
print(pol_fit) -> str
```

## Predict
Once a fit has been made this can be used to create a prediction. The input can either be a float or a variable. If the float is a variable it is assued to have the same unit as the x-data used to generate the fit-object.

```
pol_fit.predict(x: float | variable) -> variable
```

## Predict differential
Once a fit has been made this can be used to create a prediction of the differential. The input can either be a float or a variable. If the float is a variable it is assued to have the same unit as the x-data used to generate the fit-object.

```
pol_fit.predictDifferential(x: float | variable) -> variable
```