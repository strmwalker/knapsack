# __all__ = ["Knapsack", ]

from numpy import array, linspace
from pandas import DataFrame
from scipy.optimize import minimize


class Knapsack(object):
    """
    Optimization solver class.
    """
    notebook_mode = True

    def __init__(self, budget):
        """
        :param budget: total budget for problem
        """
        self.budget = budget
        self.solution = None
        self.__bounds = []
        self.__curves = []

    def get_curves(self):
        """
        :return: Curve objects assigned to this budget
        """
        return self.__curves

    def get_bounds(self):
        """
        :return: bounds for Curve objects assigned to this budget
        """
        return self.__bounds

    def add_curve(self, curve, lower=None, upper=None):
        """
        Add Curve (which essentially means media) to optimization problem.
        :param curve: Curve/MixedCurve instance
        :param upper: Upper bound for budget
        :param lower: Lower bound for budget
        :return:
        """
        if not lower:
            lower = 1
        if not upper:
            upper = self.budget
        self.__curves.append(curve)
        self.__bounds.append([lower, upper])

    @property
    def fun(self):
        def f(x, sign=1.0):
            impact = 0
            for i, curve in enumerate(self.__curves):
                impact += curve(x[i])

            return sign * impact

        return f

    def __call__(self, x):
        """
        Calculate response for given spends.
        :param x: int/float/numpy.ndarray/Series
        :return: float64
        """
        return self.fun(x)

    @property
    def mix(self):
        if self.solution:
            return self.solution.x
        else:
            return [0.0 for _ in self.__curves]

    @property
    def derivative(self):

        # despite most of the time sign == 1.0, this feature is needed if we want to minimize something
        def f(x, sign=1.0):
            return [sign * curve.derivative(x[i]) for i, curve in enumerate(self.__curves)]

        return f

    @property
    def constraints(self):
        """
        Generate callable constraints for SLSQP optimization.
        :return: dict{str, callable, callable}
        """

        def fun(x):
            spend = sum(x)
            return spend - self.budget

        def jac(x):
            return array([1.0 for _ in range(len(x))])

        constraints = (
            {
                'type': 'eq',
                'fun': fun,
                'jac': jac
            },
        )
        return constraints

    @property
    def constraints_cobyla(self):
        """
        Generate callable constraints for SLSQP optimization.
        :return: dict{str, callable, callable}
        """

        def fun(x):
            spend = sum(x)
            return spend - self.budget

        def jac(x):
            return array([1.0 for _ in range(len(x))])

        constraints = (
            {
                'type': 'ineq',
                'fun': fun,
                'jac': jac
            },
        )
        return constraints

    def solve(self, disp=True, maxiter=100):
        """
        Solve optimization problem for budget.
        :param disp: Set to True to print convergence messages
        :param maxiter: Maximum number of iterations to perform
        :return: numpy.array with corresponding budgets
        """
        constraints = self.constraints
        derivative = self.derivative
        x0 = array([bound[0] for bound in self.__bounds])

        self.solution = minimize(
            fun=self.fun,
            x0=x0,
            args=(-1.0,),
            method='SLSQP',
            jac=derivative,
            bounds=self.__bounds,
            constraints=constraints,
            options={
                'disp': disp,
                'maxiter': maxiter
            }
        )

        return self.solution.x

    def plot(self, names=None, budget=None, ext='png'):
        """
        Render all response curves to single plot. If ```notebook_mode``` is ```True```,
        return matplotlib subplot, else save image to file `plot.ext`.
        :param names: verbose names for plot
        :param budget: max x axis for plot
        :param ext: file extension if saving image to disk
        :return:
        """
        if budget:
            x = linspace(0, budget, 1000)
        else:
            x = linspace(0, self.budget + int(self.budget / 100), 1000)

        if names:
            data = {name: curve(x) for name, curve in zip(names, self.__curves)}
        else:
            data = {'y {0}'.format({i + 1}): curve(x) for i, curve in enumerate(self.__curves)}

        lines = DataFrame(
            data=data,
            index=x
        ) \
            .plot(
            kind='line',
            figsize=(12, 10),
            grid=True
        )

        if self.notebook_mode:
            return lines
        else:
            fig = lines.get_figure()
            fig.savefig("plot.".format(ext))
