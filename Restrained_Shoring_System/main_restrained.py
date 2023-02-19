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
from Single_anchor import single_anchor
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


def main_restrained(inputs):
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

            h_array_detail, sigma_a_array_detail = edit_sigma_and_height_general(
                [[0, sigma_a], [sigma_a, sigma_a], [sigma_a, 0]], h_list, delta_h, h)

        else:
            h1 = h_list_first[0]
            sigma_a, h_list = pressure.pressure_cohesive(gama_s, h1)

            h_array_detail, sigma_a_array_detail = edit_sigma_and_height_general(
                [[0, sigma_a], [sigma_a, sigma_a]], h_list, delta_h, h)

        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        for i in range(len(h_list)):
            h_list[i] = round(h_list[i], delta_h_decimal)

        main_surcharge = surcharge(unit_system, h, delta_h)
        surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge_list = result_surcharge(
            main_surcharge,
            surcharge_type, q, l1, l2,
            teta, ka)

        # h_array_detail_1, sigma_a_array_detail_1 = edit_sigma_and_height(sigma_a, h_list, delta_h)

        trapezoidal_force, trapezoidal_force_arm = force_calculator(h_array_detail, sigma_a_array_detail)
        if anchor_number != 1:
            d, d_0, Th, sigma_active, sigma_passive, D_array, active_pressure_array, passive_pressure_array = multi_anchor(
                tieback_spacing, FS, h_list_first,
                h_array_detail, sigma_a_array_detail,
                surcharge_pressure, force_active,
                arm_active, force_passive, arm_passive,
                sigma_active, sigma_passive, delta_h)

            T_list = []
            for T in Th:
                T_list.append(T / cos(
                    anchor_angle))  # ASK: this angle should be got for any anchor. or we get just one value for all?


        else:
            d, d_0, Th, sigma_active, sigma_passive, D_array, active_pressure_array, passive_pressure_array = single_anchor(
                tieback_spacing, FS, h1, h, trapezoidal_force, trapezoidal_force_arm, surcharge_force, surcharge_arm,
                force_active, arm_active, force_passive,
                arm_passive, sigma_active, sigma_passive,
                delta_h)
            T = Th / cos(anchor_angle)

        sigma_a_array_detail_copy = copy.deepcopy(sigma_a_array_detail)
        if type(surcharge_pressure) == list or type(surcharge_pressure) == np.ndarray:
            for i in range(len(sigma_a_array_detail_copy)):
                sigma_a_array_detail_copy[i] += surcharge_pressure[i]
        else:
            surcharge_pressure = copy.deepcopy(sigma_a_array_detail)
            for i in range(len(surcharge_pressure)):
                surcharge_pressure[i] = 0
        # load diagram for one anchor.
        plotter_load(h_array_detail, sigma_a_array_detail, D_array, active_pressure_array, passive_pressure_array,
                     surcharge_pressure,
                     Th,
                     h_list_first,
                     "q", "Z", "load_unit", "length_unit")

        # load result
        final_pressure_under = active_pressure_array - passive_pressure_array

        final_pressure = np.array(list(sigma_a_array_detail_copy) + list(final_pressure_under))
        depth = np.array(list(h_array_detail) + list(D_array + h_array_detail[-1]))
        for i in range(len(depth)):
            depth[i] = round(depth[i], delta_h_decimal)
        # plot2 = plotter_load_result(depth, final_pressure, "", "", "", "")

        # shear and moment values and diagrams
        if anchor_number == 1:
            analysis_instance = analysis(Th / tieback_spacing, h1, list(depth), list(final_pressure), delta_h,
                                         unit_system)
            shear_plot, shear_values = analysis_instance.shear()
            moment_plot, moment_values = analysis_instance.moment(shear_values)
            deflections = analysis_instance.deflection_single3(moment_values, d_0, h1)
        else:
            analysis_instance = analysis(Th / tieback_spacing, h_list_first, list(depth), list(final_pressure), delta_h,
                                         unit_system)
            shear_plot, shear_values = analysis_instance.shear_multi()
            moment_plot, moment_values = analysis_instance.moment(shear_values)
            deflections = analysis_instance.deflection_multi(moment_values, d_0, h_list_first)
    return sigma_active, sigma_passive, sigma_a, surcharge_pressure, surcharge_force, surcharge_arm, trapezoidal_force, trapezoidal_force_arm, d, d_0, T


outputs = main_restrained(input_values)
