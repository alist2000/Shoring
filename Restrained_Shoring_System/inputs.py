unit_system = "us"

number_of_project = 1

number_of_layer = 1

delta_h = 0.01

anchor_number = 1
h = 25  # ft or m
gama = 115  # pcf or Mpa
c = 0
if anchor_number == 1:
    h1 = 10
    h_list = [h1]
else:
    h1 = ...
    hn = ...
    h_list = [h1, hn]
if c != 0:
    gama_s = ...
else:
    gama_s = 0
cohesive_properties = [c, gama_s]

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
                "surcharge_type": [surcharge_type],
                "surcharge_inputs": [surcharge_inputs],
                "tieback_spacing": [tieback_spacing],
                "FS": [FS]
                }
