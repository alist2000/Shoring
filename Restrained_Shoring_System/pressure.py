'''
1) cohesion less soils :
    1-1-single anchor/brace
    1-2-multi anchors/braces
2) cohesive soils:
    2-1-single anchor/brace
    2-2-multi anchors/braces
'''
import copy

from sympy import symbols
from sympy.solvers import solve
import scipy.integrate as spi
from math import sqrt
import numpy as np


class anchor_pressure:
    def __init__(self, h, gama, c, ka, kp, pressure_distribution):
        self.h = h
        self.gama = gama
        self.c = c
        self.ka = ka
        self.kp = kp
        self.pressure_distribution = pressure_distribution

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
        pressure_distribution = self.pressure_distribution

        if pressure_distribution == "Trapezoidal":
            h_list = [(2 / 3) * h1, (1 / 3) * h, (2 / 3) * (h - h1)]
        else:
            h_list = [h, 0, 0]

        P = 0.5 * gama * ka * (h ** 2)
        f = 1.3
        sigma_a = f * P / ((2 / 3) * h)
        return sigma_a, h_list

    def pressure_cohesion_less_multi(self, n, h1, hn):
        h = self.h
        gama = self.gama
        ka = self.ka
        pressure_distribution = self.pressure_distribution

        if pressure_distribution == "Trapezoidal":
            h_list = [(2 / 3) * h1, h - ((2 / 3) * h1 + (2 / 3) * hn), (2 / 3) * hn]
        else:
            h_list = [h, 0, 0]

        P = 0.5 * gama * ka * (h ** 2)
        f = 1.3
        sigma_a = f * P / (h - ((1 / 3) * (h1 + hn)))
        return sigma_a, h_list

    def pressure_cohesive(self, gama_s, h1):
        h = self.h
        gama = self.gama
        c = self.c
        ka = self.ka
        pressure_distribution = self.pressure_distribution

        if pressure_distribution == "Trapezoidal":
            h_list = [(2 / 3) * h1, h - ((2 / 3) * h1)]
        else:
            h_list = [h, 0]

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


def edit_sigma_and_height(sigma, h, delta_h):
    """
    :param sigma:  it's just a number ( sigma_a )
    :param h: h is a list with 3 index
    :param delta_h: delta_h
    :return: edited sigma and h for plot
    """
    if delta_h > 0.1:
        delta_h = 0.1  # minimum allowable delta h

    # count number of decimals
    delta_h_decimal = str(delta_h)[::-1].find('.')
    if delta_h_decimal == -1:
        delta_h_decimal = 0
    sigma_h = []
    n = []
    h_list_edited = []
    for i in range(len(h) + 1):
        if i == 0:
            h_list_edited.append(0)
        else:
            h_list_edited.append(round(h_list_edited[i - 1] + h[i - 1], delta_h_decimal))

    h_array_detail = np.arange(0, sum(h) + delta_h, delta_h)
    h_list_detail = list(h_array_detail)
    h_list_detail[-1] = h_list_edited[-1]
    h_array_detail = np.array(h_list_detail)
    for i in range(len(h_array_detail)):
        h_array_detail[i] = round(h_array_detail[i], delta_h_decimal)
    sigma_a_detail = []
    for z in h_list_detail[:h_list_detail.index(h_list_edited[1]) + 1]:
        sigma_a = (sigma / (h_list_edited[1] - h_list_edited[0])) * z
        sigma_a_copy = copy.deepcopy(sigma_a)
        sigma_a_detail.append(sigma_a_copy)

    for z in h_list_detail[h_list_detail.index(h_list_edited[1]) + 1: h_list_detail.index(h_list_edited[2]) + 1]:
        sigma_a = sigma
        sigma_a_copy = copy.deepcopy(sigma_a)
        sigma_a_detail.append(sigma_a_copy)

    for z in h_list_detail[h_list_detail.index(h_list_edited[2]) + 1:]:
        sigma_a = (-sigma / (h_list_edited[3] - h_list_edited[2])) * (z - h_list_edited[2]) + sigma
        sigma_a_copy = copy.deepcopy(sigma_a)
        sigma_a_detail.append(sigma_a_copy)

    sigma_a_array_detail = np.array(sigma_a_detail)

    # sigma_a_list = [0, sigma, sigma, 0]

    return h_array_detail, sigma_a_array_detail


def edit_sigma_and_height_general(sigma, h, delta_h, h_main):
    x = symbols("x")
    """
    :param sigma: list. any index is a list with two value for pressure on the top and below of layer. and len = len h
    :param h: list. height of any layer is one index.
    :param delta_h: delta
    :return: edited sigma and h for plot
    """
    if delta_h > 0.1:
        delta_h = 0.1  # minimum allowable delta h

    # count number of decimals
    delta_h_decimal = str(delta_h)[::-1].find('.')
    if delta_h_decimal == -1:
        delta_h_decimal = 0

    h_list_edited = []
    for i in range(len(h) + 1):
        if i == 0:
            h_list_edited.append(0)
        else:
            h_list_edited.append(round(h_list_edited[i - 1] + h[i - 1], delta_h_decimal))
    if h_main != 0:
        h_list_edited[-1] = h_main

    h_array_detail = np.arange(0, h_main + delta_h, delta_h)
    for i in range(len(h_array_detail)):
        h_array_detail[i] = round(h_array_detail[i], delta_h_decimal)
    h_list_detail = list(h_array_detail)
    h_list_detail[-1] = h_list_edited[-1]

    # delete extra values
    h_list_detail = delete_same_values(h_list_detail)

    sigma_edited = []
    h_edited = []
    equation_list = []
    for i in range(len(h)):
        if h[i] == 0:
            slope, c = 0, 0
        else:
            slope = (sigma[i][1] - sigma[i][0]) / h[i]
            c = sigma[i][0]
        equation = slope * x + c
        equation_list.append(equation)

    sigma_h_detail = []
    for i in range(len(h)):
        if i == 0:
            for z in h_list_detail[:h_list_detail.index(h_list_edited[1]) + 1]:
                sigma_h = equation_list[i].subs(x, z)
                sigma_h_copy = copy.deepcopy(sigma_h)
                sigma_h_detail.append(float(sigma_h_copy))
        elif i != len(h):
            for z in h_list_detail[
                     h_list_detail.index(h_list_edited[i]) + 1: h_list_detail.index(h_list_edited[i + 1]) + 1]:
                sigma_h = equation_list[i].subs(x, z - h_list_edited[i])
                sigma_h_copy = copy.deepcopy(sigma_h)
                sigma_h_detail.append(float(sigma_h_copy))
        else:
            for z in h_list_detail[h_list_detail.index(h_list_edited[i]) + 1:]:
                sigma_h = equation_list[i].subs(x, z - h_list_edited[i])
                sigma_h_copy = copy.deepcopy(sigma_h)
                sigma_h_detail.append(float(sigma_h_copy))

    h_array_detail = np.array(h_list_detail)
    sigma_h_array_detail = np.array(sigma_h_detail)

    return h_array_detail, sigma_h_array_detail


def force_calculator(h, sigma):
    h = np.array(h)
    force = spi.simpson(sigma, h)
    centroid = spi.simpson(sigma * h, h) / force
    # note: centroid started from top
    return force, centroid


def force_calculator_x(retaining_h, h, sigma, status="active", pressure_due="soil"):
    """
    sigma and h must be a list.
    for example: h = [2 , D]
    sigma = [[0,10] , [12*D , 20*D]]
    """
    force_final = []
    arm_final = []
    for i in range(len(h)):
        force1 = h[i] * sigma[i][0]
        force2 = h[i] * (sigma[i][1] - sigma[i][0]) / 2
        force_final.append([force1, force2])

        # arm from top of soil
        if pressure_due == "soil":
            if status == "active":
                arm1 = retaining_h + h[i] / 2
                arm2 = retaining_h + 2 * h[i] / 3
                arm_final.append([arm1, arm2])
            else:
                arm1 = h[i] / 2
                arm2 = 2 * h[i] / 3
                arm_final.append([arm1, arm2])
        else:
            # for water force arm started form bottom
            arm1 = h[i] / 2
            arm2 = 1 * h[i] / 3
            arm_final.append([arm1, arm2])
    return force_final, arm_final


def control_solution(item):
    final = []
    for number in item:
        number = number.evalf(chop=True)
        try:
            final.append(float(number))
        except:
            pass
    if final:
        final_value = max(final)
    else:
        final_value = "There is no answer!"
    return final_value


def find_D(FS, force_r, arm_r, force_d, arm_d):
    D = symbols("D")

    Mr = []
    for i in range(len(force_r)):
        mr = force_r[i] * arm_r[i]
        Mr.append(mr)

    Md = []
    for i in range(len(force_d)):
        md = force_d[i] * arm_d[i]
        Md.append(md)

    equation = sum(Mr) - FS * sum(Md)
    d = solve(equation, D)
    d = control_solution(d)

    # JUST FOR REPORT.
    equation_for_report = [sum(Mr), sum(Md), equation]

    return d, equation_for_report


gama_w = {"us": 62.4, "metric": 9810}


def water_pressure(there_is_water, water_started, h, unit_system):
    gama_water = gama_w.get(unit_system)

    D = symbols("D")
    if there_is_water == "Yes":
        if water_started <= h and water_started != 0:
            water_pressure_list_active = [[0, 0], [0, (h + D - water_started) * gama_water]]
            hw_list_active = [water_started, h + D - water_started]
            water_pressure_list_passive = [[0, D * gama_water]]
            hw_list_passive = [D]

        elif water_started == 0:
            water_pressure_list_active = [[0, (h + D) * gama_water]]
            hw_list_active = [h + D]
            water_pressure_list_passive = [[0, D * gama_water]]
            hw_list_passive = [D]
        else:
            # in this situation water started is larger than main h
            water_pressure_list_active = [[0, 0], [0, D * gama_water]]
            hw_list_active = [water_started, D]
            water_pressure_list_passive = [[0, 0], [0, D * gama_water]]
            hw_list_passive = [water_started - h, D]
    else:
        water_pressure_list_active = [[0, 0]]
        hw_list_active = [0]
        water_pressure_list_passive = [[0, 0]]
        hw_list_passive = [0]

    return hw_list_active, water_pressure_list_active, hw_list_passive, water_pressure_list_passive


def water_pressure_detail(excavation_depth, water_started, unit_system):
    D = symbols("D")
    gama_water = gama_w.get(unit_system)

    excavation_depth = list(excavation_depth)
    zero_index = excavation_depth.index(water_started)

    waterPressure_edited = np.zeros_like(excavation_depth)
    pressure_index = zero_index
    for h in excavation_depth[zero_index:]:
        hw = h - water_started
        waterPressure_edited[pressure_index] = gama_water * hw
        pressure_index += 1
    # calculate force just for embedment depth
    force1 = waterPressure_edited[-1] * D
    force2 = D * D * gama_water / 2
    arm1 = D / 2
    arm2 = D / 3
    force = [[force1, force2]]
    arm = [[arm1, arm2]]

    return waterPressure_edited, force, arm


def water_pressure_detail_D(water_started, depth, unit_system):
    D = symbols("D")
    gama_water = gama_w.get(unit_system)

    depth = list(depth)
    zero_index = depth.index(water_started)

    waterPressure_edited = np.zeros_like(depth)
    pressure_index = zero_index
    for h in depth[zero_index:]:
        hw = h - water_started
        waterPressure_edited[pressure_index] = gama_water * hw
        pressure_index += 1

    return waterPressure_edited


def delete_same_values(value):
    """this function used for depth or any value that no item in that should be equal to another one.
     like depth"""
    type_value = type(value)
    if type_value == np.ndarray or type_value == np.array:
        value_list = list(value)
        convert_type_function = np.array
    else:
        value_list = list(value)
        convert_type_function = list

    for item in value_list[:-1]:
        index_item = value_list.index(item)
        if item == value_list[index_item + 1]:
            del value_list[index_item]
    return convert_type_function(value_list)
# test = anchor_pressure(25, 115, 0, 1 / 3, 4.7)
# sigma_active, sigma_passive = test.soil_pressure()
# sigma_a, h_list = test.pressure_cohesion_less_single(10)
