
# Variables

You can create a variables as follows

```
var = variable(val: float, unit: str, uncert=None)
```

The units work as expected:
 - Two variables can be added together if their units are identical
 - Any two units can be multiplied or divided
 - Exponents cannot have any units

The denominator and the numerator of the unit is seperated using a dash (/).
The in the denominator or numerator are sperated using a hyphen (-)

Here are some examples:
 - milli Liters per minute:               'mL/min'
 - Cubicmeter-kilogram per second:  'm3-kg/s

The following units are known:
 - unitless: 1
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

The following prefixes are known:
 - µ: 1e-6 (ASCII 230)
 - m: 1e-3
 - k: 1e3
 - M: 1e6