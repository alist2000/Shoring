def surcharge_inputs(surcharge_type, q, l1, l2, teta, retaining_height, unit_system):
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
                <t2>{retaining_height} {length_unit}</t2>
            </td>
        </tr>
        """
    for i in range(len(surcharge_type)):
        if surcharge_type[i] != "No Load":
            number_of_surcharge += 1
            if "Point" in surcharge_type[i]:
                q_unit = q_point
            elif "Line" in surcharge_type[i]:
                q_unit = q_line
            else:
                q_unit = q_strip
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
                    <t2>{q[i]} {q_unit}</t2>
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
    file = open("reports/template/surcharge_input.html", "w")
    file.write(table)
    file.close()


# surcharge_inputs(["Point Load", "Line Load"], [1000, 1500], [5, 3], [5, 3], [2, 3], 10, "us")


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
                <t2> {forces[i]} {force_unit}</t2>
            </td>
    """
    table += """</tr></tbody>"""
    file = open("reports/template/raker_forces.html", "w")
    file.write(table)
    file.close()


# raker_force("us", [125,4523,458,123])
def section_deflection(unit_system, fy, section, A, Sx, Ix, V_max, M_max, deflection_max, allowable_deflection, number):
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
                    <t1> Use: {section}:</t1>
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
                    <t1>{section} is satisfactory in shear</t1>
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
                    <t1>{section} is satisfactory in moment</t1>
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
                    is {allowable_deflection}, section {section} satisfies the deflection criterion.
                    It should be noted that the point of fixity is assumed to be at 0.25D<sub>0</sub> below the
                    excavation line.
                </td>
            </tr>
            </tbody>
        </table>

        <table border="0" style="border-collapse: collapse; width: 100%;">
            <tbody>
            <tr>
                <td style="width: 50%;">
                    <t1> Deflection<sub>max</sub> = {deflection_max}
                    </t1>
                </td>
                <td style="width: 50%;">
                </td>
            </tr>
            <tr>
                <td style="width: 100%; text-align: center;">
                    <img style="width: 100%; height: auto;  margin-top:0px;"
                         src="https://civision.balafan.com/restrained_shoring/plot/deflection_output{str(number)}"
                         alt="shear diagram">

            </tr>
            </tbody>
        </table>"""
    file = open("reports/template/section_deflection.html", "w")
    file.write(table)
    file.close()


# section_deflection("us", 36, "W24×45", 12, 333, 1452, 45, 2366, 0.5, 0.6, 1)
def DCRs(DCR_moment, DCR_shear, DCR_deflection, DCR_lagging, lagging_status):
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

    file = open("reports/template/DCRs.html", "w")
    file.write(table)
    file.close()


# DCRs(0.56, 0.36, 0.98, 0.69, "PASSSSS")


def deflection_output(deflection_max, unit_system):
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

    file = open("reports/template/deflection_max.html", "w")
    file.write(deflection_table2)
    file.close()


# deflection_output(0.5, 0.89, "us")


def lagging_output(unit_system, spacing, d_pile, lc, ph, R, M_max, S_req, timber_size, S_sup, lagging_status):
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
                <t1> Timber Moment Design: {lagging_status}</t1>
            </td>
        </tr>
        </tbody>
    </table>"""
    file = open("reports/template/lagging_output.html", "w")
    file.write(table)
    file.close()
