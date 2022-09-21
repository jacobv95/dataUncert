import CoolProp
from dataUncert.variable import variable


def prop(property, fluid, T, P, C=None):

    # check the property
    if property in knownProperties:
        property = knownProperties[property]
    else:
        raise ValueError(f'The property "{property}" is unknown')

    # check the fluid
    if fluid not in knownFluids:
        raise ValueError(f'The fluid "{fluid}" is unknown')

    # check the pressure
    if not isinstance(P, variable):
        raise ValueError('The pressure has to be a variable')

    # check the temperature
    if not isinstance(T, variable):
        raise ValueError('The temperature has to be a variable')

    # check the concentration
    if not C is None:
        if not isinstance(C, variable):
            raise ValueError('The concentration has to be a variable')
        if not C.unit == '1':
            raise ValueError('The concentration has to be unitless')
        if not (0 < C.value < 1):
            raise ValueError('The concentration has to be within 0 and 1')

    # store the units of the temperature and the pressure
    unitT = T.unit
    unitP = P.unit

    # convert to SI if necessary
    if unitT != 'K':
        T.convert('K')
    if unitP != 'Pa':
        P.convert('Pa')

    var = knownFluids[fluid](property, fluid, T, P, C)

    # convert back from SI if necessary
    if unitT != 'K':
        T.convert(unitT)
    if unitP != 'Pa':
        P.convert(unitP)

    return var


def prop_INCOMP(property, fluid, T, P, C):
    # create a state
    state = CoolProp.AbstractState("INCOMP", fluid)

    # update the state with the concentration, pressure and temperature
    state.set_mass_fractions([C.value])
    state.update(CoolProp.PT_INPUTS, P.value, T.value)

    # determine the value of the property
    val = getattr(state, property[0])()

    # get the gradient d(property)/dT
    try:
        gradT = state.first_partial_deriv(getattr(CoolProp, property[1]), CoolProp.iT, CoolProp.iP)
    except ValueError:
        dT = 1  # K
        state.update(CoolProp.PT_INPUTS, P.value, T.value + dT)
        T1 = getattr(state, property[0])()
        state.update(CoolProp.PT_INPUTS, P.value, T.value - dT)
        T2 = getattr(state, property[0])()
        gradT = (T1 - T2) / (2 * dT)

    # get the gradient d(property)/dP
    try:
        gradP = state.first_partial_deriv(getattr(CoolProp, property[1]), CoolProp.iP, CoolProp.iT)
    except ValueError:
        dP = 1  # Pa
        state.update(CoolProp.PT_INPUTS, P.value + dP, T.value)
        P1 = getattr(state, property[0])()
        state.update(CoolProp.PT_INPUTS, P.value - dP, T.value)
        P2 = getattr(state, property[0])()
        gradP = (P1 - P2) / (2 * dP)

    # get the gradient d(property)/dC - this is done using a finite difference
    dC = 0.001  # %
    state.set_mass_fractions([C.value + dC])
    state.update(CoolProp.PT_INPUTS, P.value, T.value)
    C1 = getattr(state, property[0])()
    state.set_mass_fractions([C.value - dC])
    state.update(CoolProp.PT_INPUTS, P.value, T.value)
    C2 = getattr(state, property[0])()
    gradC = (C1 - C2) / (2 * dC)

    # create the new variable
    var = variable(val, property[2])
    var._addDependents([T, P, C], [gradT, gradP, gradC])
    var._calculateUncertanty()

    return var


def prop_HEOS(property, fluid, T, P, _):
    # create the state
    state = CoolProp.AbstractState("HEOS", fluid)

    # update the state using the temperature and the pressure
    state.update(CoolProp.PT_INPUTS, P.value, T.value)

    # determien the value of the property
    val = getattr(state, property[0])()

    # get the gradient d(property)/dT
    try:
        gradT = state.first_partial_deriv(getattr(CoolProp, property[1]), CoolProp.iT, CoolProp.iP)
    except ValueError:
        dT = 1  # K
        state.update(CoolProp.PT_INPUTS, P.value, T.value + dT)
        T1 = getattr(state, property[0])()
        state.update(CoolProp.PT_INPUTS, P.value, T.value - dT)
        T2 = getattr(state, property[0])()
        gradT = (T1 - T2) / (2 * dT)

    # get the gradient d(property)/dP
    try:
        gradP = state.first_partial_deriv(getattr(CoolProp, property[1]), CoolProp.iP, CoolProp.iT)
    except ValueError:
        dP = 1  # Pa
        state.update(CoolProp.PT_INPUTS, P.value + dP, T.value)
        P1 = getattr(state, property[0])()
        state.update(CoolProp.PT_INPUTS, P.value - dP, T.value)
        P2 = getattr(state, property[0])()
        gradP = (P1 - P2) / (2 * dT)

    # create the new variable
    var = variable(val, property[2])
    var._addDependents([T, P], [gradT, gradP])
    var._calculateUncertanty()

    return var


knownProperties = {
    'rho': ['rhomass', 'iDmass', 'kg/m3'],
    'cp': ['cpmass', 'iCpmass', 'J/kg-K'],
    'mu': ['viscosity', 'iviscosity', 'Pa-s']
}

knownFluids = {
    'water': prop_HEOS,
    'MEG': prop_INCOMP
}
