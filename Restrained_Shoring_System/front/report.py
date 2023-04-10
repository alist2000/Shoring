def load_distribution(unit_system, sigma_a, retaining_height, ht1=0, ht2=0):
    if unit_system == "us":
        pressure_unit = """Kips/ft<sup>2</sup>"""
        length_unit = "ft"
    else:
        pressure_unit = """KN/m<sup>2</sup>"""
        length_unit = "m"
    if ht1 == 0 and ht2 == 0:  # load distribution: Triangle
        table = f"""<tbody>
        <tr>
            <td style="width: 25%;">
                <t1>&#x3C3;<sub>a</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2> {sigma_a} {pressure_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Retaining Height:
</t1>
            </td>
            <td style="width: 25%;">
                <t2>{retaining_height} {length_unit}</t2>
            </td>
        </tr>
       
        </tbody>"""
    elif ht1 != 0 and ht2 == 0:
        table = f"""<tbody>
                <tr>
                    <td style="width: 25%;">
                        <t1>&#x3C3;<sub>a</sub>:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{sigma_a} {pressure_unit}</t2>
                    </td>
                    <td style="width: 25%;">
                        <t1>Retaining Height:
        </t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{retaining_height} {length_unit}</t2>
                    </td>
                </tr>
                <tr>
                    <td style="width: 25%;">
                        <t1>H<sub>T1</sub>:</t1>
                    </td>
                    <td style="width: 25%;">
                        <t2>{ht1} {length_unit}</t2>
                    </td>
                    <td style="width: 25%;">
                        <t1></t1>
                    </td>
                    <td style="width: 25%;">
                        <t2></t2>
                    </td>
                </tr>
                </tbody>"""
    elif ht1 != 0 and ht2 != 0:
        table = f"""<tbody>
                        <tr>
                            <td style="width: 25%;">
                                <t1>&#x3C3;<sub>a</sub>:</t1>
                            </td>
                            <td style="width: 25%;">
                                <t2>{sigma_a} {pressure_unit}</t2>
                            </td>
                            <td style="width: 25%;">
                                <t1>Retaining Height:
                </t1>
                            </td>
                            <td style="width: 25%;">
                                <t2>{retaining_height} {length_unit}</t2>
                            </td>
                        </tr>
                        <tr>
                            <td style="width: 25%;">
                                <t1>H<sub>T1</sub>:</t1>
                            </td>
                            <td style="width: 25%;">
                                <t2>{ht1} {length_unit}</t2>
                            </td>
                            <td style="width: 25%;">
                                <t1>H<sub>T2</sub>:</t1>
                            </td>
                            <td style="width: 25%;">
                                <t2>{ht2} {length_unit}</t2>
                            </td>
                        </tr>
                        </tbody>"""

    else:
        table = """"""

    file = open("reports/template/load_distribution.html", "w")
    file.write(table)
    file.close()


def Formula(formula, soil_prop, retaining_height, unit_system):
    if unit_system == "us":
        length_unit = "ft"
        density_unit = "pcf"
        pressure_unit = "psf"
    else:
        length_unit = "m"
        density_unit = "N/m<sup>3</sup>"
        pressure_unit = "N/m<sup>2</sup>"

    if formula == "User Defined":
        [EFPa, EFPp, ka_surcharge, c] = soil_prop
        table_properties = f"""<tbody>
        <tr>
            <td style="width: 25%;">
                <t1>Retaining Height:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{retaining_height} {length_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Number of Soil Layer:</t1>
            </td>
            <td style="width: 25%;">
                <t2> 1 </t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>EFP<sub>a</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{EFPa} {density_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>EFP<sub>p</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{EFPp} {density_unit}</t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>K<sub>a</sub> Surcharge:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{ka_surcharge}</t2>
            </td>
            <td style="width: 25%;">
                <t1>c:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{c} {pressure_unit}</t2>
            </td>
            
        </tr>

        </tbody>"""
        table_main = f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 30%;">
                <t1>Formula: {formula}</t1>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>EFP<sub>a</sub></em>: {EFPa}
                </t2>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>EFP<sub>p</sub></em>: {EFPp}
                </t2>
            </td>
        </tr>
        </tbody>"""
    else:
        [ka, kp, gama, phi, beta_active, beta_passive, delta, c] = soil_prop
        table_properties = f"""<tbody>
        <tr>
            <td style="width: 25%;">
                <t1>Retaining Height:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{retaining_height} {length_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Number of Soil Layer:</t1>
            </td>
            <td style="width: 25%;">
                <t2> 1 </t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>&#611;:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{gama} {density_unit}</t2>
            </td>
            <td style="width: 25%;">
                <t1>&Phi;:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{phi} &deg;</t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>&#946; Active:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{beta_active} &deg;</t2>
            </td>
            <td style="width: 25%;">
                <t1>&#946; Passive:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{beta_passive} &deg;</t2>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1>&#948;:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{delta} &deg;</t2>
            </td>
            <td style="width: 25%;">
                <t1>c:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{c} {pressure_unit}</t2>
            </td>
            
        </tr>

        </tbody>"""
        table = """<tbody>
        <tr>
            <td style="width: 15%;">
                <t1>Rankine Theory</t1>
            </td>
            <td style="width: 85%;">
                <t2>
                </t2>
            </td>
        </tr>
        </tbody>
    </table>

    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 70%;">
            $$K_a = {cos\beta {cos\beta - \sqrt{cos^2\beta-cos^2\phi} \over cos\beta + \sqrt{cos^2\beta-cos^2\phi}}}.$$
            </td>
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        <tr>
            <td style="width: 70%;">
                $$K_p = {cos\beta {cos\beta + \sqrt{cos^2\beta-cos^2\phi} \over cos\beta - \sqrt{cos^2\beta-cos^2\phi}}}.$$
            </td>
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 15%;">
                <t1>Coulomb Theory</t1>
            </td>
            <td style="width: 85%;">
                <t2>
                </t2>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 70%;">
            $$K_a = {cos^2(\phi - \omega)\over cos^2\omega cos(\delta + \omega)[1 + \sqrt{sin(\delta + \phi) sin(\phi - \beta) \over cos(\delta + \omega) cos(\omega - \beta)}]^2}.$$
                     </td>
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        <tr>
            <td style="width: 70%;">
                $$K_p = {cos^2(\phi + \omega)\over cos^2\omega cos(\delta - \omega)[1 - \sqrt{sin(\delta + \phi) sin(\phi + \beta) \over cos(\delta - \omega) cos(\beta - \omega)}]^2}.$$
            <td style="width: 30%; align-items: center;">
            </td>
        </tr>
        </tbody>
    </table>
    """
        table2 = f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 30%;">
                <t1>Formula: {formula}</t1>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>K<sub>a</sub></em>: {ka}
                </t2>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>K<sub>p</sub></em>: {kp}
                </t2>
            </td>
        </tr>
        </tbody>"""
        table_main = table + table2

    file2 = open("reports/template/soil_properties.html", "w")
    file2.write(table_properties)
    file2.close()

    file = open("reports/template/formula.html", "w")
    file.write(table_main)
    file.close()


def raker_force(unit_system, forces):
    if unit_system == "us":
        force_unit = """Kips"""
    else:
        force_unit = """Kips"""
    table = """<tbody><tr>"""
    for i in range(len(forces)):
        if i % 2 == 0 and i != 0:
            table += """</tr><tr>"""

        table += f"""
            <td style="width: 25%;">
                <t1>R<sub>{ i + 1 }</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2> {forces[i]} {force_unit}</t2>
            </td>
    """
    table += """</tr></tbody>"""
    file = open("reports/template/raker_forces.html", "w")
    file.write(table)
    file.close()

# raker_force("us", [125,4523,458,123])