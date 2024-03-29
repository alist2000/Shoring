import copy
import random
import sys
from math import cos
import math
import shutil

import sympy.core.mul
from sympy import symbols
from sympy.solvers import solve
import numpy as np

from inputs import input_single
from site_input import site_input
from pressure import anchor_pressure, edit_sigma_and_height_general, force_calculator, \
    force_calculator_x, find_D, water_pressure, water_pressure_detail_D, delete_same_values
from multi_anchor import multi_anchor
from Single_anchor import single_anchor
from plot import plotter_load, plotter_load_result
from analysis_openAI import analysis, DCR_calculator, control_index_for_plot
from design import design, subscription, min_weight
from report import create_feather, report_final, create_pdf_report
from Output import output_single_solved, output_single_no_solution

sys.path.append(r"D:/git/Shoring/Lateral-pressure-")
sys.path.append(r"D:/git/Shoring/Unrestrained_Shoring_System")
sys.path.append(r"D:/git/Shoring/Restrained_Shoring_System")

sys.path.append(r"F:/Cvision/Lateral-pressure-")
sys.path.append(r"F:/Cvision/Unrestrained_Shoring_System")

from Surcharge.result import result_surcharge
from soldier_pile.surchargeLoad import surcharge
from Passive_Active.active_passive import rankine, coulomb
from front.report import load_distribution, raker_force, section_deflection, deflection_output, DCRs, lagging_output


# from Unrestrained_Shoring_System.soldier_pile.shear_moment_diagram import plotter_load


def main_restrained(inputs):
    Inputs = input_single(inputs)
    project_error = []
    [input_errors, project_information, number_of_project, number_of_layer_list, unit_system, anchor_number_list,
     h_list, delta_h_list,
     gama_list,
     h_list_list, cohesive_properties_list, pressure_distribution_list,
     k_formula_list, soil_properties_list, there_is_water_list, water_started_list, surcharge_type_list,
     surcharge_depth_list,
     surcharge_inputs_list, tieback_spacing_list,
     anchor_angle_list, FS_list, E_list, Fy_list, allowable_deflection_list,
     selected_design_sections_list, ph_max_list, Fb_list, timber_size_list] = Inputs.values()
    for project in range(number_of_project):
        number_of_layer = number_of_layer_list[project]
        anchor_number = anchor_number_list[project]
        h = h_list[project]
        delta_h = delta_h_list[project]
        gama = gama_list[project]
        h_list_first = h_list_list[project]
        cohesive_properties = cohesive_properties_list[project]
        pressure_distribution = pressure_distribution_list[project]
        k_formula = k_formula_list[project]
        soil_properties = soil_properties_list[project]
        there_is_water = there_is_water_list[project]
        water_started = water_started_list[project]
        surcharge_type = surcharge_type_list[project]
        surcharge_depth = surcharge_depth_list[project]
        [q, l1, l2, teta] = surcharge_inputs_list[project]

        tieback_spacing = tieback_spacing_list[project]
        anchor_angle = anchor_angle_list[project]

        FS = FS_list[project]
        E = E_list[project]
        Fy = Fy_list[project]
        allowable_deflection = allowable_deflection_list[project]

        selected_design_sections = selected_design_sections_list[project]

        ph_max = ph_max_list[project]
        Fb = Fb_list[project]
        timber_size = timber_size_list[project]

        if k_formula == "User Defined":
            ka, kp, sigma_a_user, ka_surcharge, h_list_pressure = soil_properties
        elif k_formula == "Rankine":
            phi, beta_active, beta_passive = soil_properties
            # phi and beta are lists. every index is for a separate soil layer.
            # here we just have one soil layer. (for now) this part can be developed.
            ka = rankine(phi[0], beta_active[0], "active")
            kp = rankine(phi[0], beta_passive[0], "passive")
            ka_surcharge = ka

        else:  # coulomb
            phi, beta_active, beta_passive, delta, omega = soil_properties
            # phi and beta and etc are lists. every index is for a separate soil layer.
            # here we just have one soil layer. (for now) this part can be developed.
            ka = coulomb(phi[0], beta_active[0], delta[0], omega[0], "active")
            kp = coulomb(phi[0], beta_passive[0], delta[0], omega[0], "passive")
            ka_surcharge = ka

        c, gama_s = cohesive_properties[0], cohesive_properties[1]

        pressure = anchor_pressure(h, gama, c, ka, kp, pressure_distribution)
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
            if pressure_distribution == "Triangle":
                sigma_a = gama * ka * h
            if k_formula == "User Defined":
                sigma_a = sigma_a_user
                if h_list_pressure[0] != "default":
                    h_list = h_list_pressure

            h_array_detail, sigma_a_array_detail = edit_sigma_and_height_general(
                [[0, sigma_a], [sigma_a, sigma_a], [sigma_a, 0]], h_list, delta_h, h)

        else:
            h1 = h_list_first[0]
            sigma_a, h_list = pressure.pressure_cohesive(gama_s, h1)

            if pressure_distribution == "Triangle":
                sigma_a = gama * ka * h
                ht1 = ht2 = 0, 0
            if k_formula == "User Defined":
                sigma_a = sigma_a_user
                if h_list_pressure[0] != "default":
                    h_list = h_list_pressure
                    h_array_detail, sigma_a_array_detail = edit_sigma_and_height_general(
                        [[0, sigma_a], [sigma_a, sigma_a], [sigma_a, 0]], h_list, delta_h, h)
                else:
                    h_array_detail, sigma_a_array_detail = edit_sigma_and_height_general(
                        [[0, sigma_a], [sigma_a, sigma_a]], h_list, delta_h, h)

        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        for i in range(len(h_list)):
            h_list[i] = round(h_list[i], delta_h_decimal)

        # surcharge
        main_surcharge = surcharge(unit_system, surcharge_depth, delta_h)
        surcharge_force, surcharge_arm, surcharge_pressure, error_surcharge_list = result_surcharge(
            main_surcharge,
            surcharge_type, q, l1, l2,
            teta, ka_surcharge)

        h_array_detail, sigma_a_array_detail = control_index_for_plot(h_array_detail, sigma_a_array_detail)
        trapezoidal_force, trapezoidal_force_arm = force_calculator(h_array_detail, sigma_a_array_detail)

        # water
        hw_list_active, water_pressure_list_active, hw_list_passive, water_pressure_list_passive = water_pressure(
            there_is_water, water_started, h, unit_system)
        water_force_active, water_arm_active = force_calculator_x(h, hw_list_active, water_pressure_list_active,
                                                                  "active", "water")
        water_force_passive, water_arm_passive = force_calculator_x(h, hw_list_passive, water_pressure_list_passive,
                                                                    "passive", "water")

        # FOR REPORT
        pressure_list_report = [sigma_active[0], sigma_active[1], sigma_passive[1], water_pressure_list_active[0][1],
                                water_pressure_list_passive[0][1]]
        force_list_report = [trapezoidal_force, force_active[0][0], force_active[0][1], surcharge_force,
                             water_force_active[0][1], force_passive[0][1], water_force_passive[0][1]]
        arm_list_report1 = list(
            map(lambda x: 0 if (x == 0) else x - h_list_first[0],
                [trapezoidal_force_arm, arm_active[0][0], arm_active[0][1],
                 surcharge_arm, water_arm_active[0][1]
                 ]))
        arm_list_report2 = list(
            map(lambda x: 0 if (x == 0) else x - h_list_first[0] + h,
                [arm_passive[0][1], water_arm_passive[0][1]
                 ]))
        arm_list_report = arm_list_report1 + arm_list_report2

        if anchor_number != 1:
            d, d_0, Th, sigma_active, sigma_passive, D_array, active_pressure_array, passive_pressure_array, equation_for_report = multi_anchor(
                tieback_spacing, FS, h_list_first,
                h_array_detail, sigma_a_array_detail,
                surcharge_pressure, force_active,
                arm_active, force_passive, arm_passive,
                sigma_active, sigma_passive, water_started, water_force_active, water_arm_active, water_force_passive,
                water_arm_passive,
                delta_h, unit_system)

            T_list = []
            for T in Th:
                T_list.append(T / cos(
                    anchor_angle))  # ASK: this angle should be got for any anchor. or we get just one value for all?
            raker_force(unit_system, T_list)

        else:
            d, d_0, Th, sigma_active, sigma_passive, D_array, active_pressure_array, passive_pressure_array, equation_for_report = single_anchor(
                tieback_spacing, FS, h1, h, trapezoidal_force, trapezoidal_force_arm, surcharge_force, surcharge_arm,
                force_active, arm_active, force_passive,
                arm_passive, sigma_active, sigma_passive, water_force_active, water_arm_active, water_force_passive,
                water_arm_passive, water_started,
                delta_h)
            T = Th / cos(anchor_angle)
            raker_force(unit_system, [T])

        sigma_a_array_detail_copy = copy.deepcopy(sigma_a_array_detail)
        try:  # if there is surcharge pressure
            if len(list(sigma_a_array_detail_copy)) != len(list(surcharge_pressure)):
                for i in range(len(sigma_a_array_detail_copy) - len(surcharge_pressure)):
                    surcharge_pressure = list(surcharge_pressure)
                    surcharge_pressure.append(0)
                surcharge_pressure = np.array(surcharge_pressure)
        except:
            pass
        if type(surcharge_pressure) == list or type(surcharge_pressure) == np.ndarray:
            for i in range(len(sigma_a_array_detail_copy)):
                if list(surcharge_pressure) == [0]:
                    surcharge_pressure = np.zeros_like(sigma_a_array_detail_copy)

                sigma_a_array_detail_copy[i] += surcharge_pressure[i]
        else:
            surcharge_pressure = copy.deepcopy(sigma_a_array_detail)
            for i in range(len(surcharge_pressure)):
                surcharge_pressure[i] = 0
        # load diagram for one anchor.

        # load result
        depth = np.array(list(h_array_detail) + list(D_array + h_array_detail[-1]))
        for i in range(len(depth)):
            depth[i] = round(depth[i], delta_h_decimal)

        final_pressure_under = active_pressure_array - passive_pressure_array

        final_pressure = np.array(list(sigma_a_array_detail_copy) + list(final_pressure_under))

        if water_started <= depth[-1]:
            water_pressure_active_final = water_pressure_detail_D(water_started, depth, unit_system)
            water_pressure_passive_final = water_pressure_detail_D(max(h, water_started), depth, unit_system)


        else:
            water_pressure_active_final = water_pressure_detail_D(depth[-1], depth, unit_system)
            water_pressure_passive_final = water_pressure_detail_D(depth[-1], depth, unit_system)
        # load diagram for one anchor.
        load_diagram = plotter_load(h_array_detail, sigma_a_array_detail, D_array, active_pressure_array,
                                    passive_pressure_array,
                                    surcharge_pressure,
                                    Th,
                                    h_list_first,
                                    water_pressure_active_final,
                                    water_pressure_passive_final,
                                    depth,
                                    "q", "Z", unit_system)

        # all pressure should have same shaped.
        final_pressure, water_pressure_active_final = control_index_for_plot(final_pressure,
                                                                             water_pressure_active_final)
        water_pressure_active_final, water_pressure_passive_final = control_index_for_plot(water_pressure_active_final,
                                                                                           water_pressure_passive_final)
        water_pressure_active_final = np.array(water_pressure_active_final)
        water_pressure_passive_final = np.array(water_pressure_passive_final)

        final_pressure = final_pressure + water_pressure_active_final - water_pressure_passive_final
        create_feather(depth, final_pressure, "Load", "load_project" + str(project + 1))

        # plot2 = plotter_load_result(depth, final_pressure, "", "", "", "")

        # shear and moment values and diagrams
        if anchor_number == 1:
            analysis_instance = analysis(Th, h1, list(depth), list(final_pressure * tieback_spacing), delta_h,
                                         unit_system, project + 1)
            # analysis_instance = analysis(Th / tieback_spacing, h1, list(depth), list(final_pressure), delta_h,
            #                              unit_system, project + 1)
            shear_diagram, shear_values, V_max, Y_zero_load = analysis_instance.shear()
            moment_diagram, moment_values, M_max, Y_zero_shear = analysis_instance.moment(shear_values)
            deflection_values, z_max, max_deflection = analysis_instance.deflection_single3(
                moment_values, d_0, h1)
        else:
            analysis_instance = analysis(Th, h_list_first, list(depth), list(final_pressure * tieback_spacing), delta_h,
                                         unit_system, project + 1)
            shear_diagram, shear_values, V_max, Y_zero_load = analysis_instance.shear_multi()
            moment_diagram, moment_values, M_max, Y_zero_shear = analysis_instance.moment(shear_values)
            deflection_values, z_max, max_deflection = analysis_instance.deflection_multi(
                moment_values, d_0, h_list_first)

        final_sections = []
        final_sections_names = []
        Ix = []
        Sx = []
        A = []
        for section in selected_design_sections:
            section = section[1:]
            section_design = design(section, E, Fy, unit_system)
            moment_ok, S_required = section_design.moment_design(M_max)
            shear_ok, A_required = section_design.shear_design(V_max)
            deflection_ok = section_design.deflection_design(allowable_deflection, max_deflection)

            qualified_sections, number_of_section = subscription(moment_ok, shear_ok, deflection_ok)
            if number_of_section != 0:
                best_section = min_weight(qualified_sections)
                final_sections.append(best_section)
                section_name = best_section["section"]
                final_sections_names.append(section_name)
                ix = best_section["Ix"]
                Ix.append(ix)
                sx = best_section["Sx"]
                Sx.append(sx)
                ax = best_section["area"]
                A.append(ax)

        if final_sections:
            section_error = "No Error!"
            final_deflections, max_deflections, deflection_plots, DCR_lagging, \
            status_lagging, d_concrete_list, h_list_section, bf_list, tw_list, tf_list, lc_list, R_list, M_max_lagging, s_req_list, s_sup_list = analysis_instance.final_deflection_and_lagging(
                deflection_values,
                final_sections, E, tieback_spacing, ph_max, timber_size, Fb,
                unit_system)
            DCR_deflection, DCR_shear, DCR_moment = DCR_calculator(max_deflections, allowable_deflection, Sx,
                                                                   S_required, A, A_required)
            report_values = report_final(Inputs, S_required, A_required, M_max, V_max, Y_zero_shear, ka, kp,
                                         pressure_list_report,
                                         force_list_report, arm_list_report, equation_for_report, d_0, d,
                                         )
            for i in range(len(final_sections)):
                DCRs(DCR_moment[i], DCR_shear[i], DCR_deflection[i], DCR_lagging[i], status_lagging[i], i + 1)
                section_deflection(unit_system, Fy, final_sections_names[i], A[i], Sx[i], Ix[i], V_max, M_max,
                                   max_deflections[i], allowable_deflection, i + 1)
                deflection_output(max_deflections[i], unit_system, i + 1)
                lagging_output(unit_system, tieback_spacing, d_concrete_list[i], lc_list[i], ph_max, R_list[i],
                               M_max_lagging[i], s_req_list[i], timber_size, s_sup_list[i], status_lagging[i], i + 1)

                report_values["DCR_file"] = f"template/DCRs{i + 1}.html"
                report_values["def_max_file"] = f"template/deflection_max{i + 1}.html"
                report_values["section_file"] = f"template/section_deflection{i + 1}.html"
                report_values["lagging_file"] = f"template/lagging_output{i + 1}.html"

                create_pdf_report("reports/template/Rep_Restrained_Shoring.html", report_values)

                shutil.copyfile("reports/template/Rep_Restrained_Filled.html",
                                f"reports/Rep_Restrained_Shoring{i + 1}.html")

        else:
            section_error = ["No Section is Matched!"]
            project_error.append(section_error)

            final_deflections, max_deflections, deflection_plots = "", "", ""

        if number_of_project == 1 and section_error == "No Error!":  # errors can be develop
            # create report
            if len(h_list) == 2:
                ht2 = 0
                ht1 = h_list[0]
            else:
                ht2 = h_list[-1]
                ht1 = h_list[0]
            load_distribution(unit_system, sigma_a, h, ht1, ht2)

            # outputs
            general_plot = [load_diagram, shear_diagram, moment_diagram]
            general_values = [math.ceil(d), round(V_max / 1000, 2), round(M_max / 1000, 2), Y_zero_shear, A_required,
                              S_required]
            general_output = {"plot": general_plot, "value": general_values}
            specific_plot = deflection_plots
            specific_values = [final_sections_names, max_deflections, DCR_moment, DCR_shear, DCR_deflection,
                               timber_size,
                               status_lagging, d_concrete_list, h_list_section, bf_list, tw_list, tf_list]
            specific_output = {"plot": specific_plot, "value": specific_values}
            output_single = output_single_solved(unit_system, general_output, specific_output)
            return output_single
        elif number_of_project == 1 and section_error != "No Error!":
            output_single = output_single_no_solution(project_error)
            return output_single

    return sigma_active, sigma_passive, sigma_a, surcharge_pressure, surcharge_force, surcharge_arm, trapezoidal_force, trapezoidal_force_arm, d, d_0, T


outputs = main_restrained(site_input)
