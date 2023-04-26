def surcharge_inputs(surcharge_type, q, l1, l2, teta, surcharge_depth, unit_system):
    surcharge_depth = round(surcharge_depth, 2)
    if unit_system == "us":
        length_unit = "ft"
        q_point = "lb"
        q_line = "lb/ft"
        q_strip = "lb/ft<sup>2</sup>"
    else:
        length_unit = "m"
        q_point = "lb"
        q_line = "N/m"
        q_strip = "N/m<sup>2</sup>"

    number_of_surcharge = 0
    for i in range(len(surcharge_type)):
        if surcharge_type[i] != "No Load":
            number_of_surcharge += 1

    table = f"""<tr>
            <td style="width: 25%;">
                <t1>Number of Surcharge Load:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{number_of_surcharge}</t2>
            </td>
            <td style="width: 25%;">
                <t1>Surcharge Depth:</t1>
            </td>
            <td style="width: 25%;">
                <t2>{surcharge_depth} {length_unit}</t2>
            </td>
        </tr>
        """
    for i in range(len(surcharge_type)):
        if surcharge_type[i] != "No Load":
            if "Point" in surcharge_type[i]:
                q_unit = q_point
            elif "Line" in surcharge_type[i]:
                q_unit = q_line
            else:
                q_unit = q_strip
            if l1[i] == "" or l1[i] is None:
                l1[i] = "-"

            if l2[i] == "" or l2[i] is None:
                l2[i] = "-"

            if teta[i] == "" or teta[i] is None:
                teta[i] = "-"
            table += f"""<tr>
                <td style="width: 25%;">
                    <t1>Load Type:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{surcharge_type[i]}</t2>
                </td>
                <td style="width: 25%;">
                    <t1>q:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{round(q[i], 2)} {q_unit}</t2>
                </td>
            </tr>
            <tr>
                <td style="width: 25%;">
                    <t1>L1:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{l1[i]} {length_unit}</t2>
                </td>
                <td style="width: 25%;">
                    <t1>L2:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{l2[i]} {length_unit}</t2>
                </td>
            </tr>
            <tr>
                <td style="width: 25%;">
                    <t1>&#952;:</t1>
                </td>
                <td style="width: 25%;">
                    <t2>{teta[i]} &deg;</t2>
                </td>
                <td style="width: 25%;">
                    <t1></t1>
                </td>
                <td style="width: 25%;">
                    <t2></t2>
                </td>
            </tr>"""

    if number_of_surcharge == 0:
        table += """<tr>
                <td style="width: 25%;">
                    <t1>There is No Surcharge Load.</t1>
                </td>
                
            </tr>"""

    # SURCHARGE FORMULA
    surcharge_type = [ "Uniform", "Point Load", "Line Load", "Strip Load"]
    surcharge_type_set = set(surcharge_type)
    surcharge_type_set.discard("No Load")
    table2 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script type="text/javascript" id="MathJax-script" async
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
    </script>
    <title>Document</title>
</head>
<body>"""
    for load in surcharge_type_set:
        if load == "Uniform":
            table2 += f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{ load }</th>
            </td>
        </tr>
        </tbody> </table>
        <table><tbody>
        <tr>
            <td>&#963;<sub>h</sub> = K<sub>a</sub> &#215; Q </td>
          </tr>
        <tr>
            <td style="text-align:center;"><img src="images/uniform_load.jpg" alt="UNIFORM LOAD"></td></tr>
        </tbody>
    </table>"""

        elif load == "Point Load":
            table2 += f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{ load }</th>
            </td>
        </tr> </tbody></table>""" + """<table><tbody><tr>
            <td style="text-align: left;">
                For m &#8804; 0.4:
                </td>
            </tr>
          <tr>
            <td>
                $$\sigma_h = 0.28{ {Q_p} \over {H^2}}{n^2 \over {(0.16 + n^2)^3} }.$$
                </td>
          </tr>
          <tr>
            <td style="text-align: left;">
                For m > 0.4:
                </td>
            </tr>
          <tr>
            <td >
                $$\sigma_h = 1.77{{Q_p} \over {H^2}}{n^2 m^2 \over {(m^2 + n^2)^3} }.$$
                </td>
          </tr>
          <tr>
            <td style="text-align:center;"><img src="images/point_load.jpg" alt="POINT LOAD"></td></tr>
        </tbody>
    </table>"""
        elif load == "Line Load":
                table2 += f"""<table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{ load } </th>
            </td>
        </tr>
        </tbody>
    </table>
    <table>
        <tbody>
        <tr>
            <td style="text-align: left;">
                For m &#8804; 0.4:
                </td>
            </tr>
          <tr> """ + """<td>
                $$\sigma_h = { {Q_l} \over {H}}{0.2 n \over {(0.16 + n^2)^2} }.$$
                </td>
          </tr>
          <tr>
            <td style="text-align: left;">
                For m > 0.4:
                </td>
            </tr>
          <tr>
            <td >
                $$\sigma_h = 1.28{{Q_l} \over {H}}{m^2 n \over {(m^2 + n^2)^2} }.$$
                </td>
          </tr>
          <tr>
            <td style="text-align:center;"><img src="images/line_load.jpg" alt="LINE LOAD"></td></tr>
        </tbody>
    </table>"""
        elif load == "Strip Load":
            table2 += f"""
            <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="text-align: left;">
                <th>Surcharge Type:{ load }</th>
            </td>
        </tr>
        </tbody>
    </table> """ + """<table>
        <tbody>
          <tr>
            <td>
                $$\sigma_h = { {2Q} \over {\pi}}{( \beta_R - \sin\beta\cos(2\alpha) )}.$$
                </td>
          </tr>
          <tr>
            <td style="text-align:center;"><img src="images/strip_load.jpg" alt="STRIP LOAD"></td></tr>
        </tbody>
    </table>"""
    table2 += """</body>
</html>"""

    file = open("reports/template/surcharge_input.html", "w")
    file.write(table)
    file.close()
    file = open("reports/template/surcharge_formula.html", "w")
    file.write(table2)
    file.close()


# surcharge_inputs(["Point Load", "Line Load"], [1000, 1500], [5, 3], [5, 3], [2, 3], 10, "us")


def load_distribution(unit_system, sigma_a, retaining_height, ht1=0, ht2=0):
    sigma_a = round(sigma_a, 2)
    retaining_height = round(retaining_height, 2)
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
                    <em>EFP<sub>a</sub></em>: {EFPa} {density_unit}
                </t2>
            </td>
            <td style="width: 35%;">
                <t2>
                    <em>EFP<sub>p</sub></em>: {EFPp} {density_unit}
                </t2>
            </td>
        </tr>
        </tbody>"""
    else:
        [ka, kp, gama, phi, beta_active, beta_passive, delta, c] = soil_prop
        for i in soil_prop:
            if i is None or i == "":
                i = 0
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


# Formula("Rankine", [0.56, 1.23, 135, 30, 0, 0, 0, 0], 10, "us")
# Formula("User Defined", [70, 190, 0.56, 0], 10, "us")

def racker_input(unit_system, racker_number, h_list):
    if unit_system == "us":
        length_unit = "ft"
    else:
        length_unit = "m"

    table = f"""<tbody>
            <tr>
                <td style="width: 25%;">
                    <t1>Number of Racker/Tieback:</t1>
                </td>
                <td style="width: 25%;">
                    <t2> {racker_number} </t2>
                </td>
                <td style="width: 25%;">
                </td>
                <td style="width: 25%;">
                </td>"""
    for i in range(racker_number):
        if i % 2 == 0:
            table += "</tr><tr>"
        table += f"""<td style="width: 25%;">
                    <t1>h{i + 1}:</t1>
                </td>
                <td style="width: 25%;">
                    <t2> {h_list[i]} {length_unit} </t2>
                </td>"""

    table += """</tr></tbody>"""
    file = open("reports/template/racker_prop.html", "w")
    file.write(table)
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
                <t1>R<sub>{i + 1}</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t2> {round(forces[i], 2)} {force_unit}</t2>
            </td>
    """
    table += """</tr></tbody>"""
    file = open("reports/template/raker_forces.html", "w")
    file.write(table)
    file.close()


# raker_force("us", [125,4523,458,123])
def section_deflection(unit_system, fy, section, A, Sx, Ix, V_max, M_max, deflection_max, allowable_deflection, number):
    deflection_max = round(deflection_max, 3)
    
    cross = section.find("X")
    part1 = section[:cross]
    part2 = section[cross + 1:]
    section = part1 + "&#215;" + part2
    if unit_system == "us":
        fb = round(M_max * 12 / (Sx * 1000), 2)
        fb_unit = "ksi"
        fv = round(V_max / (A * 1000), 2)
        fv_unit = "ksi"
        force_unit = "lb"
        moment_unit = "lb-ft"
        deflection_unit = "in"
        A_unit = "in<sup>2</sup>"
        s_unit = "in<sup>3</sup>"
        I_unit = "in<sup>4</sup>"
    else:
        fb = round(M_max * 1000 / Sx)
        fb_unit = "Mpa"
        fv = round(V_max / A, 2)
        fv_unit = "MPa"
        force_unit = "N"
        moment_unit = "N-m"
        deflection_unit = "mm"
        A_unit = "mm<sup>2</sup>"
        s_unit = "mm<sup>3</sup>"
        I_unit = "mm<sup>4</sup>"
    table = f"""<table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 100%;"><h3>5.8 Section Design</h3></td>
            </tr>
            </tbody>
        </table>
        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 25%;">
                    <b> Use: {section}:</b>
                </td>
                <td style="width: 25%;">
                    <t1> S<sub>x</sub> = {Sx} {s_unit}</t1>
                </td>
                <td style="width: 25%;">
                    <t1> I<sub>x</sub> = {Ix} {I_unit}</t1>
                </td>
                <td style="width: 25%;">
                    <t1> A = {A} {A_unit}</t1>
                </td>
            </tr>
            </tbody>
            </table>
            <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 50%;">
                    <t1> f<sub>v</sub>=V<sub>max</sub>/A ={fv} {fv_unit}</t1>
                </td>
                <td style="width: 50%;"></td>
            </tr>
            <tr>
                <td style="width: 30%;">
                    <t1> f<sub>v,max</sub>= 0.44 &#215; Fy = {0.44 * fy}</t1>
                </td>
                <td style="width: 70%;">
                    <b>{section} is satisfactory in shear</b>
                </td>
            </tr>
            <tr>
                <td style="width: 50%;">
                    <t1> f<sub>b</sub>=M<sub>max</sub>/S ={fb} {fb_unit}</t1>
                </td>
                <td style="width: 50%;"></td>
            </tr>
            <tr>
                <td style="width: 30%;">
                    <t1> f<sub>b,max</sub>= 0.66 &#215; Fy = {0.66 * fy}</t1>
                </td>
                <td style="width: 70%;">
                    <b>{section} is satisfactory in moment</b>
                </td>
            </tr>
            </tbody>
        </table>
        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 100%;"><h3>5.9 Deflection Check</h3></td>
            </tr>
            </tbody>
        </table>
        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="text-align: justify;text-justify: inter-word;">The deflection of the restrained soldier pile
                    is calculated using moment areas method, and the
                    corresponding deflection diagram is shown below.Considering the maximum allowable deflection
                    is <b>{allowable_deflection} {deflection_unit}</b>, section <b>{section}</b> satisfies the deflection criterion.
                    It should be noted that the point of fixity is assumed to be at <b>0.25D<sub>0</sub></b> below the
                    excavation line.
                </td>
            </tr>
            </tbody>
        </table>

        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 50%;">
                    <b> Deflection<sub>max</sub> = {deflection_max} {deflection_unit}
                    </b>
                </td>
                <td style="width: 50%;">
                </td>
            </tr>
            <tr>
                <td style="width: 100%; text-align: center;">
                    <img style="width: 100%; height: auto;  margin-top:0px;"
                         src="../plot/deflection_output{str(number)}.png"
                         alt="shear diagram">

            </tr>
            </tbody>
        </table>"""
        # image in server should be received with below source:
        # src="https://civision.balafan.com/restrained_shoring/plot/deflection_output{str(number)}"
    file = open(f"reports/template/section_deflection{number}.html", "w")
    file.write(table)
    file.close()


# section_deflection("us", 36, "W24×45", 12, 333, 1452, 45, 2366, 0.5, 0.6, 1)
def DCRs(DCR_moment, DCR_shear, DCR_deflection, DCR_lagging, lagging_status, number):
    DCR_moment = round(DCR_moment, 3)
    DCR_shear = round(DCR_shear, 3)
    DCR_deflection = round(DCR_deflection, 3)
    DCR_lagging = round(DCR_lagging, 3)
    moment_status = shear_status = deflection_status = "Pass"
    table = f"""<tr>
            <td style="width: 50%;">
                <t1b></t1b>
            </td>
            <td style="width: 20%; text-align: center;">
                <t1b>DCR</t1b>
            </td>
            <td style="width: 5%; text-align: center;">
                <t1b>Status</t1b>
            </td>
            <td style="width: 20%; text-align: center;">
                <t1b></t1b>
            </td>
            <td style="width: 5%; text-align: center;">
                <t1b></t1b>
            </td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Moment</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_moment}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{moment_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Shear</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_shear}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{shear_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Deflection</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_deflection}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{deflection_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>
        <tr>
            <td style="width: 50%;">
                <t1>Lagging (Moment Design)</t1>
            </td>
            <td style="width: 20%; text-align: center;">
                <t2>{DCR_lagging}</t2>
            </td>
            <td style="width: 5%; text-align: center;">{lagging_status}</td>
            <td style="width: 20%; text-align: center;">
                <t2></t2>
            </td>
            <td style="width: 5%; text-align: center;"></td>
        </tr>"""

    file = open(f"reports/template/DCRs{number}.html", "w")
    file.write(table)
    file.close()


# DCRs(0.56, 0.36, 0.98, 0.69, "PASSSSS")


def deflection_output(deflection_max, unit_system, number):
    deflection_max = round(deflection_max, 3)
    if unit_system == "us":
        deflection_unit = "in"
    else:
        deflection_unit = "mm"
    deflection_table2 = f"""<td style="width: 20%;">
                <t1b>Deflection Max</t1b>
            </td>
            <td style="width: 80%;">
                <t2>
                    {deflection_max} {deflection_unit}
                </t2>
            </td>"""

    # file = open("reports/template/deflection_dcr.html", "w")
    # file.write(deflection_table1)
    # file.close()

    file = open(f"reports/template/deflection_max{number}.html", "w")
    file.write(deflection_table2)
    file.close()


# deflection_output(0.5, 0.89, "us")


def lagging_output(unit_system, spacing, d_pile, lc, ph, R, M_max, S_req, timber_size, S_sup, lagging_status, number):
    M_max = round(M_max, 0)
    S_req = round(S_req, 3)
    S_sup = round(S_sup, 3)
        
    if unit_system == "us":
        length_unit = "ft"
        density_unit = "pcf"
        force_unit = "lb"
        Sx_unit = "in<sup>3</sup>"
        moment_unit = "lb-ft"

    else:
        length_unit = "m"
        density_unit = "N/m<sup>3</sup>"
        force_unit = "N"
        Sx_unit = "mm<sup>3</sup>"
        moment_unit = "N-m"

    table = f"""<table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 25%;">
                <t1> Tieback/Racker Spacing:</t1>
            </td>
            <td style="width: 25%;">
                <t1> {spacing} {length_unit}</t1>
            </td>
            <td style="width: 25%;">
                <t1> d<sub>pile</sub></t1>
            </td>
            <td style="width: 25%;">
                <t1> {d_pile} {length_unit}</t1>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1> L<sub>c</sub>:</t1>
            </td>
            <td style="width: 25%;">
                <t1> {lc} {length_unit}</t1>
            </td>
            <td style="width: 25%;">
                <t1> PH<sub>Max</sub></t1>
            </td>
            <td style="width: 25%;">
                <t1> {ph} {density_unit}</t1>
            </td>
        </tr>
        <tr>
            <td style="width: 25%;">
                <t1> R = 0.5 &#215; (PH &#215;L<sub>c</sub>/2):</t1>
            </td>
            <td style="width: 25%;">
                <t1> {R} {force_unit}</t1>
            </td>
            <td style="width: 25%;">
                <t1> M<sub>Max</sub></t1>
            </td>
            <td style="width: 25%;">
                <t1> {M_max} {moment_unit}</t1>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 100%;">
                <t1> S<sub>required</sub>= M<sub>max</sub>/F<sub>b</sub>= {S_req} {Sx_unit}</t1>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%; background: #dfe3e6">
        <tbody>
        <tr>
            <td style="width: 15%;">
                <t1>Try</t1>
            </td>
            <td style="width: 85%;">
                <t2>{timber_size} :
                </t2>
            </td>
        </tr>
        </tbody>
    </table>
    <table border="0" style="border-collapse: collapse; width: 100%;">
        <tbody>
        <tr>
            <td style="width: 100%;">
                <t1> S<sub>supplied</sub> = {S_sup} {Sx_unit}</t1>
            </td>
        </tr>
        <tr>
            <td style="width: 100%;">
                <t1> Timber Moment Design: <b>{lagging_status}</b></t1>
            </td>
        </tr>
        </tbody>
    </table>"""
    file = open(f"reports/template/lagging_output{number}.html", "w")
    file.write(table)
    file.close()
