import copy
import random
import sys
from math import cos

import sympy.core.mul
from sympy import symbols
from sympy.solvers import solve
import numpy as np

from inputs import input_values
from pressure import anchor_pressure, edit_sigma_and_height_general, force_calculator, \
    force_calculator_x, find_D
from multi_anchor import multi_anchor
from plot import plotter_load, plotter_load_result
from analysis import analysis

sys.path.append(r"D:/git/Shoring/Lateral-pressure-")
sys.path.append(r"D:/git/Shoring/Unrestrained_Shoring_System")

sys.path.append(r"F:/Cvision/Lateral-pressure-")
sys.path.append(r"F:/Cvision/Unrestrained_Shoring_System")

from Surcharge.result import result_surcharge
from soldier_pile.surchargeLoad import surcharge
from Passive_Active.active_passive import rankine, coulomb


# from Unrestrained_Shoring_System.soldier_pile.shear_moment_diagram import plotter_load


def single_anchor(inputs):
    [number_of_project, number_of_layer_list, unit_system, anchor_number_list, h_list, delta_h_list, gama_list,
     h_list_list, cohesive_properties_list,
     k_formula_list, soil_properties_list, surcharge_type_list, surcharge_inputs_list, tieback_spacing_list,
     FS_list, anchor_angle_list] = inputs.values()
    for project in range(number_of_project):
        number_of_layer = number_of_layer_list[project]
        anchor_number = anchor_number_list[project]
        h = h_list[project]
        delta_h = delta_h_list[project]
        gama = gama_list[project]
        h_list_first = h_list_list[project]
        cohesive_properties = cohesive_properties_list[project]
        k_formula = k_formula_list[project]
        soil_properties = soil_properties_list[project]
        surcharge_type = surcharge_type_list[project]
        [q, l1, l2, teta] = surcharge_inputs_list[project]

        tieback_spacing = tieback_spacing_list[project]
        FS = FS_list[project]
        anchor_angle = anchor_angle_list[project]

        if k_formula == "User Defined":
            ka, kp = soil_properties[0], soil_properties[1]
        elif k_formula == "Rankine":
            phi, beta = soil_properties
            # phi and beta are lists. every index is for a separate soil layer.
            # here we just have one soil layer. (for now) this part can be developed.
            ka = rankine(phi[0], beta[0], "active")
            kp = rankine(phi[0], beta[0], "passive")

        else:  # coulomb
            phi, beta, delta, omega = soil_properties
            # phi and beta and etc are lists. every index is for a separate soil layer.
            # here we just have one soil layer. (for now) this part can be developed.
            ka = coulomb(phi[0], beta[0], delta[0], omega[0], "active")
            kp = coulomb(phi[0], beta[0], delta[0], omega[0], "passive")

        c, gama_s = cohesive_properties[0], cohesive_properties[1]

        pressure = anchor_pressure(h, gama, c, ka, kp)
        sigma_active, sigma_passive = pressure.soil_pressure()
        D = symbols("D")
        force_active, arm_active = force_calculator_x(h, [D], [sigma_active])
        force_passive, arm_passive = force_calculator_x(h, [D], [sigma_passive], "passive")

        if c == 0:
            if anchor_number == 1:
                h1 = h_list_first[0]
                sigma_a, h_list = pressure.pressure_cohesion_less_single(h1)
            else:
                h1 = h_list_first[0]
                hn = h_list_first[-1]
                sigma_a, h_list = pressure.pressure_cohesion_less_multi(anchor_number, h1, hn)

        else:
            # this part should be developed.
            pass

        main_surcharge = surcharge(unit_system, h, delta_h)
        surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge_list = result_surcharge(
            main_surcharge,
            surcharge_type, q, l1, l2,
            teta, ka)

        # h_array_detail_1, sigma_a_array_detail_1 = edit_sigma_and_height(sigma_a, h_list, delta_h)
        h_array_detail, sigma_a_array_detail = edit_sigma_and_height_general(
            [[0, sigma_a], [sigma_a, sigma_a], [sigma_a, 0]], h_list, delta_h, h)

        trapezoidal_force, trapezoidal_force_arm = force_calculator(h_array_detail, sigma_a_array_detail)
        if anchor_number != 1:
            output = multi_anchor(tieback_spacing, FS, h_list_first, h_array_detail, sigma_a_array_detail,
                                  surcharge_pressure, force_active,
                                  arm_active, force_passive, arm_passive)
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

        d = find_D(FS, resisting_force, resisting_force_arm, driving_force, driving_force_arm)
        d_0 = find_D(1, resisting_force, resisting_force_arm, driving_force, driving_force_arm)

        # replace d0 in D for all values
        for item in [sigma_active, sigma_passive, resisting_force, resisting_force_arm, driving_force,
                     driving_force_arm]:
            for i in range(len(item)):
                if type(item[i]) == sympy.core.mul.Mul or type(item[i]) == sympy.core.add.Add:
                    item[i] = item[i].subs(D, d_0)

        D_array, active_pressure_array = edit_sigma_and_height_general([sigma_active], [d_0], delta_h)
        D_array, passive_pressure_array = edit_sigma_and_height_general([sigma_passive], [d_0], delta_h)

        # calculate anchor force.
        Th = abs(sum(resisting_force) - sum(driving_force)) * tieback_spacing  # anchor force --> unit: lb
        T = Th / cos(anchor_angle)

        # load diagram
        plotter_load(h_array_detail, sigma_a_array_detail, D_array, active_pressure_array, passive_pressure_array, Th,
                     h1,
                     "q", "Z", "load_unit", "length_unit")

        # load result
        final_pressure_under = active_pressure_array - passive_pressure_array
        final_pressure = np.array(list(sigma_a_array_detail) + list(final_pressure_under))
        depth = np.array(list(h_array_detail) + list(D_array + h_array_detail[-1]))
        # plot2 = plotter_load_result(depth, final_pressure, "", "", "", "")

        # shear and moment values and diagrams
        analysis_instance = analysis(Th / tieback_spacing, h1, list(depth), list(final_pressure), delta_h, unit_system)
        shear_plot, shear_values = analysis_instance.shear()
        moment_plot, moment_values = analysis_instance.moment(shear_values)
    return sigma_active, sigma_passive, sigma_a, surcharge_pressure, surcharge_force, surcharge_arm, trapezoidal_force, trapezoidal_force_arm, d, d_0, T


outputs = single_anchor(input_values)
