import numpy as np
from sympy import symbols
import json
import copy

# # NOTE: we can receive pressure distribution anyway. ask dr.
# unit_system = "us"

number_of_project = 1

number_of_layer = 1

delta_h = 0.01
delta_h_decimal = str(delta_h)[::-1].find('.')
if delta_h_decimal == -1:
    delta_h_decimal = 0


# # anchor_number = 4
# anchor_number = 1
# # h = 60  # ft or m
# h = 25  # ft or m
# h = round(h, delta_h_decimal)
#
# c = 0
# if anchor_number == 1:
#     h1 = 10
#     h_list = [h1]
# else:
#     h1 = 7
#     h1 = round(h1, delta_h_decimal)
#     h2 = 16
#     h2 = round(h2, delta_h_decimal)
#     h3 = 12
#     h3 = round(h3, delta_h_decimal)
#     h4 = 15
#     h4 = round(h4, delta_h_decimal)
#     hn = h - (h1 + h2 + h3 + h4)
#     hn = round(hn, delta_h_decimal)
#     h_list = [h1, h2, h3, h4, hn]  # len = anchor number + 1
# if c != 0:
#     gama_s = 20
# else:
#     gama_s = 0
# cohesive_properties = [c, gama_s]
#
# # water
# """
# user can define is there any water or no.
# then if there was water user should input
# z that water started from that. z is a height from
# top of soil."""
# there_is_water = "No"
# if there_is_water == "Yes":
#     water_started = round(62, delta_h_decimal)  # ft or m
# else:
#     water_started = h * 9999999999  # just a big number
#
# # surcharge
# surcharge_type = ["Uniform"]
# q_all = []
# l1_all = []
# l2_all = []
# teta_all = []
# for i in range(len(surcharge_type)):
#     if surcharge_type[i] == "Uniform":
#         q = 0
#         # q = 72 / 0.283
#         q_all.append(q)
#         l1_all.append("")
#         l2_all.append("")
#         teta_all.append("")
#
#         # if q < q_min:
#         #     q = q_min
#     elif surcharge_type[i] == "Point Load":
#         q = 100000
#         l1 = 1
#         teta = 0
#         q_all.append(q)
#         l1_all.append(l1)
#         l2_all.append("")
#         teta_all.append(teta)
#
#     elif surcharge_type[i] == "Line Load":
#         q = ...
#         l1 = ...
#         q_all.append(q)
#         l1_all.append(l1)
#         l2_all.append("")
#         teta_all.append("")
#
#     elif surcharge_type[i] == "Strip Load":
#         q = ...
#         l1 = ...
#         l2 = ...
#         q_all.append(q)
#         l1_all.append(l1)
#         l2_all.append(l2)
#         teta_all.append("")
#
# surcharge_inputs = [q_all, l1_all, l2_all, teta_all]
#
# pressure_distribution = "Trapezoidal"
#
# k_formula = "User Defined"  # Rankin or Coulomb
# if k_formula == "User Defined":
#     pressure_distribution = "Triangle"
#     sigma_a = 100
#     gama = 1  # pcf or N/m^3
#     """
#     inputs: EFPa, EFPp, Ka surcharge, sigma_a, Pressure distribution.
#     consider Ka = EFPa , Kp = EFPp and gama = 1
#     if pressure distribution = triangle --> sigma_a = EFPa × h"""
#     ka = 38.3  # EFPa
#     kp = 540.5  # EFPp
#     ka_surcharge = 0.333
#     if pressure_distribution == "Triangle":
#         sigma_a = ka * h
#
#     soil_properties = [ka, kp, sigma_a, ka_surcharge]
#
# elif k_formula == "Rankine":
#     gama = 115  # pcf or N/m^3
#     phi = [30]  # degree
#     beta = [0]
#     soil_properties = [phi, beta]
#
# elif k_formula == "Coulomb":
#     gama = 115  # pcf or N/m^3
#     phi = [30]  # degree
#     beta = [0]
#     delta = [0]
#     omega = [0]  # for sheet pile omega always equal to zero.
#     soil_properties = [phi, beta, delta, omega]
#
# tieback_spacing = 10  # ft or m
# FS = 1.3
# # anchor_angel = 15  # degree
# anchor_angel = 0  # degree
# anchor_angel = anchor_angel * np.pi / 180
#
# allowable_deflection = 0.5  # in
# Fy = 36  # ksi or MpaNo
# E = 29000  # ksi or MPa
#
# #  *** LAGGING ***
#
# ph_max = 125
# Fb = 20
# timber_size = "3 x 16"
#
# selected_design_sections = ["W18", "W21", "W24", "W27"]
#
# input_values = {"number_of_project": number_of_project,
#                 "number_of_layer": [number_of_layer],
#                 "unit_system": unit_system,
#                 "anchor_number": [anchor_number],
#                 "h": [h],
#                 "delta_h": [delta_h],
#                 "gama": [gama],
#                 "h_list": [h_list],
#                 "cohesive_properties": [cohesive_properties],
#                 "pressure_distribution": [pressure_distribution],
#                 "k_formula": [k_formula],
#                 "soil_properties": [soil_properties],
#                 "there_is_water": [there_is_water],
#                 "water_started": [water_started],
#                 "surcharge_type": [surcharge_type],
#                 "surcharge_inputs": [surcharge_inputs],
#                 "tieback_spacing": [tieback_spacing],
#                 "anchor_angel": [anchor_angel],
#                 "FS": [FS],
#                 "E": [E],
#                 "Fy": [Fy],
#                 "allowable_deflection": [allowable_deflection],
#                 "selected_design_sections": [selected_design_sections],
#                 "ph_max": [ph_max],
#                 "Fb": [Fb],
#                 "timber_size": [timber_size]
#                 }


def input_single(input_values):
    # INPUT errors --> can be developed. now we have no error for inputs.
    # *** pile spacing need a limitation.

    # *** GENERAL INFORMATION ***

    product_id = input_values.get("product_id")
    user_id = input_values.get("user_id")
    unit_system = input_values.get("information").get("unit")
    title = input_values.get("information").get("title")
    jobNo = input_values.get("information").get("jobNo")
    designer = input_values.get("information").get("designer")
    checker = input_values.get("information").get("checker")
    company = input_values.get("information").get("company")
    client = input_values.get("information").get("client")
    date = input_values.get("information").get("date")
    comment = input_values.get("information").get("comment")
    other = input_values.get("information").get("other")

    project_information = [product_id, user_id, title, jobNo, designer, checker, company, client, date, comment, other]

    # *** General Properties ***

    FS = abs(float(input_values.get("data").get("General Properties").get("FS").get("value")))
    Fy = abs(float(input_values.get("data").get("General Properties").get("Fy").get("value")))
    E = abs(float(input_values.get("data").get("General Properties").get("E").get("value")))
    tieback_spacing = abs(float(input_values.get("data").get("General Properties").get("Pile Spacing").get("value")))
    allowable_deflection = abs(
        float(input_values.get("data").get("General Properties").get("Allowable Deflection").get("value")))
    selected_design_sections = json.loads(
        input_values.get("data").get("General Properties").get("Sections").get("value")).get(
        "item").split(",")  # this value should be converted to a list.

    # *** Geometrical Properties ***
    retaining_height = abs(
        float(input_values.get("data").get("Geometrical Properties").get("Retaining Height").get("value")))

    anchor_number = abs(int(
        json.loads(input_values.get("data").get("Geometrical Properties").get("Number of Anchors").get("value")).get(
            "item")))
    anchor_angel = abs(
        float(input_values.get("data").get("Geometrical Properties").get("Angle of Anchors").get("value")))
    h_list = []
    for i in range(1, anchor_number + 1):
        h1 = abs(
            float(input_values.get("data").get("Geometrical Properties").get(f"h{str(i)}").get("value")))
        h1 = round(h1, delta_h_decimal)
        h_list.append(h1)
    if anchor_number > 1:
        h_listt = copy.deepcopy(h_list)
        hn = retaining_height - sum(h_listt)
        h_list.append(hn)

    # *** SOIL PROPERTIES ***
    formula = json.loads(input_values.get("data").get("Soil Properties").get("Formula").get("value")).get(
        "item")
    Formula_passive = Formula_active = formula
    space = " "

    EFPa_valid = True
    phi_valid = True
    EFPp_valid = True
    Ka_valid = True
    gama_s_valid = True
    gama_valid = True
    sigma_a_valid = True

    if formula == "User Defined":
        gama = 1  # pcf or N/m^3 (it's just an assumption)
        EFPa = Ka = abs(
            float(input_values.get("data").get("Soil Properties").get("Equivalent Fluid Pressure Active").get("value")))
        EFPp = Kp = abs(
            float(
                input_values.get("data").get("Soil Properties").get("Equivalent Fluid Pressure Passive").get("value")))
        Ka_surcharge = abs(float(input_values.get("data").get("Soil Properties").get("Ka Surcharge").get("value")))
        pressure_distribution = json.loads(
            input_values.get("data").get("Soil Properties").get("Pressure Distribution").get("value")).get(
            "item")
        sigma_a = abs(
            float(input_values.get("data").get("Soil Properties").get("σa").get("value")))
        if pressure_distribution == "Triangle":
            sigma_a = Ka * retaining_height
            h_list_pressure = ["default"]
        else:
            try:
                ht1 = abs(float(input_values.get("data").get("Soil Properties").get("Ht1").get("value")))
                ht1 = round(ht1, delta_h_decimal)
            except:
                ht1 = retaining_height
            try:
                ht2 = abs(float(input_values.get("data").get("Soil Properties").get("Ht2").get("value")))
                ht2 = round(ht2, delta_h_decimal)
            except:
                ht2 = ht1
            if ht2 + ht1 >= retaining_height:
                h_list_pressure = ["default"]
            else:
                h_list_pressure = [ht1, round(retaining_height - (ht1 + ht2), delta_h_decimal), ht2]

        soil_properties = [Ka, Kp, sigma_a, Ka_surcharge, h_list_pressure]

        EFPa_valid = EFPa
        EFPp_valid = EFPp
        Ka_valid = Ka_surcharge
        sigma_a_valid = sigma_a

    elif formula == "Rankine" or "Coulomb":
        gama = abs(float(input_values.get("data").get("Soil Properties").get("γ").get("value")))  # pcf or N/m^3
        phi = [abs(float(input_values.get("data").get("Soil Properties").get('Φ').get(
            "value")))]  # degree  (CAN BE ZERO !??)
        beta_active = [abs(float(input_values.get("data").get("Soil Properties").get("β Active").get("value")))]
        beta_passive = [abs(float(input_values.get("data").get("Soil Properties").get("β Passive").get("value")))]
        phi_valid = phi
        if formula == "Coulomb":
            delta = [abs(float(input_values.get("data").get("Soil Properties").get("δ").get("value")))]
            omega = [0]  # for sheet pile omega always equal to zero.
            soil_properties = [phi, beta_active, beta_passive, delta, omega]
        else:
            soil_properties = [phi, beta_active, beta_passive]

        pressure_distribution = "Trapezoidal"

    soil_cohesion = json.loads(input_values.get("data").get("Soil Properties").get("Soil Cohesion").get("value")).get(
        "item")
    if soil_cohesion == "Cohesionless":
        c = 0
        gama_s = 0
    else:
        c = abs(float(input_values.get("data").get("Soil Properties").get("c").get("value")))  # pcf or N/m^3
        if c != 0:
            gama_s = abs(float(input_values.get("data").get("Soil Properties").get("γs").get("value")))  # pcf or N/m^3
        else:
            gama_s = 0
    cohesive_properties = [c, gama_s]
    gama_s_valid = gama_s

    # *** WATER PROPERTIES ***
    there_is_water = json.loads(
        input_values.get("data").get("Water Properties").get("There is water?").get("value")).get(
        "item")
    if there_is_water == "Yes":
        water_started = abs(
            float(input_values.get("data").get("Water Properties").get("Water level start from top").get("value")))
        water_started = round(water_started, delta_h_decimal)  # ft or m
    else:
        water_started = retaining_height * 9999999999  # just a big number

    # *** SURCHARGE ***
    try:
        surcharge_depth = abs(
            float(input_values.get("data").get("Surcharge").get("Surcharge Effective Depth").get("value")))
    except:
        surcharge_depth = retaining_height  # I should define it in site ***
    if surcharge_depth > retaining_height:  # surcharge has no effect under excavation line.(ASSUMED ACCORDING TO MANUAL FILE)
        surcharge_depth = retaining_height

    max_surcharge_site = 4
    surcharge_type = [
        json.loads(input_values.get("data").get("Surcharge").get("Load Type" + space * layer).get("value")).get(
            "item") for layer in range(max_surcharge_site)]

    q_all = []
    l1_all = []
    l2_all = []
    teta_all = []
    for i in range(len(surcharge_type)):
        if surcharge_type[i] == "Uniform":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append("")
            l2_all.append("")
            teta_all.append("")

        elif surcharge_type[i] == "Point Load":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))
            l1 = abs(float(input_values.get("data").get("Surcharge").get('L1' + i * space).get(
                "value")))
            teta = abs(float(input_values.get("data").get("Surcharge").get('Ɵ' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append(l1)
            l2_all.append("")
            teta_all.append(teta)

        elif surcharge_type[i] == "Line Load":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))

            l1 = abs(float(input_values.get("data").get("Surcharge").get('L1' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append(l1)
            l2_all.append("")
            teta_all.append("")

        elif surcharge_type[i] == "Strip Load":
            q = abs(float(input_values.get("data").get("Surcharge").get('q' + i * space).get(
                "value")))
            l1 = abs(float(input_values.get("data").get("Surcharge").get('L1' + i * space).get(
                "value")))
            l2 = abs(float(input_values.get("data").get("Surcharge").get('L2' + i * space).get(
                "value")))
            q_all.append(q)
            l1_all.append(l1)
            l2_all.append(l2)
            teta_all.append("")

        else:
            q_all.append(0)
            l1_all.append(0)
            l2_all.append(0)
            teta_all.append(0)

    surcharge_inputs = [q_all, l1_all, l2_all, teta_all]

    #  *** LAGGING ***

    ph_max = abs(float(input_values.get("data").get("Lagging").get('Ph max').get(
        "value")))
    Fb = abs(float(input_values.get("data").get("Lagging").get('Fb').get(
        "value")))
    timber_size = json.loads(input_values.get("data").get("Lagging").get("Timber Size").get("value")).get("item")

    # *** CHECK ERROR ***
    validation_dict = {"FS": FS, "Fy": Fy, "E": E, "Tieback Spacing": tieback_spacing,
                       "Allowable Deflection": allowable_deflection, "Retaining Height": retaining_height,
                       "Ph max": ph_max, "Fb": Fb, "γ": gama_valid, "EFPa": EFPa_valid, "EFPp": EFPp_valid,
                       "Ka surcharge": Ka_valid, "Φ": phi_valid, "σa": sigma_a_valid, "γs": gama_s_valid}
    status, input_errors = validation_zero(validation_dict)
    error_number = len(input_errors)
    error_description = input_errors
    input_validation = {"error_number": error_number,
                        "description": error_description}
    final_values = {"input_validation": input_validation,
                    "project_information": project_information,
                    "number_of_project": number_of_project,
                    "number_of_layer": [number_of_layer],
                    "unit_system": unit_system,
                    "anchor_number": [anchor_number],
                    "h": [retaining_height],
                    "delta_h": [delta_h],
                    "gama": [gama],
                    "h_list": [h_list],
                    "cohesive_properties": [cohesive_properties],
                    "pressure_distribution": [pressure_distribution],
                    "k_formula": [formula],
                    "soil_properties": [soil_properties],
                    "there_is_water": [there_is_water],
                    "water_started": [water_started],
                    "surcharge_type": [surcharge_type],
                    "surcharge_depth": [surcharge_depth],
                    "surcharge_inputs": [surcharge_inputs],
                    "tieback_spacing": [tieback_spacing],
                    "anchor_angel": [anchor_angel],
                    "FS": [FS],
                    "E": [E],
                    "Fy": [Fy],
                    "allowable_deflection": [allowable_deflection],
                    "selected_design_sections": [selected_design_sections],
                    "ph_max": [ph_max],
                    "Fb": [Fb],
                    "timber_size": [timber_size]
                    }

    return final_values


def validation_zero(item):
    errors = []
    values = list(item.values())
    keys = list(item.keys())
    for i in range(len(values)):
        if values[i] == 0:
            errors.append([f"{keys[i]} can not be zero!"])
    return not bool(errors), errors
