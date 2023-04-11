import pandas as pd
import pyarrow.feather as feather
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from front.report import surcharge_inputs, Formula


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
    HTML(string=html_filled, base_url=__file__)
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
        [q, l1, l2, teta] = surcharge_inputs_list[project]

        surcharge_inputs(surcharge_type, q, l1, l2, teta, retaining_height=h, unit_system=unit_system)

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

        # UNITS
        if unit_system == "us":
            length_unit = "ft"
            force_unit = "lb"
            moment_unit = "bl-ft"
            pressure_unit = "ksi"
            deflection_unit = "in"
            density_unit = "pcf"
            A_unit = "in<sup>2</sup>"
            s_unit = "in<sup>3</sup>"
        else:
            length_unit = "N"
            force_unit = "m"
            moment_unit = "M-m"
            pressure_unit = "MPa"
            deflection_unit = "mm"
            density_unit = "N/m<sup>2</sup>"
            A_unit = "mm<sup>2</sup>"
            s_unit = "mm<sup>3</sup>"

        # PRESSURES
        [soil_top_active, soil_end_active, soil_end_passive, water_pre_e_a, water_pre_e_p] = pressures

        # LOADS
        [trapezoidal_force, force_soil1, force_soil2, surcharge_force, water_active_force, soil_passive_force,
         water_passive_force] = loads
        [trapezoidal_arm, arm_soil1, arm_soil2, surcharge_arm, water_active_arm, soil_passive_arm,
         water_passive_arm] = arms

        # EQUATIONS
        Mr = equations[0]
        Md = equations[1]
        d_equation = equations[2]

        # # LAGGING
        # [d_concrete, lc, R_lagging, M_max_lagging, Sx_req_lagging, Sx_sup_lagging, lagging_status] = lagging_prop

        # FILLER DICT
        report_values = {
            # GENERAL INFORMATION
            "project_title": title, "designer": designer, "job_title": jobNo, "checker": checker,
            "company": company, "analysis_date": date, "comments": comment, "unit_system": unit_system,

            # GENERAL PROPERTIES
            "E": E, "FS": FS, "Fb": Fb, "Fy": Fy,
            "tieback_spacing": tieback_spacing, "allowable_deflection ": allowable_deflection,
            "retaining_height ": h,

            # LAGGING INPUTS AND OUTPUTS
            "Ph_max": ph_max, "timber_size": timber_size,

            # IMPORTANT VALUES FROM ANALYSIS
            "D": D,
            "Sx_required": Sx, "Ax_required": Ax, "M_max": M_max, "shear_max": V_max,
            "y_zero_shear": y_zero, "d0": D_0, "d_equation": d_equation, "Md": Md, "Mr": Mr,

            # PRESSURES
            "sp_s_a": soil_top_active, "sp_e_a": soil_end_active, "sp_e_p": soil_end_passive,
            "wp_e_a": water_pre_e_a, "wp_e_p": water_pre_e_p,

            # LOADS & ARMS
            "dr1": trapezoidal_force, "dr2": force_soil1, "dr3": force_soil2, "dr4": surcharge_force,
            "dr5": water_active_force,
            "sr1": soil_passive_force, "rs2": water_passive_force,
            "arm_dr1": trapezoidal_arm, "arm_dr2": arm_soil1, "arm_dr3": arm_soil2, "arm_dr4": surcharge_arm,
            "arm_dr5": water_active_arm,
            "arm_sr1": soil_passive_arm, "arm_rs2": water_passive_arm,

            # STATUSES --> IT'S ALWAYS Pass BECAUSE WE CHOOSE SECTION TO Pass IN MOMENT SHEAR AND DEFLECTION.
            "moment_status": "Pass",
            "shear_status": "Pass",

            # UNITS
            "length_unit": length_unit, "density_unit": density_unit, "force_unit": force_unit,
            "moment_unit": moment_unit,
            "deflection_unit": deflection_unit, "Ax_unit": A_unit, "Sx_unit": s_unit, "pressure_unit": pressure_unit,
            "ull": " &deg;"

        }
        return report_values
