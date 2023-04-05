import copy

import numpy as np
import scipy.integrate as spi

from Lagging import lagging_design
from plot import plotter_shear, plotter_moment, plotter_deflection
from report import create_feather


def find_max(z, value):
    first = abs(value[0])
    second = abs(value[1])
    if first >= second:
        return value[0], z[0]
    else:
        return value[1], z[1]


class analysis:
    def __init__(self, T, h1, depth, sigma, delta_h, unit_system, project_number):
        self.T = T  # for single just a number for multi it's a list.
        self.h1 = h1  # for single just h1 and for other  h_list_first.
        self.depth = depth
        self.sigma = sigma
        self.delta_h = delta_h
        self.unit_system = unit_system
        self.project_number = project_number
        # count number of decimals
        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        self.delta_h_decimal = delta_h_decimal

        if unit_system == "us":
            deflection_unit = "in"
            length_unit = "ft"
        else:
            deflection_unit = "mm"
            length_unit = "m"

        self.deflection_unit = deflection_unit
        self.length_unit = length_unit

    def shear(self):
        T = self.T
        h1 = self.h1
        depth = self.depth
        sigma = self.sigma
        delta_h = self.delta_h
        unit_system = self.unit_system
        project_number = self.project_number

        if unit_system == "us":
            load_unit = "lb"  # if unit of gama was pcf
            length_unit = "ft"
        else:
            load_unit = "N"  # if unit of gama was N/M^3
            length_unit = "m"

        shear_values = np.zeros_like(depth)
        h1_index = depth.index(h1)
        for i, d in enumerate(depth[:h1_index + 1]):
            if i == 0:
                shear_values[i] = 0
            else:
                shear_values[i] = np.trapz(sigma[:i], depth[:i])

        shear_h1 = shear_values[h1_index] - T
        shear_values[h1_index] = shear_h1
        for i, d in enumerate(depth[h1_index + 1:]):
            j = i + h1_index
            if i == 0:
                shear_values[j] = shear_h1
            else:
                shear_values[j] = np.trapz(sigma[h1_index:i + h1_index], depth[h1_index:i + h1_index]) + shear_h1

        V_max = np.abs(shear_values).max()
        Y_zero_load_index = np.argmax(np.abs(shear_values))
        Y_zero_load = depth[Y_zero_load_index]

        create_feather(depth, shear_values, "Shear", "shear_project" + str(project_number))

        plot = plotter_shear(depth, shear_values, "V", "Z", load_unit, length_unit)
        depth, shear_values = control_index_for_plot(depth, shear_values)
        return plot, shear_values, V_max, Y_zero_load

    def shear_multi(self):
        T = self.T
        h = self.h1
        depth = self.depth
        sigma = self.sigma
        delta_h = self.delta_h
        unit_system = self.unit_system
        delta_h_decimal = self.delta_h_decimal
        project_number = self.project_number

        if unit_system == "us":
            load_unit = "lb"  # if unit of gama was pcf
            length_unit = "ft"
        else:
            load_unit = "N"  # if unit of gama was N/M^3
            length_unit = "m"

        anchor_number = len(h) - 1
        first_index = 0
        shear_h1 = 0
        shear_values = []
        for j in range(anchor_number):
            linker = round(sum(h[:j + 1]), delta_h_decimal)
            last_index = depth.index(linker)
            for i in range(len(depth[first_index:last_index])):
                try:
                    shear = spi.simpson(sigma[first_index:i + first_index],
                                        depth[first_index:i + first_index]) + shear_h1
                except:
                    shear = 0.0
                shear_values.append(float(shear))
            first_index = copy.deepcopy(last_index) + 1
            shear_h1 = shear_values[-1] - T[j]
            shear_values.append(float(shear_h1))

        shear_values_end = shear_values[-1]
        link = round(sum(h[:-1]), delta_h_decimal)
        for i in range(len(depth[depth.index(link) + 1:])):
            try:
                shear = spi.simpson(sigma[first_index:i + first_index],
                                    depth[first_index:i + first_index]) + shear_values_end
            except:
                shear = 0.0
            shear_values.append(float(shear))

        V_max = max(max(shear_values), abs(min(shear_values)))
        try:
            Y_zero_load_index = shear_values.index(V_max)
            Y_zero_load = depth[Y_zero_load_index]
        except:
            Y_zero_load_index = shear_values.index(-V_max)
            Y_zero_load = depth[Y_zero_load_index]

        depth = np.array(depth)
        shear_values = np.array(shear_values)

        plot = plotter_shear(depth, shear_values, "V", "Z", load_unit, length_unit)
        create_feather(depth, shear_values, "Shear", "shear_project" + str(project_number))
        depth, shear_values = control_index_for_plot(depth, shear_values)
        return plot, shear_values, V_max, Y_zero_load

    import numpy as np

    import numpy as np

    def moment(self, shear_values):
        depth = self.depth
        unit_system = self.unit_system
        project_number = self.project_number

        if unit_system == "us":
            load_unit = "lb-ft"
            length_unit = "ft"
        else:
            load_unit = "N-m"
            length_unit = "m"

        moment_values = np.zeros_like(depth)
        moment_values[1:] = np.cumsum(shear_values[:-1] * np.diff(depth))

        M_max = np.max(np.abs(moment_values))
        Y_zero_shear_index = np.argmax(np.abs(moment_values))
        Y_zero_shear = depth[Y_zero_shear_index]

        create_feather(depth, moment_values, "Moment", "moment_project" + str(project_number))
        plot = plotter_moment(depth, moment_values, "M", "Z", load_unit, length_unit)
        depth, moment_values = control_index_for_plot(depth, moment_values)
        return plot, moment_values, M_max, Y_zero_shear

    def deflection_single(self, moment, d, h1):
        """
        moment: contain moment value. started from top of pile to tip of pile ( last value -> in embedment depth )
        deflection from last anchor to tip of pile is exactly like unrestrained shoring.
        step1: calculate delta c/b.
        step2: calculate delta x/b in two ranges. ( or three )
        """
        depth = self.depth
        delta_h = self.delta_h
        delta_h_decimal = self.delta_h_decimal

        h_total = round(depth[-1], delta_h_decimal)
        # calculate PoF
        PoF = 0.25 * d  # started from excavation line
        PoF_form_top = h_total - d + PoF  # started from top
        PoF = round(PoF, delta_h_decimal)
        PoF_form_top = round(PoF_form_top, delta_h_decimal)

        # range 1: A-B --> anchor to top of pile
        h1_list = np.arange(0, h1 + delta_h, delta_h)
        AB = h1_list
        AB_list = list(copy.deepcopy(AB))

        # range 2: B-C --> anchor to PoF
        BC_length = round(PoF_form_top - h1, delta_h_decimal)  # PoF_form_top - h1: length of BC
        BC = np.arange(0, BC_length + delta_h, delta_h)
        BC_list = list(copy.deepcopy(BC))

        # range 3: C-D --> PoF to End
        CD_length = h_total - PoF_form_top + delta_h  # h_total - PoF_form_top: length of CD
        CD = np.arange(0, CD_length, delta_h)
        CD_list = list(copy.deepcopy(CD))
        del CD_list[0]
        CD = np.array(CD_list)

        # point indexes
        A_index = len(depth) - 1
        B_index = depth.index(h1)
        C_index = depth.index(PoF_form_top)
        D_index = 0  # tip of pile

        # calculate delta c/b
        area_cb = abs(spi.simpson(moment[C_index:B_index:-1], depth[C_index:B_index:-1]))
        X_cb = abs(spi.simpson(moment[C_index:B_index:-1] * BC[:],
                               depth[C_index:B_index:-1])) / area_cb
        delta_cb = area_cb * X_cb  # unit : if us --> lb - ft^3. if metric --> N - m^3

        # deflection in range 1
        deflection1 = []
        x_point_moment_last = copy.deepcopy(B_index)
        for x in AB:
            x_point = AB_list.index(x)
            if x == 0:
                delta_xb = 0.
            else:
                delta_xb = abs(spi.simpson(moment[x_point_moment_last:B_index] * AB[:x_point],
                                           depth[x_point_moment_last:B_index]))
            x_point_moment_last -= 1

            deflection1.append(delta_xb)  # start B end A --> Ok

        # deflection in range 2
        deflection2 = []
        x_point_moment_last = copy.deepcopy(B_index)
        for x in BC:
            x_point = BC_list.index(x)
            # if x == 0:
            #     delta_xb = 0.  # this part is not necessary ( number of index )
            # else:
            if x != 0:
                delta_xb = abs(spi.simpson(moment[x_point_moment_last:B_index:-1] * BC[:x_point],
                                           depth[x_point_moment_last:B_index:-1]))
                deflection2.append(delta_xb)  # start B end C --> should be reversed --> convert to: start C end B
            x_point_moment_last += 1

        # deflection in range 3
        deflection3 = []
        x_point_moment_last = copy.deepcopy(C_index)
        for x in CD:
            x_point = CD_list.index(x)
            # if x == 0:
            #     delta_xb = 0.  # this part is not necessary ( number of index )
            # else:
            if x_point != 0:
                delta_xb = abs(
                    spi.simpson(moment[x_point_moment_last:B_index:-1] * np.array(list(BC) + list(CD[:x_point])),
                                depth[x_point_moment_last:B_index:-1]))
                deflection3.append(delta_xb)  # start C end D --> should be reversed --> convert to: start D end C

            x_point_moment_last += 1

        # Add last value for deflection.
        delta_xb = abs(spi.simpson(moment[x_point_moment_last:B_index - 1:-1] * np.array(list(BC) + list(CD[:])),
                                   depth[x_point_moment_last:B_index - 1:-1]))
        deflection3.append(delta_xb)

        deflection = []
        '''NOTE: length of deflection 1 and 3 are equal to length of AB and CD but
           length of deflection 2 = len(BC) - 1 because first zero in ignored.'''
        for i in range(len(deflection1)):
            deflection1[i] = -(deflection1[i] + delta_cb * AB_list[i] / BC_length)

        del BC_list[0]
        for i in range(len(deflection2)):
            deflection2[i] = -(deflection2[i] - delta_cb * BC_list[i] / BC_length)

        for i in range(len(deflection3)):
            deflection3[i] = -(-deflection3[i] + delta_cb * (BC_length + CD_list[i]) / BC_length)

        deflection2.reverse()  # now started from C to B

        deflection3.reverse()  # now started from D to C

        deflection += list(deflection3) + list(deflection2) + list(deflection1)
        deflection.reverse()
        deflection_array = np.array(deflection)
        deflection = plotter_deflection(depth, deflection_array, 'x_title', 'y_title', 'x_unit', 'y_unit')

    def deflection_single2(self, moment, d, h1):
        """
        moment: contain moment value. started from top of pile to tip of pile ( last value -> in embedment depth )
        deflection from last anchor to tip of pile is exactly like unrestrained shoring.
        step1: calculate delta c/b.
        step2: calculate delta x/b in two ranges. ( or three )
        """
        depth = self.depth
        delta_h = self.delta_h
        delta_h_decimal = self.delta_h_decimal

        h_total = round(depth[-1], delta_h_decimal)
        # calculate PoF
        PoF = 0.25 * d  # started from excavation line
        PoF_form_top = h_total - d + PoF  # started from top
        PoF = round(PoF, delta_h_decimal)
        PoF_form_top = round(PoF_form_top, delta_h_decimal)

        # range 1: A-B --> anchor to top of pile
        h1_list = np.arange(0, h1 + delta_h, delta_h)
        AB = h1_list
        AB_list = list(copy.deepcopy(AB))

        # range 2: B-C --> anchor to PoF
        BC_length = round(PoF_form_top - h1, delta_h_decimal)  # PoF_form_top - h1: length of BC
        BC = np.arange(0, BC_length + delta_h, delta_h)
        BC_list = list(copy.deepcopy(BC))

        # # range 3: C-D --> PoF to End
        CD_length = round(h_total - PoF_form_top, delta_h_decimal)  # h_total - PoF_form_top: length of CD
        CD = np.arange(0, CD_length + delta_h, delta_h)
        CD_list = list(copy.deepcopy(CD))
        # # del CD_list[0]
        # # CD = np.array(CD_list)

        BD = np.arange(0, BC_length + CD_length + delta_h, delta_h)
        BD_list = list(copy.deepcopy(BD))

        # point indexes
        A_index = len(depth) - 1
        B_index = depth.index(h1)
        C_index = depth.index(PoF_form_top)
        D_index = 0  # tip of pile

        # calculate delta c/b
        area_cb = abs(spi.simpson(moment[C_index:B_index:-1], depth[C_index:B_index:-1]))
        X_cb = abs(spi.simpson(moment[C_index:B_index:-1] * BC[:],
                               depth[C_index:B_index:-1])) / area_cb
        delta_cb = area_cb * X_cb  # unit : if us --> lb - ft^3. if metric --> N - m^3

        # deflection in range 1
        deflection1 = []
        x_point_moment_last = copy.deepcopy(B_index)
        for x in AB:
            x_point = AB_list.index(x)
            if x == 0:
                delta_xb = 0.
            else:
                delta_xb = abs(spi.simpson(moment[x_point_moment_last:B_index] * AB[:x_point],
                                           depth[x_point_moment_last:B_index]))
            x_point_moment_last -= 1

            deflection1.append(delta_xb)  # start B end A --> Ok

        # deflection in range 2, 3
        deflection2 = []
        x_point_moment_last = copy.deepcopy(B_index)
        for x in BD:
            x_point = BD_list.index(x)
            # if x == 0:
            #     delta_xb = 0.  # this part is not necessary ( number of index )
            # else:
            if x != 0:
                delta_xb = abs(spi.simpson(moment[x_point_moment_last:B_index:-1] * BD[:x_point],
                                           depth[x_point_moment_last:B_index:-1]))
                deflection2.append(delta_xb)  # start B end C --> should be reversed --> convert to: start C end B
            x_point_moment_last += 1

        C_index_deflection = BD_list.index(BC_length)
        deflection2_edited = []
        for i in deflection2[:C_index_deflection]:
            deflection2_edited.append(i)
        deflection3 = []
        for i in deflection2[C_index_deflection:]:
            deflection3.append(i)
        deflection = []
        '''NOTE: length of deflection 1 and 3 are equal to length of AB and CD but
           length of deflection 2 = len(BC) - 1 because first zero in ignored.'''
        for i in range(len(deflection1)):
            deflection1[i] = -(deflection1[i] + delta_cb * AB_list[i] / BC_length)

        del BC_list[0]
        for i in range(len(deflection2_edited)):
            deflection2_edited[i] = -(deflection2_edited[i] - delta_cb * BC_list[i] / BC_length)

        for i in range(len(deflection3)):
            deflection3[i] = -(-deflection3[i] + delta_cb * (BC_length + CD_list[i]) / BC_length)

        deflection2_edited.reverse()  # now started from C to B

        deflection3.reverse()  # now started from D to C

        deflection += list(deflection3) + list(deflection2_edited) + list(deflection1)
        deflection.reverse()
        deflection_array = np.array(deflection)
        deflection = plotter_deflection(depth, deflection_array, 'x_title', 'y_title', 'x_unit', 'y_unit')

    def deflection_single3(self, moment, d, h1):
        """
        moment: contain moment value. started from top of pile to tip of pile ( last value -> in embedment depth )
        deflection from last anchor to tip of pile is exactly like unrestrained shoring.
        step1: calculate delta c/b.
        step2: calculate delta x/b in two ranges. ( or three )
        """
        depth = self.depth
        delta_h = self.delta_h
        delta_h_decimal = self.delta_h_decimal
        deflection_unit = self.deflection_unit
        length_unit = self.length_unit

        h_total = round(depth[-1], delta_h_decimal)
        # calculate PoF
        PoF = 0.25 * d  # started from excavation line
        PoF_form_top = h_total - d + PoF  # started from top
        PoF = round(PoF, delta_h_decimal)
        PoF_form_top = round(PoF_form_top, delta_h_decimal)

        # range 1: A-B --> anchor to top of pile
        h1_list = np.arange(0, h1 + delta_h, delta_h)
        AB = h1_list
        AB_list = list(copy.deepcopy(AB))

        # range 2: B-C --> anchor to PoF
        BC_length = round(PoF_form_top - h1 + delta_h, delta_h_decimal)  # PoF_form_top - h1: length of BC
        BC = np.arange(0, BC_length, delta_h)
        BC_list = list(copy.deepcopy(BC))

        # # range 3: C-D --> PoF to End
        CD_length = round(h_total - PoF_form_top + delta_h, delta_h_decimal)  # h_total - PoF_form_top: length of CD
        CD = np.arange(0, CD_length, delta_h)
        CD_list = list(copy.deepcopy(CD))
        # # del CD_list[0]
        # # CD = np.array(CD_list)

        AC = np.arange(0, BC_length + h1, delta_h)
        AC_list = list(copy.deepcopy(AC))

        # point indexes
        A_index = len(depth) - 1
        B_index = depth.index(h1)
        C_index = depth.index(PoF_form_top)
        D_index = 0  # tip of pile

        # calculate delta c/b
        area_cb = abs(spi.simpson(moment[C_index:B_index:-1], depth[C_index:B_index:-1]))
        X_cb = abs(spi.simpson(moment[C_index:B_index:-1] * BC[:],
                               depth[C_index:B_index:-1])) / area_cb
        delta_cb = area_cb * X_cb  # unit : if us --> lb - ft^3. if metric --> N - m^3

        # calculate delta b/c
        area_bc = abs(spi.simpson(moment[B_index: C_index], depth[B_index:C_index]))
        X_bc = abs(spi.simpson(moment[B_index: C_index] * BC[:],
                               depth[B_index:C_index])) / area_bc
        delta_bc = area_bc * X_bc  # unit : if us --> lb - ft^3. if metric --> N - m^3

        # # deflection in range 1
        # deflection1 = []
        # x_point_moment_last = copy.deepcopy(B_index)
        # for x in AB:
        #     x_point = AB_list.index(x)
        #     if x == 0:
        #         delta_xb = 0.
        #     else:
        #         delta_xb = abs(spi.simpson(moment[x_point_moment_last:B_index] * AB[:x_point],
        #                                    depth[x_point_moment_last:B_index]))
        #     x_point_moment_last -= 1
        #
        #     deflection1.append(delta_xb)  # start B end A --> Ok

        # deflection in range 1, 2
        deflection1_2 = []
        x_point_moment_last = copy.deepcopy(C_index)
        for x in AC:
            x_point = AC_list.index(x)
            if x == 0:
                delta_xb = 0.  # this part is not necessary ( number of index )
            else:
                delta_xb = abs(spi.simpson(moment[x_point_moment_last:C_index] * AC[:x_point],
                                           depth[x_point_moment_last:C_index]))
            deflection1_2.append(delta_xb)  # start B end C --> should be reversed --> convert to: start C end B
            x_point_moment_last -= 1

        # deflection in range 3
        deflection3 = []
        x_point_moment_last = copy.deepcopy(C_index)
        for x in CD:
            x_point = CD_list.index(x)
            # if x == 0:
            #     delta_xb = 0.  # this part is not necessary ( number of index )
            # else:
            if x_point != 0:
                delta_xb = abs(
                    spi.simpson(moment[x_point_moment_last:C_index:-1] * (CD[:x_point]),
                                depth[x_point_moment_last:C_index:-1]))
                deflection3.append(delta_xb)  # start C end D --> should be reversed --> convert to: start D end C

            x_point_moment_last += 1

        # Add last value for deflection.
        try:
            delta_xb = abs(spi.simpson(moment[x_point_moment_last:C_index - 1:-1] * (CD[:]),
                                       depth[x_point_moment_last:C_index - 1:-1]))
        except:  # sometimes we got index error
            delta_xb = deflection3[-1]

        deflection3.append(delta_xb)

        deflection_list = []
        '''NOTE: length of deflection 1 and 3 are equal to length of AB and CD but
           length of deflection 2 = len(BC) - 1 because first zero in ignored.'''
        # for i in range(len(deflection1)):
        #     deflection1[i] = -(deflection1[i] + delta_cb * AB_list[i] / BC_length)

        del BC_list[0]
        for i in range(len(deflection1_2)):
            deflection1_2[i] = -(-deflection1_2[i] + delta_bc * AC_list[i] / BC_length)

        for i in range(len(deflection3)):
            deflection3[i] = -(deflection3[i] - delta_bc * (CD_list[i]) / BC_length)

        # deflection2.reverse()  # now started from C to B

        deflection3.reverse()  # now started from D to C

        deflection_list += list(deflection3) + list(deflection1_2)
        deflection_list.reverse()
        deflection_array = np.array(deflection_list)
        # deflection = plotter_deflection(depth, deflection_array, 'Deflection', 'z', deflection_unit, length_unit)
        max1 = max(deflection_array)
        x1 = deflection_list.index(max1)

        max2 = min(deflection_array)
        x2 = deflection_list.index(max1)
        max_deflection, z_max = find_max([x1, x2], [max1, max2])
        z_max = depth[z_max]

        depth, deflection_array = control_index_for_plot(depth, deflection_array)

        return deflection_array, z_max, abs(max_deflection)

    def deflection_multi(self, moment, d, h):
        """
        h1: sum(h list first except last one.)
        moment: contain moment value. started from top of pile to tip of pile ( last value -> in embedment depth )
        deflection from last anchor to tip of pile is exactly like unrestrained shoring.
        step1: calculate delta c/b.
        step2: calculate delta x/b in two ranges. ( or three )
        """
        depth = self.depth
        delta_h = self.delta_h
        delta_h_decimal = self.delta_h_decimal
        deflection_unit = self.deflection_unit
        length_unit = self.length_unit

        h_total = round(depth[-1], delta_h_decimal)
        # calculate PoF
        PoF = 0.25 * d  # started from excavation line
        PoF_form_top = h_total - d + PoF  # started from top
        PoF = round(PoF, delta_h_decimal)
        PoF_form_top = round(PoF_form_top, delta_h_decimal)

        anchor_number = len(h) - 1

        # range 1: A-B --> anchor to top of pile
        h1_list = np.arange(0, h[0] + delta_h, delta_h)
        AB_first = h1_list
        AB_list_first = list(copy.deepcopy(AB_first))

        # range 2: B-C --> anchor to PoF
        BC_length_first = round(h[1], delta_h_decimal)  # PoF_form_top - h1: length of BC
        BC_first = np.arange(0, BC_length_first, delta_h)
        BC_list_first = list(copy.deepcopy(BC_first))
        BC_list_first.insert(len(BC_list_first) - 1, BC_first[-1] + delta_h)
        BC_first = np.array(BC_list_first)

        AC_length_first = round(sum(h[:2]) + delta_h, delta_h_decimal)
        AC_first = np.arange(0, AC_length_first, delta_h)
        AC_list_first = list(copy.deepcopy(AC_first))

        # point indexes
        A_index_first = len(depth) - 1
        B_index_first = depth.index(h[0])
        C_index_first = depth.index(AC_length_first)
        D_index_first = 0  # tip of pile

        # calculate delta b/c
        area_bc_first = abs(spi.simpson(moment[B_index_first: C_index_first], depth[B_index_first:C_index_first]))
        X_bc_first = abs(spi.simpson(moment[B_index_first: C_index_first] * BC_first[:],
                                     depth[B_index_first:C_index_first])) / area_bc_first
        delta_bc_first = area_bc_first * X_bc_first  # unit : if us --> lb - ft^3. if metric --> N - m^3

        # deflection in range 1, 2
        deflection1_2 = []
        deflection_first = []
        x_point_moment_last = copy.deepcopy(C_index_first)
        for x in AC_first:
            x_point = AC_list_first.index(x)
            if x == 0:
                delta_xb_first = 0.  # this part is not necessary ( number of index )
            else:
                delta_xb_first = abs(spi.simpson(moment[x_point_moment_last:C_index_first] * AC_first[:x_point],
                                                 depth[x_point_moment_last:C_index_first]))
            delta_xb_first = -(-delta_xb_first + delta_bc_first * AC_list_first[x_point] / BC_length_first)
            deflection_first.append(
                delta_xb_first)  # start B end C --> should be reversed --> convert to: start C end B
            x_point_moment_last -= 1
        deflection_first.reverse()
        deflection1_2 += deflection_first

        B_index_mid = C_index_first
        deflection_mid = []
        for i in range(anchor_number - 1):
            if i == (anchor_number - 2):
                BC_length_mid = round(h[i + 2] + PoF + delta_h, delta_h_decimal)
                BC_mid = np.arange(0, BC_length_mid, delta_h)
                BC_list_mid = list(copy.deepcopy(BC_mid))

                # point indexes
                # C_index_mid = depth.index(sum(h[:i + 3]) + PoF)
                C_index_mid = B_index_mid + len(BC_mid) - 2
            else:
                BC_length_mid = round(h[i + 2] + delta_h, delta_h_decimal)
                BC_mid = np.arange(0, BC_length_mid, delta_h)
                BC_list_mid = list(copy.deepcopy(BC_mid))

                # point indexes
                # C_index_mid = depth.index(sum(h[:i + 3]))
                C_index_mid = B_index_mid + len(BC_mid) - 2

            # calculate delta b/c
            area_bc_mid = abs(spi.simpson(moment[B_index_mid: C_index_mid + 1], depth[B_index_mid:C_index_mid + 1]))
            X_bc_mid = abs(spi.simpson(moment[B_index_mid: C_index_mid + 1] * BC_mid[1:],
                                       depth[B_index_mid:C_index_mid + 1])) / area_bc_mid
            delta_bc_mid = area_bc_mid * X_bc_mid  # unit : if us --> lb - ft^3. if metric --> N - m^3

            x_point_moment_last = copy.deepcopy(C_index_mid)
            for x in BC_mid:
                x_point = BC_list_mid.index(x)
                if x != 0:
                    #     delta_xb_mid = 0.  # this part is not necessary ( number of index )
                    # else:
                    delta_xb_mid = abs(spi.simpson(moment[x_point_moment_last:C_index_mid] * BC_mid[:x_point],
                                                   depth[x_point_moment_last:C_index_mid]))
                    delta_xb_mid = -(-delta_xb_mid + delta_bc_mid * BC_list_mid[x_point] / BC_length_mid)
                    deflection_mid.append(
                        delta_xb_mid)  # start B end C --> should be reversed --> convert to: start C end B
                x_point_moment_last -= 1
            deflection_mid_copy = copy.deepcopy(deflection_mid)
            deflection_mid_copy.reverse()
            deflection_mid.clear()
            deflection1_2 += deflection_mid_copy
            if i == (anchor_number - 2):
                # range 3: C-D --> PoF to End
                CD_length_last = round(d - PoF + delta_h, delta_h_decimal)  # h_total - PoF_form_top: length of CD
                CD_last = np.arange(0, CD_length_last, delta_h)
                CD_list_last = list(copy.deepcopy(CD_last))
                # deflection in range 3
                deflection3 = []
                x_point_moment_last = copy.deepcopy(C_index_mid)
                for x in CD_last:
                    x_point = CD_list_last.index(x)
                    if x_point != 0:
                        delta_xb_last = abs(
                            spi.simpson(moment[x_point_moment_last:C_index_mid:-1] * (CD_last[:x_point]),
                                        depth[x_point_moment_last:C_index_mid:-1]))
                        delta_xb_last = -(delta_xb_last - delta_bc_mid * CD_list_last[x_point] / BC_length_mid)

                        deflection3.append(
                            delta_xb_last)  # start C end D --> should be reversed --> convert to: start D end C

                    x_point_moment_last += 1

                # Add
                delta_xb_last = abs(
                    spi.simpson(moment[x_point_moment_last:C_index_mid:-1] * (CD_last[:]),
                                depth[x_point_moment_last:C_index_mid:-1]))
                delta_xb_last = -(delta_xb_last - delta_bc_mid * CD_list_last[x_point] / BC_length_mid)

                deflection3.append(
                    delta_xb_last)  # start C end D --> should be reversed --> convert to: start D end C
                # deflection3.reverse()  # now started from D to C

            B_index_mid = copy.deepcopy(C_index_mid) + 1

        deflection_list = []
        '''NOTE: length of deflection 1 and 3 are equal to length of AB and CD but
           length of deflection 2 = len(BC) - 1 because first zero in ignored.'''

        deflection_list += list(deflection1_2) + list(deflection3)
        # deflection.reverse()
        deflection_array = np.array(deflection_list)
        # deflection = plotter_deflection(depth, deflection_array, 'Deflection', "z", deflection_unit, length_unit)

        max1 = max(deflection_array)
        x1 = deflection_list.index(max1)

        max2 = min(deflection_array)
        x2 = deflection_list.index(max1)
        max_deflection, z_max = find_max([x1, x2], [max1, max2])
        z_max = depth[z_max]

        depth, deflection_array = control_index_for_plot(depth, deflection_array)

        return deflection_array, z_max, abs(max_deflection)

    def final_deflection_and_lagging(self, deflection_values, final_sections, E, Pile_spacing, ph, timber_size, Fb,
                                     unit_system):
        depth = self.depth
        deflection_unit = self.deflection_unit
        length_unit = self.length_unit
        project_number = self.project_number

        final_deflections = []
        deflection_plot_list = []
        max_deflection_list = []
        DCR_lagging = []
        status_lagging = []
        d_concrete_list = []
        h_list = []
        bf_list = []
        tw_list = []
        tf_list = []

        for section_number, item in enumerate(final_sections, start=1):
            section, Ix, section_area, Sx, wc, h, bf, tw, tf = item.values()
            if section and Ix:
                # E: Ksi , M: lb.ft , Ix: in^4 / E: Mpa , M: N.m , Ix: mm^4
                EI = E * (1000 * float(Ix) / 12 ** 3 if unit_system == "us" else float(Ix) * 10 ** 9)

                deflection_copy = [d / EI for d in deflection_values]
                max_deflection = max(max(deflection_copy), abs(min(deflection_copy)))
                max_deflection_list.append(max_deflection)
                final_deflections.append(deflection_copy)

                # lagging control
                lagging = lagging_design(unit_system, Pile_spacing, section, ph, timber_size)
                DCR_moment_timber, status, d_concrete = lagging.moment_design(Fb, tw, 1.25, 1.1, 1.1)
                DCR_lagging.append(DCR_moment_timber)
                status_lagging.append(status)
                d_concrete_list.append(d_concrete)

                create_feather(depth, deflection_copy, "Deflection",
                               f"Deflection_project" + str(project_number) + "_section{section_number}")
                deflection_plot = plotter_deflection(depth, deflection_copy, 'Deflection', "z", deflection_unit,
                                                     length_unit)
                deflection_plot_list.append(deflection_plot)

                h_list.append(h)
                bf_list.append(bf)
                tw_list.append(tw)
                tf_list.append(tf)

        return final_deflections, max_deflection_list, deflection_plot_list, DCR_lagging, status_lagging, d_concrete_list, h_list, bf_list, tw_list, tf_list


# OpenAI code: NOTE: first version has error I edit.
def DCR_calculator(max_deflection, allowable_deflection, Sx, S_required, A, A_required):
    DCR_deflection = [max_def / allowable_deflection for max_def in max_deflection]
    DCR_shear = [A_required / A_val for A_val in A]
    DCR_moment = [S_required / Sx_val for Sx_val in Sx]

    return DCR_deflection, DCR_shear, DCR_moment


def control_index_for_plot(depth, pressure):
    pressure = list(pressure)
    len_depth = len(depth)
    len_pressure = len(pressure)
    while len_depth != len_pressure:
        if len_depth > len_pressure:
            pressure.append(pressure[-1])
        elif len_depth < len_pressure:
            del pressure[-1]
        len_pressure = len(pressure)

    return depth, pressure
