from knapsack import Curve, Knapsack

if __name__ == '__main__':

    # initializing solver (Knapsack class) instance with maximum money for all media
    budget = Knapsack(70874156)
    # maximal budget for every media
    maxb = 70 * 10 ** 6

    # initializing media as Curve instances
    # every Curve is some media like TV, OOH, etc.
    media1 = Curve(397650, 0.5085217, 0.92, 9.168728e-06 / 87.98509)
    media2 = Curve(1336580, 0.941772, 0.9964167, 7.202334e-07)
    media3 = Curve(5.509022, 5000, 0.99, 0.0002982394 / 219)
    media4 = Curve(3191.663, 10000, 0.75, 0.001353697 / 65)
    media5 = Curve(237349.3, 0.9954354, 0.7, 9.501362e-06 / 12.47645)
    media6 = Curve(2961.2209, 100, 0.5, 0.003669801 / 87.98509)
    media7 = Curve(664196.7, 0.662257, 0.92, 1.275716e-06 / 87.98509)

    # adding media to budget
    # in second argument we pass minimum and maximum allowed for media
    budget.add_curve(media1, 10600000, maxb)
    budget.add_curve(media2, 5700000, maxb)
    budget.add_curve(media3, 1923077, maxb)
    budget.add_curve(media4, 8307692, maxb)
    budget.add_curve(media5, 3246154, maxb)
    budget.add_curve(media6, 9791667, maxb)
    budget.add_curve(media7, 15786389, maxb)

    # call to optimize spends between media
    # last line represents optimal budget for every media, e.g. first number
    # stands for media1, second for media2, etc.
    budget.solve()
    """
    Optimization terminated successfully.(Exit mode 0)
    Current function value: -1.0779430709417468
    Iterations: 2
    Function evaluations: 2
    Gradient evaluations: 2
    Out[37]:
    array([7917025.28571427, 4140102.28571439, 10524717.28571427,
           5463179.28571427, 12008692.28571427, 12817025.28571427,
           18003414.28571427])
    """
    print(budget.solution)
    # Out[38]: 1.0779430709417468
    # Old solution found with old optimization method
    print(budget([10900000, 4120000, 8300000, 3246000, 14300000, 14100000, 16000000]))
    # Out[39]: 1.075431463000254
