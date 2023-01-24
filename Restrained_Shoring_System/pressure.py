'''
1) cohesion less soils :
    1-1-single anchor/brace
    1-2-multi anchors/braces
2) cohesive soils:
    2-1-single anchor/brace
    2-2-multi anchors/braces
'''

from sympy import symbols
from sympy.solvers import solve
from math import sqrt


class anchor_pressure:
    def __init__(self, h, gama, c, ka, kp):
        self.h = h
        self.gama = gama
        self.c = c
        self.ka = ka
        self.kp = kp

    # soil pressure
    def soil_pressure(self):
        h = self.h
        gama = self.gama
        ka = self.ka
        kp = self.kp
        c = self.c

        D = symbols("D")
        sigma_active1 = ka * h * gama - c * sqrt(ka)
        sigma_active2 = ka * (h + D) * gama - c * sqrt(ka)
        sigma_passive1 = 0
        sigma_passive2 = kp * D * gama + c * sqrt(kp)
        sigma_active = [sigma_active1, sigma_active2]
        sigma_passive = [sigma_passive1, sigma_passive2]
        return sigma_active, sigma_passive

    # calculate sigma a for 1-1 situation.
    def pressure_cohesion_less_single(self, h1):
        h = self.h
        gama = self.gama
        ka = self.ka

        h_list = [(2 / 3) * h1, (1 / 3) * h, (2 / 3) * (h - h1)]

        P = 0.5 * gama * ka * (h ** 2)
        f = 1.3
        sigma_a = f * P / ((2 / 3) * h)
        return sigma_a, h_list

    def pressure_cohesion_less_multi(self, n, h1, hn):
        h = self.h
        gama = self.gama
        ka = self.ka

        h_list = [(2 / 3) * h1, h - ((2 / 3) * h1 + (2 / 3) * hn), (2 / 3) * hn]

        P = 0.5 * gama * ka * (h ** 2)
        f = 1.3
        sigma_a = f * P / (h - ((1 / 3) * (h1 + hn)))
        return sigma_a, h_list

    def pressure_cohesive(self, gama_s, h1):
        h = self.h
        gama = self.gama
        c = self.c
        ka = self.ka

        h_list = [(2 / 3) * h1, h - ((2 / 3) * h1), 0]

        Ns = gama_s * h / c
        if Ns <= 4:
            sigma_a = 0.2 * gama_s * h  # to 0.4 * gama_s * h  ??! ASK
        elif Ns >= 6:
            sigma_a = ka * gama_s * h
            # another equation for ka is defined. is that necessary? ASK
        else:
            sigma_a1 = 0.2 * gama_s * h
            sigma_a2 = ka * gama_s * h
            sigma_a = max(sigma_a1, sigma_a2)
        return sigma_a, h_list


test = anchor_pressure(25, 115, 0, 1 / 3, 4.7)
sigma_active, sigma_passive = test.soil_pressure()
sigma_a, h_list = test.pressure_cohesion_less_single(10)
