from tkinter.messagebox import NO
import pandas as pd
import pyarrow.feather as feather
# from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import datetime
import math
import numpy as np

from front.report import surcharge_inputs, Formula, racker_input


# creating excel
def create_feather(z, value, title, excel_name):
    data = list(zip(z, value))
    df = pd.DataFrame(data, columns=["Z", title])
    df.to_feather("reports/excel/" + excel_name + ".feather")
    # df.to_csv("reports/excel/" + excel_name + ".csv")


def create_pdf_report(html_temp_file, template_vars):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(html_temp_file)
    html_filled = template.render(template_vars)
    with open('reports/template/Rep_Restrained_Filled.html', 'w') as f:
        f.write(html_filled)
    # return html_filled
    # file = open("report" + str(number) + ".html", "w")
    # file.write(html_filled)
    # file.close()
    # HTML(string=html_filled, base_url=__file__).write_pdf(pdf_name)


def report_final(input_values, Sx, Ax, M_max, V_max,
                 y_zero, k_or_EFPa, k_or_EFPp, pressures, loads, arms,
                 equations, D_0, D
                 ):
    # SITE INPUTS.
    [input_errors, project_information, number_of_project, number_of_layer_list, unit_system, anchor_number_list,
     h_list, delta_h_list,
     gama_list,
     h_list_list, cohesive_properties_list, pressure_distribution_list,
     k_formula_list, soil_properties_list, there_is_water_list, water_started_list, surcharge_type_list,
     surcharge_depth_list,
     surcharge_inputs_list, tieback_spacing_list,
     anchor_angle_list, FS_list, E_list, Fy_list, allowable_deflection_list,
     selected_design_sections_list, ph_max_list, Fb_list, timber_size_list] = input_values.values()
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

        surcharge_inputs(surcharge_type, q, l1, l2, teta, surcharge_depth, unit_system=unit_system)

        tieback_spacing = tieback_spacing_list[project]
        anchor_angle = anchor_angle_list[project]

        FS = FS_list[project]
        E = E_list[project]
        Fy = Fy_list[project]
        allowable_deflection = allowable_deflection_list[project]

        selected_design_sections = selected_design_sections_list[project]
        sections = ""
        for i in selected_design_sections:
            sections += i + ", "
        sections = sections[:-2]

        ph_max = ph_max_list[project]
        Fb = Fb_list[project]
        timber_size = timber_size_list[project]
        c, gama_s = cohesive_properties[0], cohesive_properties[1]

        if k_formula == "User Defined":
            ka, kp, sigma_a_user, ka_surcharge, h_list_pressure = soil_properties
            soil_prop = [k_or_EFPa, k_or_EFPp, ka_surcharge, c]
            Formula(k_formula, soil_prop, h, unit_system)

        elif k_formula == "Rankine":
            phi, beta_active, beta_passive = soil_properties
            delta = 0
            soil_prop = [k_or_EFPa, k_or_EFPp, gama, phi, beta_active, beta_passive, delta, c]
            Formula(k_formula, soil_prop, h, unit_system)

            # # phi and beta are lists. every index is for a separate soil layer.
            # # here we just have one soil layer. (for now) this part can be developed.
            # ka = rankine(phi[0], beta_active[0], "active")
            # kp = rankine(phi[0], beta_passive[0], "passive")
            # ka_surcharge = ka

        else:  # coulomb
            phi, beta_active, beta_passive, delta, omega = soil_properties
            soil_prop = [k_or_EFPa, k_or_EFPp, gama, phi, beta_active, beta_passive, delta, c]
            Formula(k_formula, soil_prop, h, unit_system)

            # # phi and beta and etc are lists. every index is for a separate soil layer.
            # # here we just have one soil layer. (for now) this part can be developed.
            # ka = coulomb(phi[0], beta_active[0], delta[0], omega[0], "active")
            # kp = coulomb(phi[0], beta_passive[0], delta[0], omega[0], "passive")
            # ka_surcharge = ka

        [product_id, user_id, title, jobNo, designer, checker, company, client, date, comment,
         other] = project_information

        if comment == None:
            comment = "-"
        if date == None:
            date = datetime.datetime.today().strftime('%Y-%m-%d')

        # UNITS
        if unit_system == "us":
            length_unit = "ft"
            force_unit = "lb"
            k_force_unit = "kips"
            moment_unit = "lb-ft"
            k_moment_unit = "kip-ft"
            pressure_unit = "ksi"
            deflection_unit = "in"
            density_unit = "pcf"
            A_unit = "in<sup>2</sup>"
            s_unit = "in<sup>3</sup>"
        else:
            length_unit = "m"
            force_unit = "N"
            k_force_unit = "KN"
            moment_unit = "N-m"
            k_moment_unit = "KN-m"
            pressure_unit = "MPa"
            deflection_unit = "mm"
            density_unit = "N/m<sup>2</sup>"
            A_unit = "mm<sup>2</sup>"
            s_unit = "mm<sup>3</sup>"

        # PRESSURES
        # better appearance
        [soil_top_active, soil_end_active, soil_end_passive, water_pre_e_a, water_pre_e_p] = edit_equation(*pressures)
        # pressure picture
        if pressure_distribution == "Trapezoidal" and c == 0:
            distribution_pic = "template/picture_pressure1.html"
        elif pressure_distribution == "Trapezoidal" and c != 0:
            distribution_pic = "template/picture_pressure2.html"
        else:
            distribution_pic = "template/picture_pressure3.html"

        # LOADS
        # better appearance
        [trapezoidal_force, force_soil1, force_soil2, surcharge_force, water_active_force, soil_passive_force,
         water_passive_force] = edit_equation(*loads)
        [trapezoidal_arm, arm_soil1, arm_soil2, surcharge_arm, water_active_arm, soil_passive_arm,
         water_passive_arm] = edit_equation(*arms)
        # force & arm picture
        if pressure_distribution == "Trapezoidal" and c == 0:
            force_pic = "template/picture_force1.html"
        elif pressure_distribution == "Trapezoidal" and c != 0:
            force_pic = "template/picture_force2.html"
        else:
            force_pic = "template/picture_force3.html"

        # EQUATIONS
        Mr = equations[0]
        Md = equations[1]
        d_equation = equations[2]
        [Mr, Md, d_equation] = edit_equation(Mr, Md, d_equation)

        # RACKER
        racker_input(unit_system, anchor_number, h_list_first)

        # WATER
        if there_is_water == "No":
            water_started = "-"

        # # LAGGING
        # [d_concrete, lc, R_lagging, M_max_lagging, Sx_req_lagging, Sx_sup_lagging, lagging_status] = lagging_prop

        # FILLER DICT
        report_values = {
            # GENERAL INFORMATION
            "project_title": title, "designer": designer, "job_title": jobNo, "checker": checker,
            "company": company, "analysis_date": date, "comments": comment, "unit_system": unit_system,

            # GENERAL PROPERTIES
            "E": E, "FS": FS, "Fb": Fb, "Fy": Fy,
            "tieback_spacing": tieback_spacing, "allowable_deflection": allowable_deflection,
            "retaining_height ": h, "Sections": sections,

            # WATER PROPERTIES
            "there_is_water": there_is_water, "water_started": water_started,

            # LAGGING INPUTS AND OUTPUTS
            "Ph_max": ph_max, "timber_size": timber_size,

            # IMPORTANT VALUES FROM ANALYSIS
            "D": math.ceil(D),
            "Sx_required": round(Sx, 1), "Ax_required": math.ceil(Ax), "M_max": round(M_max / 1000, 1),
            "shear_max": round(V_max / 1000, 1),
            "y_zero_shear": y_zero, "d0": round(D_0, 2), "d_equation": d_equation, "Md": Md, "Mr": Mr,

            # PRESSURES
            "sp_s_a": soil_top_active, "sp_e_a": soil_end_active, "sp_e_p": soil_end_passive,
            "wp_e_a": water_pre_e_a, "wp_e_p": water_pre_e_p, "load_distribution_pic": distribution_pic,

            # LOADS & ARMS
            "dr1": round(trapezoidal_force, 2), "dr2": force_soil1, "dr3": force_soil2,
            "dr4": round(surcharge_force, 2),
            "dr5": water_active_force,
            "rs1": soil_passive_force, "rs2": water_passive_force,
            "arm_dr1": round(trapezoidal_arm, 2), "arm_dr2": arm_soil1, "arm_dr3": arm_soil2,
            "arm_dr4": round(surcharge_arm, 2),
            "arm_dr5": water_active_arm,
            "arm_rs1": soil_passive_arm, "arm_rs2": water_passive_arm,
            "force_pic": force_pic,

            # STATUSES --> IT'S ALWAYS Pass BECAUSE WE CHOOSE SECTION TO Pass IN MOMENT SHEAR AND DEFLECTION.
            "moment_status": "Pass",
            "shear_status": "Pass",

            # UNITS
            "length_unit": length_unit, "density_unit": density_unit, "force_unit": force_unit,
            "k_force_unit": k_force_unit,
            "moment_unit": moment_unit, "k_moment_unit": k_moment_unit,
            "deflection_unit": deflection_unit, "Ax_unit": A_unit, "Sx_unit": s_unit, "pressure_unit": pressure_unit,
            "ull": " &deg;"

        }
        return report_values


def edit_equation(*equations):
    return_list = []
    for equation in equations:
        if type(equation) not in [float, int, str, np.float64, np.int64]:
            equation = round_number_equation(equation)
            equation = str(equation)
            equation = equation.replace("**", "<sup>")
            equation = equation.replace("*", "×")
            equation = edit_power(equation)
            return_list.append(equation)
        else:
            return_list.append(equation)
    return return_list


import sympy


def round_number_equation(equation):
    new_args = ()
    for i in equation.args:
        if type(i) == sympy.core.Float:
            i = round(i, 2)
        new_args += (i,)

    edited_equation = equation.func(*new_args)
    return edited_equation


def edit_power(equation):
    for i in range(len(equation)):
        if equation[i] == ">":
            equation = equation[: i + 2] + "</sup>" + equation[i + 2:]
    return equation
