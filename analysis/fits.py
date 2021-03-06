import numpy
import scipy.integrate
import scipy_data_fitting

import data
import models

class Fig4(scipy_data_fitting.Fit):
    """
    Fit for Figure 4 in PhysRevLett.105.167202.

    Must supply `subfig` in the form `(subfig_letter, contact_spacing_(L))`,
    e.g. `('a', 2.1)`.

    Should not be used directly, but only subclassed.
    The subclass must define `self.init()` to setup the fit details.
    """

    def __init__(self, subfig):
        super().__init__()
        self.subfig = subfig[0]
        self.param_length = subfig[1]
        self.name = 'fig_4' + self.subfig
        self.description = 'Figure 4' + self.subfig
        self.options['maxfev'] = 1000000
        self.init()

class NonZeroField(Fig4):
    """
    Fit for Figure 4 in PhysRevLett.105.167202 using `fits.NonZeroField`.

    Must set `self.expression` and `self.data` before using.
    """

    def __init__(self, subfig, zero_theta=False):
        self.zero_theta = zero_theta
        super().__init__(subfig)

    def init(self):
        self.model = models.NonZeroField()

        if self.zero_theta:
            self.name = self.name + '_infinite_contact_resistance'
            self.description = self.description + ', R_C → ∞'

        self.options['fit_function'] = 'lmfit'

        self.replacements = ['ratios', 'ω', "p, p' to P", 'resistances', 'λ', 'Ω_F', 'A_J']
        if self.zero_theta: self.replacements.insert(0, 'θ_zero')

        self.independent = {'symbol': 'B', 'name': 'Magnetic Field', 'units': 'T'}
        self.dependent = {'name': 'Nonlocal resistance', 'units': 'Ω'}

        if self.subfig == 'd':
            self.dependent['units'] = 'mΩ'
            self.dependent['prefix'] = 'milli'

        self.quantities = [
            {'expression': 'ζ', 'name': 'W/λ'},
            {'expression': 'θ', 'name': 'λ/r'},
            {'expression': 'ϕ', 'name': 'L/λ'},
            {'expression': 'λ', 'name': 'λ', 'prefix': 'micro', 'units': 'μm'},
            {'expression': 'r', 'name': 'r', 'prefix': 'micro', 'units': 'μm'},
            {'expression': 'Ω_F', 'name': 'Ω_F', 'units': 'Ω'},
            {'expression': 'R_N', 'name': 'R_N', 'units': 'Ω'},
        ]
        # Delete θ and r.
        # If the order changes above these indexes must be updated.
        if self.zero_theta:
            del self.quantities[1]
            del self.quantities[3]

        self.constants = [
            {'symbol': 'ħ', 'value': 'Planck constant over 2 pi'},
            {'symbol': 'μ_B', 'value': 'Bohr magneton'},
            {'symbol': 'g', 'value': 2},
        ]

        self.parameters = [
            {'symbol': 'L', 'value': self.param_length, 'prefix': 'micro', 'units': 'μm'},
            {'symbol': 'W', 'value': 2.2, 'prefix': 'micro', 'units': 'μm'},
            {'symbol': 'W_F', 'value': 1.0, 'prefix': 'micro', 'units': 'μm'},
            {'symbol': 'σ_G', 'value': 0.5, 'prefix': 'milli', 'units': 'mS'},

            {'symbol': 'ρ_F', 'value': 60, 'prefix': 'nano', 'units': 'Ω nm'},
            {'symbol': 'λ_F', 'value': 0.06, 'prefix': 'micro', 'units': 'μm'},
            {'symbol': 'd', 'value': 0.5, 'prefix': 'nano', 'units': 'nm'},

            # This is self.parameters[7].
            # If this changes index, update NonZeroFieldNormalized below.
            {'symbol': 'P', 'guess': 0.7,
                'lmfit': {'min': 0, 'max': 1}},

            # This is self.parameters[8].
            {'symbol': 'Ω_C', 'guess': 1, 'prefix': 'kilo', 'units': 'kΩ',
                'lmfit': {'min': 0, 'max': 10**8}},

            # This is self.parameters[9].
            {'symbol': 'τ', 'guess': 100, 'prefix': 'pico', 'units': 'ps',
                'lmfit': {'min': 0, 'max': 10**8}},

            {'symbol': 'D', 'guess': 0.011, 'units': 'm^2 / s',
                'lmfit': {'min': 0, 'max': 10**8}},
        ]
        # Delete and Ω_C.
        # If the order changes above this index must be updated.
        if self.zero_theta: del self.parameters[8]

class NonZeroFieldParallel(NonZeroField):
    """
    The parallel field fit to Figure 4 in PhysRevLett.105.167202.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_parallel'
        self.description = self.description + ', Parallel'
        self.expression = 'nonlocal_resistance_scaled'
        self.data = data.Fig4Parallel(self.subfig)

class NonZeroFieldAntiparallel(NonZeroField):
    """
    The antiparallel field fit to Figure 4 in PhysRevLett.105.167202.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_antiparallel'
        self.description = self.description + ', Antiparallel'
        self.expression = 'nonlocal_resistance_scaled_antiparallel'
        self.data = data.Fig4Antiparallel(self.subfig)

class NonZeroFieldDifference(NonZeroField):
    """
    The field difference fit to Figure 4 in PhysRevLett.105.167202.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_difference'
        self.description = self.description + ', Difference'
        self.expression = 'nonlocal_resistance_scaled_difference'
        self.data = data.Fig4Difference(self.subfig)

class NonZeroFieldNormalized(NonZeroField):
    """
    The normalized field fit to Figure 4 in PhysRevLett.105.167202.

    Must set `self.expression` and `self.data` before using.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_normalized'
        self.description = self.description + ', Normalized'
        self.dependent = {'name': 'Normalized nonlocal resistance'}
        del self.parameters[7]

class NonZeroFieldNormalizedParallel(NonZeroFieldNormalized):
    """
    The normalized parallel field fit to Figure 4 in PhysRevLett.105.167202.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_parallel'
        self.description = self.description + ', Parallel'
        self.expression = 'f/f0'
        self.data = data.Fig4NormalizedParallel(self.subfig)

class NonZeroFieldNormalizedAntiparallel(NonZeroFieldNormalized):
    """
    The normalized antiparallel field fit to Figure 4 in PhysRevLett.105.167202.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_antiparallel'
        self.description = self.description + ', Antiparallel'
        self.expression = '-f/f0'
        self.data = data.Fig4NormalizedAntiparallel(self.subfig)

class NonZeroFieldNormalizedDifference(NonZeroFieldNormalized):
    """
    The normalized difference field fit to Figure 4 in PhysRevLett.105.167202.
    """

    def __init__(self, subfig, zero_theta=False):
        super().__init__(subfig, zero_theta)
        self.name = self.name + '_difference'
        self.description = self.description + ', Difference'
        self.expression = 'abs(f/f0)'
        self.data = data.Fig4NormalizedDifference(self.subfig)

class TransparentContacts(Fig4):
    """
    The fit to Figure 4 in PhysRevLett.105.167202 using the
    transparent contact model.

    Must set `self.dependent` and `self.data` before using.
    """

    def init(self):
        self.name = self.name + '_transparent_contacts'
        self.description = self.description + ', Transparent Contacts'
        self.model = models.TransparentContacts()

        self.options['fit_function'] = 'lmfit'

        self.replacements = ['D', 'τ', 'a']

        self.dependent = {'name': 'Non-local resistance', 'units': 'Ω'}
        self.independent = {'symbol': 'B', 'name': 'Magnetic Field', 'units': 'T'}

        if self.subfig == 'd':
            self.dependent['units'] = 'mΩ'
            self.dependent['prefix'] = 'milli'

        self.free_variables = ['u']

        s = self.model.symbol
        self.quantities = [
            {'expression': s('τ'), 'name': 'τ', 'prefix': 'pico', 'units': 'ps'},
            {'expression': s('D'), 'name': 'D', 'units': 'm^2 / s'},
            {'expression': 'λ', 'name': 'λ', 'prefix': 'micro', 'units': 'μm'},
            {'expression': 'L/λ', 'name': 'L/λ'},
        ]

        self.constants = [
            {'symbol': 'ħ', 'value': 'Planck constant over 2 pi'},
            {'symbol': 'μ_B', 'value': 'Bohr magneton'},
        ]

        self.parameters = [
            {'symbol': 'L', 'value': self.param_length, 'prefix': 'micro', 'units': 'μm'},

            {'symbol': 'A', 'guess': 0.3, 'prefix': 'kilo', 'units': 'kΩ', 'lmfit': {'min': 0}},
            {'symbol': 'α', 'guess': 50, 'lmfit': {'min': 0}},
            {'symbol': 'β', 'guess': 0.25, 'lmfit': {'min': 0}},
        ]

        self.expression = 'integrand'
        integrand = self.function
        integral_function = lambda *x: scipy.integrate.quad(integrand, 0, numpy.inf, args=x)[0]
        self.function = numpy.vectorize(integral_function)

class TransparentContactsParallel(TransparentContacts):
    """
    The parallel field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_parallel'
        self.description = self.description + ', Parallel'
        self.data = data.Fig4Parallel(self.subfig)

class TransparentContactsAntiparallel(TransparentContacts):
    """
    The antiparallel field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_antiparallel'
        self.description = self.description + ', Antiparallel'
        self.data = data.Fig4Antiparallel(self.subfig)
        f = numpy.vectorize(self.function)
        self.function = lambda *x: -1 * f(*x)

class TransparentContactsDifference(TransparentContacts):
    """
    The difference field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_difference'
        self.description = self.description + ', Difference'
        self.data = data.Fig4Difference(self.subfig)
        f = numpy.vectorize(self.function)
        self.function = lambda *x: 2 * abs(f(*x))

class TransparentContactsNormalized(TransparentContacts):
    """
    The normalized field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_normalized'
        self.description = self.description + ', Normalized'

        del self.parameters[1]
        self.constants.append({'symbol': 'A', 'value': 1})

        del self._function
        self.expression = 'integrand'
        integrand = numpy.vectorize(self.function)
        integral_function = lambda *x: scipy.integrate.quad(integrand, 0, numpy.inf, args=x)[0]

        del self._function
        self.expression = 'integrand, B = 0'
        normalization_integrand = numpy.vectorize(self.function)
        normalization_integral_function = lambda *x: scipy.integrate.quad(normalization_integrand, 0, numpy.inf, args=x)[0]

        f = lambda *x: integral_function(*x) / normalization_integral_function(*x)
        self.function = numpy.vectorize(f)

class TransparentContactsNormalizedParallel(TransparentContactsNormalized):
    """
    The normalized parallel field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_parallel'
        self.description = self.description + ', Parallel'
        self.data = data.Fig4NormalizedParallel(self.subfig)

class TransparentContactsNormalizedAntiparallel(TransparentContactsNormalized):
    """
    The normalized antiparallel field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_antiparallel'
        self.description = self.description + ', Antiparallel'
        self.data = data.Fig4NormalizedAntiparallel(self.subfig)
        f = numpy.vectorize(self.function)
        self.function = lambda *x: -1 * f(*x)

class TransparentContactsNormalizedDifference(TransparentContactsNormalized):
    """
    The normalized difference field fit to Figure 4 in PhysRevLett.105.167202
    using the transparent contact model.
    """

    def __init__(self, subfig):
        super().__init__(subfig)
        self.name = self.name + '_difference'
        self.description = self.description + ', Difference'
        self.data = data.Fig4Difference(self.subfig)
        f = numpy.vectorize(self.function)
        self.function = lambda *x: abs(f(*x))
