
# Variables

You can create a variables as follows

```
var = variable(val: float | list | ndarray, unit: str, uncert=None: float | list | ndarray | None, nDigits = 3: int)
```

 - val is the value of the variable
 - unit is the unit of the variable
 - uncert is the uncertanty of the variable
 - nDigits is the number of significant digits used to print the variable, if the uncertanty is None or 0

## Units
The unit is used to determine which computations can be performed:
 - Two variables can be added together or subtracted from each other if their units are identical
 - Any two units can be multiplied or divided
 - Exponents cannot have any units
 - A variable with a unit can be raised to an integer power
 - The n'th root of a variable can be taken if the exponent of the unit of the variable is divisible by n

The denominator and the numerator of the unit is seperated using a dash (/).
The units in the denominator or numerator are sperated using a hyphen (-)


The following units are known:
 - unitless: 1, ''
 - force: N
 - mass: g
 - Energy: J
 - power: W
 - pressure: Pa, bar
 - Temperature: K, C, F
 - time: s, min, h, yr
 - volume: m3, L
 - length: m
 - current: A
 - Voltage: V
 - Angles: rad, °


The following prefixes are known:
 - µ: 1e-6 (ASCII 230)
 - m: 1e-3
 - k: 1e3
 - M: 1e6

### examples
 - milli Liters per minute:               'mL/min'
 - Cubicmeter-kilogram per second:  'm3-kg/s


## Printing
The uncertanty is printed with one significant digit. The measurement is printed with the same number of decimal places as the uncertanty. This means that if the uncertanty is a factor of 10 larger than the measurement, then the variable is printed as zero.

### Examples
```
print(variable(12.3,'m',0.01))
>> 12.30 +/- 0.01 [m]

print(variable(12.34,'m',0.))
>> 12.3 +/- 0.1 [m]

print(variable(1234,'m',16))
>> 1230 +/- 20 [m]

print(variable(12.34,'m',16))
>> 10 +/- 20 [m]

print(variable(1.234,'m',16))
>> 0 +/- 20 [m]
```


## Convert
A variable can be converted to another unit using the convert method.

```
variable.convert(unit: str)
```



## operators
 - add
 - subtract
 - multiply
 - divide
 - power
 - np.sqrt
 - np.exp
 - np.sin
 - np.cos
 - np.tan
 - np.mean
 - np.min
 - np.max
 - np.log
 - np.log10
 - np.sqrt

