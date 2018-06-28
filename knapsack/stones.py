# __all__ = ["Curve", "MixedCurve"]


from functools import partial
from numpy import array, exp, ndarray
from pandas import Series


def basic(x, cap=1, ec50=0.5, steep=0, price=1, multiplier=1):
    """
    S-shaped curve similar to sigmoid function. Depending on parameters,
    can be fully concave given x > 0, or have convex and concave parts.

    :param x: input array
    :param cap: max level for function.
    :param ec50: half-efficiency point. Moves curve horizontally, and serves as bend point.
    :param steep: slope coefficient. If < 1, curve will be fully concave on interval (0, +Inf), if > 1, curve will be
    concave before ec50 and convex after.
    :param price: price
    :param multiplier: model coefficient for curve
    :return: float with same dimensions as x.
    """
    if isinstance(x, int) or isinstance(x, float):
        return (cap / (1 + (x / price / cap / ec50) ** (-steep))) * multiplier if x != 0 else 0
    elif isinstance(x, Series) or isinstance(x, ndarray):
        if 0 not in x:
            return array(cap / (1 + (x / price / cap / ec50) ** (-steep))) * multiplier
        else:
            return array([(cap / (1 + (y / price / cap / ec50) ** (-steep))) * multiplier if y != 0 else 0 for y in x])
    #
    # return (cap / (1 + (x / price / cap / ec50) ** (-steep))) * multiplier


def basic_derivative(x, cap, ec50, steep, price=1, multiplier=1):
    numerator = cap * steep * multiplier * (x / (cap * ec50 * price)) ** steep
    denominator = x * (1 + (x / (cap * ec50 * price)) ** steep) ** 2
    return numerator / denominator


def log(x, cap, ec50, steep, price=1, multiplier=1):
    """
     S-shaped curve based on exponential function

    :param x: input array
    :param cap: max level for function.
    :param ec50: half-efficiency point. Moves curve horizontally, and
    serves as bend point.
    :param steep: slope coefficient. If < 1, curve will be fully concave on
    interval (0, +Inf), if > 1, curve will be concave before ec50 and convex
    after.
    :param price:
    :param multiplier:
    :return: float with same dimensions as x.
    """
    return (cap / (1 + exp(-steep * x / price / cap - ec50)) - cap / (1 + exp(steep * ec50))) * multiplier


def log_derivative(x, cap, ec50, steep, price=1, multiplier=1):
    numerator = steep * multiplier * exp(steep * x / price / cap + ec50)
    denominator = (exp(steep * x / price / cap + ec50) + 1) ** 2
    return numerator / denominator


def art(x, a, b, multiplier=1):
    first_term = 100 / (1 + exp(a * exp(x * - a / b)))
    second_term = 100 / (1 + exp(a))
    return (first_term - second_term) * multiplier


def art_derivative(x, a, b, multiplier=1.0):
    numerator = -100 * a * multiplier * exp(a * exp(- (a / b) * x - (a / b)))
    denominator = (exp(a * exp(-a / b) * x) + 1) ** 2

    return numerator / denominator


class Curve(object):
    # TODO LaTeX curve equation rendering
    def __init__(self, cap, ec50, steep, multiplier=1, price=1, curve_type='basic'):
        """
        :param cap: maximum level for function
        :param ec50: half-efficiency point. Moves curve horizontally, and
        serves as bend point.
        :param steep: slope coefficient. If < 1, curve will be fully concave on
        interval (0, +Inf), if < 1, curve will be convex before ec50 and concave
        after.
        :param multiplier: model coefficient for curve
        :param curve_type: regular or logistic response curve, can be 'basic' or 'log'
        """
        self.cap = cap
        self.ec50 = ec50
        self.steep = steep
        self.multiplier = multiplier
        self.price = price
        self.type = curve_type

    @property
    def fun(self):
        if self.type == 'basic':
            return partial(basic,
                           cap=self.cap,
                           ec50=self.ec50,
                           steep=self.steep,
                           price=self.price,
                           multiplier=self.multiplier)
        elif self.type == 'log':
            return partial(log,
                           cap=self.cap,
                           ec50=self.ec50,
                           steep=self.steep,
                           price=self.price,
                           multiplier=self.multiplier)

    @property
    def derivative(self):
        if self.type == 'basic':
            return partial(basic_derivative,
                           cap=self.cap,
                           ec50=self.ec50,
                           steep=self.steep,
                           price=self.price,
                           multiplier=self.multiplier)
        elif self.type == 'log':
            return partial(log_derivative,
                           cap=self.cap,
                           ec50=self.ec50,
                           steep=self.steep,
                           price=self.price,
                           multiplier=self.multiplier)

    def __call__(self, x):
        """
        Calculate response
        :param x: budget
        :return:  float64
        """
        return self.fun(x)


# noinspection PyMissingConstructor
class ArtyomCurve(object):
    def __init__(self, a, b, multiplier=1.0):
        self.a = a
        self.b = b
        self.multiplier = multiplier

    @property
    def fun(self):
        return partial(art, a=self.a, b=self.b, multiplier=self.multiplier)

    @property
    def derivative(self):
        return partial(art_derivative, a=self.a, b=self.b, multiplier=self.multiplier)

    def __call__(self, x):
        return self.fun(x)

        # def __str__(self):
        #     first_term = f'100 / (1 + exp({self.a} * exp(x * - {self.a} / {self.b})))'
        #     second_term = f'100 / (1 + exp({self.a}))'

        #     return first_term + ' - ' + second_term


class MixedCurve(object):
    """
    Mixed curve is designed for POEM and should represent response from one media. Constructed from a basic Curve objects.
    """

    def __init__(self, *curves):
        self.curves = curves

    def __call__(self, x):
        return self.fun(x)

    @property
    def fun(self):
        """
        Callable that can be passed further.
        """

        def f(x):
            return sum([curve(x) for curve in self.curves])

        return f

    @property
    def derivative(self):
        def d(x):
            return sum([curve.derivative(x) for curve in self.curves])

        return d
