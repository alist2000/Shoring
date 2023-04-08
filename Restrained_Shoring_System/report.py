import pandas as pd
import pyarrow.feather as feather

from front.report import load_distribution, Formula


# creating excel
def create_feather(z, value, title, excel_name):
    data = list(zip(z, value))
    df = pd.DataFrame(data, columns=["Z", title])
    df.to_feather("reports/excel/" + excel_name + ".feather")
    # df.to_csv("reports/excel/" + excel_name + ".csv")


def report_final(input_values, DCR_moment, DCR_shear, DCR_deflection, DCR_lagging, Sx, Ax, M_max, V_max,
                 deflection_max, y_zero, k_or_EFPa, k_or_EFPp, load_distribution_prop, pressures, loads, arms, moments,
                 equations, D_0, D,
                 maximums, section_prop, lagging_prop):
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
        report_values = {"project_title": title, "designer": designer, "job_title": jobNo, "checker": checker,
                         "company": company, "analysis_date": date, "comments": comment, "unit_system": unit_system,
                         "E": E, "FS": FS, "Fb": Fb, "Fy": Fy,
                         "tieback_spacing": tieback_spacing, "Sections": selected_design_sections,
                         "retaining_height ": h, "soil_layer_number": 1, "formula": k_formula}

