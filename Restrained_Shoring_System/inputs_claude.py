import numpy as np
import json

number_of_project = 1

number_of_layer = 1


class InputHandler:
    def __init__(self, input_values):
        self.input_values = input_values
        self.project_information = None
        self.number_of_project = None
        self.number_of_layer_list = None
        self.unit_system = None
        self.anchor_number_list = None
        self.h_list = None
        self.delta_h_list = None
        self.gama_list = None
        self.h_list_list = None
        self.cohesive_properties_list = None
        self.pressure_distribution_list = None
        self.k_formula_list = None
        self.soil_properties_list = None
        self.there_is_water_list = None
        self.water_started_list = None
        self.surcharge_type_list = None
        self.surcharge_depth_list = None
        self.surcharge_inputs_list = None
        self.tieback_spacing_list = None
        self.anchor_angle_list = None
        self.FS_list = None
        self.E_list = None
        self.Fy_list = None
        self.allowable_deflection_list = None
        self.selected_design_sections_list = None
        self.ph_max_list = None
        self.Fb_list = None
        self.timber_size_list = None
        self.input_errors = None

        delta_h = 0.01
        self.delta_h_decimal = str(delta_h)[::-1].find('.')
        if self.delta_h_decimal == -1:
            self.delta_h_decimal = 0

        self.parse_input_values()

    def parse_input_values(self):
        self.parse_project_information()
        self.parse_general_properties()
        self.parse_geometrical_properties()
        self.parse_soil_properties()
        self.parse_water_properties()
        self.parse_surcharge_properties()
        self.parse_lagging_properties()
        self.validate_inputs()

    def parse_project_information(self):
        self.project_information = [
            self.input_values.get("product_id"),
            self.input_values.get("user_id"),
            self.input_values.get("information").get("title"),
            self.input_values.get("information").get("jobNo"),
            self.input_values.get("information").get("designer"),
            self.input_values.get("information").get("checker"),
            self.input_values.get("information").get("company"),
            self.input_values.get("information").get("client"),
            self.input_values.get("information").get("date"),
            self.input_values.get("information").get("comment"),
            self.input_values.get("information").get("other")
        ]

    def parse_general_properties(self):
        self.number_of_project = 1
        self.number_of_layer_list = [1]
        self.unit_system = self.input_values.get("information").get("unit")
        self.FS_list = [abs(float(self.input_values.get("data").get("General Properties").get("FS").get("value")))]
        self.Fy_list = [abs(float(self.input_values.get("data").get("General Properties").get("Fy").get("value")))]
        self.E_list = [abs(float(self.input_values.get("data").get("General Properties").get("E").get("value")))]
        self.tieback_spacing_list = [
            abs(float(self.input_values.get("data").get("General Properties").get("Pile Spacing").get("value")))]
        self.allowable_deflection_list = [abs(float(
            self.input_values.get("data").get("General Properties").get("Allowable Deflection").get("value")))]
        self.selected_design_sections_list = [
            json.loads(self.input_values.get("data").get("General Properties").get("Sections").get("value")).get(
                "item").split(",")]

    def parse_geometrical_properties(self):
        self.h_list = [abs(float(
            self.input_values.get("data").get("Geometrical Properties").get("Retaining Height").get("value")))]
        self.anchor_number_list = [abs(int(json.loads(
            self.input_values.get("data").get("Geometrical Properties").get("Number of Anchors").get("value")).get(
            "item")))]
        self.anchor_angle_list = [abs(float(
            self.input_values.get("data").get("Geometrical Properties").get("Angle of Anchors").get(
                "value"))) * np.pi / 180]
        self.h_list_list = []
        for i in range(1, self.anchor_number_list[0] + 1):
            h1 = abs(float(self.input_values.get("data").get("Geometrical Properties").get(f"h{str(i)}").get("value")))
            h1 = round(h1, self.delta_h_decimal)
            self.h_list_list.append(h1)
        if self.anchor_number_list[0] > 1:
            self.h_list_list.append(round(self.h_list[0] - sum(self.h_list_list), self.delta_h_decimal))
        self.delta_h_list = [self.input_values.get("information").get("delta_h")]

    def parse_soil_properties(self):
        formula = json.loads(self.input_values.get("data").get("Soil Properties").get("Formula").get("value")).get(
            "item")
        self.k_formula_list = [formula]
        Formula_passive = Formula_active = formula
        self.space = " "

        if formula == "User Defined":
            self.gama_list = [1]  # pcf or N/m^3 (it's just an assumption)
            ka = abs(float(
                self.input_values.get("data").get("Soil Properties").get("Equivalent Fluid Pressure Active").get(
                    "value")))
            kp = abs(float(
                self.input_values.get("data").get("Soil Properties").get("Equivalent Fluid Pressure Passive").get(
                    "value")))
            ka_surcharge = abs(
                float(self.input_values.get("data").get("Soil Properties").get("Ka Surcharge").get("value")))
            self.pressure_distribution_list = [json.loads(
                self.input_values.get("data").get("Soil Properties").get("Pressure Distribution").get("value")).get(
                "item")]
            sigma_a = abs(float(self.input_values.get("data").get("Soil Properties").get("σa").get("value")))
            if self.pressure_distribution_list[0] == "Triangle":
                sigma_a = ka * self.h_list[0]
                h_list_pressure = ["default"]
            else:
                try:
                    ht1 = abs(float(self.input_values.get("data").get("Soil Properties").get("Ht1").get("value")))
                    ht1 = round(ht1, self.delta_h_decimal)
                except:
                    ht1 = self.h_list[0]
                try:
                    ht2 = abs(float(self.input_values.get("data").get("Soil Properties").get("Ht2").get("value")))
                    ht2 = round(ht2, self.delta_h_decimal)
                except:
                    ht2 = ht1
                if ht2 + ht1 >= self.h_list[0]:
                    h_list_pressure = ["default"]
                else:
                    h_list_pressure = [ht1, round(self.h_list[0] - (ht1 + ht2), self.delta_h_decimal), ht2]

            self.soil_properties_list = [[ka, kp, sigma_a, ka_surcharge, h_list_pressure]]

        elif formula == "Rankine" or formula == "Coulomb":
            self.gama_list

    def parse_water_properties(self):
        there_is_water = json.loads(
            self.input_values.get("data").get("Water Properties").get("There is water?").get("value")).get("item")
        self.there_is_water_list = ["Yes" if there_is_water else "No"]
        if there_is_water:
            self.water_started_list = [round(abs(float(
                self.input_values.get("data").get("Water Properties").get("Water level start from top").get("value"))),
                self.delta_h_decimal)]
        else:
            self.water_started_list = [self.h_list[0] * 9999999999]  # just a big number

    def parse_surcharge_properties(self):
        try:
            self.surcharge_depth_list = [abs(float(
                self.input_values.get("data").get("Surcharge").get("Surcharge Effective Depth").get("value")))]
        except:
            self.surcharge_depth_list = [self.h_list[0]]  # I should define it in site ***
        if self.surcharge_depth_list[0] > self.h_list[
            0]:  # surcharge has no effect under excavation line.(ASSUMED ACCORDING TO MANUAL FILE)
            self.surcharge_depth_list[0] = self.h_list[0]

        max_surcharge_site = 4
        self.surcharge_type_list = [json.loads(
            self.input_values.get("data").get("Surcharge").get("Load Type" + self.space * layer).get("value")).get(
            "item")
                                    for layer in range(max_surcharge_site)]

        q_all, l1_all, l2_all, teta_all = [], [], [], []
        for i in range(len(self.surcharge_type_list)):
            surcharge_type = self.surcharge_type_list[i]
            if surcharge_type == "Uniform":
                q = abs(float(self.input_values.get("data").get("Surcharge").get('q' + i * self.space).get("value")))
                q_all.append(q)
                l1_all.append("")
                l2_all.append("")
                teta_all.append("")

            elif surcharge_type == "Point Load":
                q = abs(float(self.input_values.get("data").get("Surcharge").get('q' + i * self.space).get("value")))
                l1 = abs(float(self.input_values.get("data").get("Surcharge").get('L1' + i * self.space).get("value")))
                teta = abs(float(self.input_values.get("data").get("Surcharge").get('Ɵ' + i * self.space).get("value")))
                q_all.append(q)
                l1_all.append(l1)
                l2_all.append("")
                teta_all.append(teta)

            elif surcharge_type == "Line Load":
                q = abs(float(self.input_values.get("data").get("Surcharge").get('q' + i * self.space).get("value")))
                l1 = abs(float(self.input_values.get("data").get("Surcharge").get('L1' + i * self.space).get("value")))
                q_all.append(q)
                l1_all.append(l1)
                l2_all.append("")
                teta_all.append("")

            elif surcharge_type == "Strip Load":
                q = abs(float(self.input_values.get("data").get("Surcharge").get('q' + i * self.space).get("value")))
                l1 = abs(float(self.input_values.get("data").get("Surcharge").get('L1' + i * self.space).get("value")))
                l2 = abs(float(self.input_values.get("data").get("Surcharge").get('L2' + i * self.space).get("value")))
                q_all.append(q)
                l1_all.append(l1)
                l2_all.append(l2)
                teta_all.append("")

            else:
                q_all.append(0)
                l1_all.append(0)
                l2_all.append(0)
                teta_all.append(0)

        self.surcharge_inputs_list = [[q_all, l1_all, l2_all, teta_all]]

    def parse_lagging_properties(self):
        self.ph_max_list = [abs(float(self.input_values.get("data").get("Lagging").get('Ph max').get("value")))]
        self.Fb_list = [abs(float(self.input_values.get("data").get("Lagging").get('Fb').get("value")))]
        self.timber_size_list = [
            json.loads(self.input_values.get("data").get("Lagging").get("Timber Size").get("value")).get("item")]

    def validate_inputs(self):
        validation_dict = {"FS": self.FS_list[0], "Fy": self.Fy_list[0], "E": self.E_list[0],
                           "Tieback Spacing": self.tieback_spacing_list[0],
                           "Allowable Deflection": self.allowable_deflection_list[0],
                           "Retaining Height": self.h_list[0],
                           "Ph max": self.ph_max_list[0], "Fb": self.Fb_list[0], "γ": self.gama_list[0],
                           "EFPa": self.soil_properties_list[0][0],
                           "EFPp": self.soil_properties_list[0][1], "Ka surcharge": self.soil_properties_list[0][3],
                           "Φ": self.soil_properties_list[0][0],
                           "σa": self.soil_properties_list[0][2], "γs": self.cohesive_properties_list[0][1]}
        status, self.input_errors = self.validation_zero(validation_dict)
        self.error_number = len(self.input_errors)
        self.error_description = self.input_errors
        self.input_validation = {"error_number": self.error_number,
                                 "description": self.error_description}

    def validation_zero(self, item):
        errors = []
        values = list(item.values())
        keys = list(item.keys())
        for i in range(len(values)):
            if values[i] == 0:
                errors.append([f"{keys[i]} can not be zero!"])
        return not bool(errors), errors
