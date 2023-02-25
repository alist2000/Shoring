import sys
from math import cos
import copy

import sympy.core.mul
from sympy import symbols
from sympy.solvers import solve
import numpy as np
from pressure import force_calculator, force_calculator_x, find_D, edit_sigma_and_height_general


def single_anchor(spacing, FS, h1, h, trapezoidal_force, trapezoidal_force_arm, surcharge_force, surcharge_arm,
                  force_active, arm_active, force_passive,
                  arm_passive, sigma_active, sigma_passive, water_force_active, water_arm_active, water_force_passive,
                  water_arm_passive, water_started, delta_h):
    D = symbols("D")
    driving_force = []
    for i in force_active:
        for j in i:
            driving_force.append(j)
    driving_force += [trapezoidal_force] + [surcharge_force]

    resisting_force = []
    for i in force_passive:
        for j in i:
            resisting_force.append(j)

    driving_force_arm = []
    for i in arm_active:
        for j in i:
            driving_force_arm.append(j - h1)
    driving_force_arm += [trapezoidal_force_arm - h1] + [surcharge_arm - h1]

    resisting_force_arm = []
    for i in arm_passive:
        for j in i:
            resisting_force_arm.append(j + h - h1)

    delta_h_decimal = str(delta_h)[::-1].find('.')
    if delta_h_decimal == -1:
        delta_h_decimal = 0

    if water_started > h:
        d = find_D(FS, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d_0 = find_D(1, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d = round(d, delta_h_decimal)
        d_0 = round(d_0, delta_h_decimal)
        if d > water_started - h:
            # add water pressure now is necessary
            # first I should consider D from water started - h
            for item in [driving_force, resisting_force, driving_force_arm, resisting_force_arm]:
                for i in range(len(item)):
                    if type(item[i]) == sympy.core.mul.Mul or type(item[i]) == sympy.core.add.Add:
                        item[i] = item[i].subs(D, D + (water_started - h))
            # now I should add water pressure
            for i in water_force_active:
                for j in i:
                    driving_force.append(j)
            for i in water_force_passive:
                for j in i:
                    resisting_force.append(j)
            for i in water_arm_active:  # note: just last index in water pressure and arm is important.
                for j in i:
                    driving_force_arm.append(
                        water_started + D - h1 - j)  # water arm started form end. and we should change it to started form anchor.
            for i in water_arm_passive:  # note: just last index in water pressure and arm is important.
                for j in i:
                    resisting_force_arm.append(
                        water_started + D - h1 - j)  # water arm started form end. and we should change it to started form anchor.

        d = find_D(FS, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d_0 = find_D(1, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d = round(d + (water_started - h), delta_h_decimal)
        d_0 = round(d_0 + water_started - h, delta_h_decimal)

    else:
        # add water pressure
        for i in water_force_active:
            for j in i:
                driving_force.append(j)
        for i in water_force_passive:
            for j in i:
                resisting_force.append(j)
        for i in water_arm_active:
            for j in i:
                driving_force_arm.append(
                    h + D - h1 - j)  # water arm started form end. and we should change it to started form anchor.
        for i in water_arm_passive:
            for j in i:
                resisting_force_arm.append(
                    h + D - h1 - j)  # water arm started form end. and we should change it to started form anchor.
        d = find_D(FS, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d_0 = find_D(1, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d = round(d, delta_h_decimal)
        d_0 = round(d_0, delta_h_decimal)

    # replace d0 in D for all values
    for item in [sigma_active, sigma_passive, resisting_force, resisting_force_arm, driving_force,
                 driving_force_arm]:
        for i in range(len(item)):
            if type(item[i]) == sympy.core.mul.Mul or type(item[i]) == sympy.core.add.Add:
                item[i] = item[i].subs(D, d_0)
    D_array, active_pressure_array = edit_sigma_and_height_general([sigma_active], [d_0], delta_h, d_0)
    D_array, passive_pressure_array = edit_sigma_and_height_general([sigma_passive], [d_0], delta_h, d_0)

    # calculate anchor force.
    Th = abs(sum(resisting_force) - sum(driving_force)) * spacing  # anchor force --> unit: lb
    return d, d_0, Th, sigma_active, sigma_passive, D_array, active_pressure_array, passive_pressure_array
