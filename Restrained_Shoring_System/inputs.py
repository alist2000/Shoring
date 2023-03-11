import numpy as np
from sympy import symbols

unit_system = "us"

number_of_project = 1

number_of_layer = 1

delta_h = 0.01
delta_h_decimal = str(delta_h)[::-1].find('.')
if delta_h_decimal == -1:
    delta_h_decimal = 0

# anchor_number = 4
anchor_number = 1
# h = 60  # ft or m
h = 25  # ft or m
h = round(h, delta_h_decimal)

gama = 115  # pcf or N/m^3
c = 0
if anchor_number == 1:
    h1 = 10
    h_list = [h1]
else:
    h1 = 7
    h1 = round(h1, delta_h_decimal)
    h2 = 16
    h2 = round(h2, delta_h_decimal)
    h3 = 12
    h3 = round(h3, delta_h_decimal)
    h4 = 15
    h4 = round(h4, delta_h_decimal)
    hn = h - (h1 + h2 + h3 + h4)
    hn = round(hn, delta_h_decimal)
    h_list = [h1, h2, h3, h4, hn]  # len = anchor number + 1
if c != 0:
    gama_s = 20
else:
    gama_s = 0
cohesive_properties = [c, gama_s]

# water
"""
user can define is there any water or no.
then if there was water user should input 
z that water started from that. z is a height from 
top of soil."""
there_is_water = "No"
if there_is_water == "Yes":
    water_started = round(62, delta_h_decimal)  # ft or m
else:
    water_started = h * 9999999999  # just a big number

# surcharge
surcharge_type = ["Uniform"]
q_all = []
l1_all = []
l2_all = []
teta_all = []
for i in range(len(surcharge_type)):
    if surcharge_type[i] == "Uniform":
        q = 0
        # q = 72 / 0.283
        q_all.append(q)
        l1_all.append("")
        l2_all.append("")
        teta_all.append("")

        # if q < q_min:
        #     q = q_min
    elif surcharge_type[i] == "Point Load":
        q = 100000
        l1 = 1
        teta = 0
        q_all.append(q)
        l1_all.append(l1)
        l2_all.append("")
        teta_all.append(teta)

    elif surcharge_type[i] == "Line Load":
        q = ...
        l1 = ...
        q_all.append(q)
        l1_all.append(l1)
        l2_all.append("")
        teta_all.append("")

    elif surcharge_type[i] == "Strip Load":
        q = ...
        l1 = ...
        l2 = ...
        q_all.append(q)
        l1_all.append(l1)
        l2_all.append(l2)
        teta_all.append("")

surcharge_inputs = [q_all, l1_all, l2_all, teta_all]

k_formula = "User Defined"  # Rankin or Coulomb
if k_formula == "User Defined":
    ka = 0.333
    kp = 4.7
    soil_properties = [ka, kp]

elif k_formula == "Rankine":
    phi = [30]  # degree
    beta = [0]
    soil_properties = [phi, beta]

elif k_formula == "Coulomb":
    phi = [30]  # degree
    beta = [0]
    delta = [0]
    omega = [0]  # for sheet pile omega always equal to zero.
    soil_properties = [phi, beta, delta, omega]

tieback_spacing = 10  # ft or m
FS = 1.3
# anchor_angel = 15  # degree
anchor_angel = 0  # degree
anchor_angel = anchor_angel * np.pi / 180

allowable_deflection = 0.5  # in
Fy = 36  # ksi or MpaNo
E = 29000  # ksi or MPa

#  *** LAGGING ***

ph_max = 125
Fb = 20
timber_size = "3 x 16"

selected_design_sections = ["W18", "W21", "W24", "W27"]

input_values = {"number_of_project": number_of_project,
                "number_of_layer": [number_of_layer],
                "unit_system": unit_system,
                "anchor_number": [anchor_number],
                "h": [h],
                "delta_h": [delta_h],
                "gama": [gama],
                "h_list": [h_list],
                "cohesive_properties": [cohesive_properties],
                "k_formula": [k_formula],
                "soil_properties": [soil_properties],
                "there_is_water": [there_is_water],
                "water_started": [water_started],
                "surcharge_type": [surcharge_type],
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
