from database import SQL_reader


class design:
    """this class with some change will be very useful if user input exact a section not a list of them with a title."""

    def __init__(self, section, E, Fy, unit_system):
        self.section = section
        self.E = E
        self.Fy = Fy
        self.unit_system = unit_system

    def moment_design(self, M_max):
        section = self.section
        Fy = self.Fy
        unit_system = self.unit_system
        fb = 0.66 * Fy

        if unit_system == "us":
            s_required = M_max * 12 / (fb * 1000)  # s unit --> inch^3
        else:
            # s_required = M_max * 10 ** 6 / fb  # s unit --> mm^3
            s_required = M_max * 10 ** 3 / fb  # s unit --> mm^3   *** MUST BE CHECKED ***
        output = SQL_reader(section, "not important A", s_required, "not important I", "moment", unit_system)
        return output, s_required

    def shear_design(self, V_max):
        section = self.section
        Fy = self.Fy
        unit_system = self.unit_system

        if unit_system == "us":
            A_required = V_max / (0.44 * Fy * 1000)  # in^2
        else:
            # A_required = V_max * 1000 / (0.44 * Fy)  # mm^2
            A_required = V_max / (0.44 * Fy)  # mm^2  *** MUST BE CHECKED ***
        output = SQL_reader(section, A_required, " not important s", "not important I", "shear", unit_system)
        return output, A_required

    def deflection_design(self, allowable_deflection, deflection_max):
        section = self.section
        E = self.E
        unit_system = self.unit_system

        if unit_system == "us":
            E_allowable_deflection = E * 1000 * float(allowable_deflection) / (12 ** 3)  # E: Ksi , M: lb.ft
        else:
            # E_allowable_deflection = E * float(allowable_deflection) * (10 ** 9)  # E: Mpa , M: N.m
            E_allowable_deflection = E * float(allowable_deflection) * (
                        10 ** (-9))  # E: Mpa , M: N.m  *** MUST BE CHECKED ***
        Ix_min = deflection_max / E_allowable_deflection
        output = SQL_reader(section, "not important A", " not important s", Ix_min, "deflection", unit_system)
        return output


def subscription(moment_section, shear_section, deflection_section):
    qualified_section = []
    qualified_section_index = []

    base_len = 9999999
    base_subscription = []
    for i in [moment_section, shear_section, deflection_section]:
        if len(i["section"]) <= base_len:
            base_len = len(i["section"])
            base_subscription = i

    section_list = []
    Ix_list = []
    area_list = []
    Sx_list = []
    wc_list = []
    h_list = []
    bf_list = []
    tw_list = []
    tf_list = []
    number_of_section = 0
    for i in range(len(base_subscription["section"])):
        if base_subscription["section"][i] in moment_section["section"][i] and shear_section["section"][i] and \
                deflection_section["section"][i]:
            section_list.append(base_subscription["section"][i])
            Ix_list.append(base_subscription["Ix"][i])
            area_list.append(base_subscription["area"][i])
            Sx_list.append(base_subscription["Sx"][i])
            wc_list.append(base_subscription["wc"][i])
            h_list.append(base_subscription["h"][i])
            bf_list.append(base_subscription["bf"][i])
            tw_list.append(base_subscription["tw"][i])
            tf_list.append(base_subscription["tf"][i])
            number_of_section += 1

    return {"section": section_list, "Ix": Ix_list, "area": area_list, "Sx": Sx_list, "wc": wc_list, "h": h_list,
            "bf": bf_list, "tw": tw_list, "tf": tf_list}, number_of_section


def min_weight(sections):
    base_weight = sections["wc"][0]
    best_section_index = 0
    for i in range(len(sections["wc"])):
        if sections["wc"][i] <= base_weight:
            best_section_index = i

    return {"section": sections["section"][best_section_index], "Ix": sections["Ix"][best_section_index],
            "area": sections["area"][best_section_index], "Sx": sections["Sx"][best_section_index],
            "wc": sections["wc"][best_section_index], "h": sections["h"][best_section_index],
            "bf": sections["bf"][best_section_index], "tw": sections["tw"][best_section_index],
            "tf": sections["tf"][best_section_index]}
