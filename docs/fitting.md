
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