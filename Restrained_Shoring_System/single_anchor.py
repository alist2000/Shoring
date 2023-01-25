import copy
import random
import sys
from sympy import symbols
from sympy.solvers import solve
import numpy as np

from inputs import input_values
from pressure import anchor_pressure, edit_sigma_and_height, force_calculator

sys.path.append(r"D:/git/Shoring/Lateral-pressure-")
sys.path.append(r"D:/git/ShoringUnrestrained_Shoring_System")

from Surcharge.result import result_surcharge
from Unrestrained_Shoring_System.soldier_pile.surchargeLoad import surcharge
from Unrestrained_Shoring_System.soldier_pile.shear_moment_diagram import plotter_load


def single_anchor(inputs):
    [number_of_project, number_of_layer_list, unit_system, anchor_number_list, h_list, delta_h_list, gama_list,
     h_list_list, cohesive_properties_list,
     k_formula_list, soil_properties_list, surcharge_type_list, surcharge_inputs_list, FS_list] = inputs.values()
    for project in range(number_of_project):
        number_of_layer = number_of_layer_list[project]
        anchor_number = anchor_number_list[project]
        h = h_list[project]
        delta_h = delta_h_list[project]
        gama = gama_list[project]
        h_list = h_list_list[project]
        cohesive_properties = cohesive_properties_list[project]
        k_formula = k_formula_list[project]
        soil_properties = soil_properties_list[project]
        surcharge_type = surcharge_type_list[project]
        [q, l1, l2, teta] = surcharge_inputs_list[project]

        FS = FS_list[project]

        if k_formula == "User Defined":
            ka, kp = soil_properties[0], soil_properties[1]
        else:
            pass
        c, gama_s = cohesive_properties[0], cohesive_properties[1]

        pressure = anchor_pressure(h, gama, c, ka, kp)
        sigma_active, sigma_passive = pressure.soil_pressure()
        if c == 0:
            if anchor_number == 1:
                h1 = h_list[0]
                sigma_a, h_list = pressure.pressure_cohesion_less_single(h1)

        main_surcharge = surcharge(unit_system, h, delta_h)
        surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge_list = result_surcharge(
            main_surcharge,
            surcharge_type, q, l1, l2,
            teta, ka)

        h_array_detail, sigma_a_array_detail = edit_sigma_and_height(sigma_a, h_list, delta_h)

        trapezoidal_force, trapezoidal_force_arm = force_calculator(h_array_detail, sigma_a_array_detail)

        plotter_load(h_array_detail, sigma_a_array_detail, "", "", "", "")

    return sigma_active, sigma_passive, sigma_a, surcharge_pressure, surcharge_force, surcharge_arm, trapezoidal_force, trapezoidal_force_arm


outputs = single_anchor(input_values)