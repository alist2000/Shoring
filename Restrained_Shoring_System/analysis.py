import copy

import numpy as np
import scipy.integrate as spi

from plot import plotter_shear, plotter_moment, plotter_deflection


class analysis:
    def __init__(self, T, h1, depth, sigma, delta_h, unit_system):
        self.T = T  # for single just a number for multi it's a list.
        self.h1 = h1  # for single just h1 and for other  h_list_first.
        self.depth = depth
        self.sigma = sigma
        self.delta_h = delta_h
        self.unit_system = unit_system
        # count number of decimals
        delta_h_decimal = str(delta_h)[::-1].find('.')
        if delta_h_decimal == -1:
            delta_h_decimal = 0

        self.delta_h_decimal = delta_h_decimal

    def shear(self):
        T = self.T
        h1 = self.h1
        depth = self.depth
        sigma = self.sigma
        delta_h = self.delta_h
        unit_system = self.unit_system

        if unit_system == "us":
            load_unit = "lb"  # if unit of gama was pcf
            length_unit = "ft"
        else:
            load_unit = "N"  # if unit of gama was N/M^3
            length_unit = "m"

        shear_values = []
        for i in range(len(depth[:depth.index(h1)])):
            try:
                shear = spi.simpson(sigma[:i], depth[:i])
            except:
                shear = 0.0
            last_index = i
            shear_values.append(float(shear))

        shear_h1 = shear_values[-1] - T
        shear_values.append(float(shear_h1))
        for i in range(len(depth[depth.index(h1) + 1:])):
            try:
                shear = spi.simpson(sigma[last_index:i + last_index], depth[last_index:i + last_index]) + shear_h1
            except:
                shear = 0.0
            shear_values.append(float(shear))

        depth = np.array(depth)
        shear_values = np.array(shear_values)
        plot = plotter_shear(depth, shear_values, "V", "Z", load_unit, length_unit)
        return plot, shear_values

    def shear_multi(self):
        T = self.T
        h = self.h1
        depth = self.depth
        sigma = self.sigma
        delta_h = self.delta_h
        unit_system = self.unit_system

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
            last_index = depth.index(sum(h[:j + 1]))
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
        for i in range(len(depth[depth.index(sum(h[:-1])) + 1:])):
            try:
                shear = spi.simpson(sigma[first_index:i + first_index],
                                    depth[first_index:i + first_index]) + shear_values_end
            except:
                shear = 0.0
            shear_values.append(float(shear))

        depth = np.array(depth)
        shear_values = np.array(shear_values)
        plot = plotter_shear(depth, shear_values, "V", "Z", load_unit, length_unit)
        return plot, shear_values

    def moment(self, shear_values):
        depth = self.depth
        unit_system = self.unit_system
        if unit_system == "us":
            load_unit = "lb-ft"
            length_unit = "ft"
        else:
            load_unit = "N-m"
            length_unit = "m"
        moment_values = []
        for i in range(len(depth)):
            try:
                moment = spi.simpson(shear_values[:i], depth[:i])
            except:
                moment = 0
            moment_values.append(moment)
        moment_values[-1] = 0
        moment_values = np.array(moment_values)

        plot = plotter_moment(depth, moment_values, "M", "Z", load_unit, length_unit)

        return plot, moment_values

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

        # deflection in range 2
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
