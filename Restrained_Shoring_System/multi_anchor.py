import sys
from math import cos
import copy

import sympy.core.mul
from sympy import symbols
from sympy.solvers import solve
import numpy as np
from pressure import force_calculator, force_calculator_x, find_D, edit_sigma_and_height_general, water_pressure_detail


def multi_anchor(spacing, FS, h_list, ha, sigma_a, surcharge_pressure, force_active, arm_active, force_passive,
                 arm_passive, sigma_active, sigma_passive, water_started, force_active_water, arm_active_water,
                 water_force_passive,
                 water_arm_passive,
                 delta_h, unit_system):
    """
    h_list: heights between anchors. first value started from top of soil till first anchor and
        last value started from last anchor till excavation line.
    ha: depth of soil till excavation line. ( detail )
    sigma_a: soil pressure till excavation line. ( detail )
    surcharge_pressure: surcharge pressure till excavation line. ( detail )
    force_active: force of soil in loading side under excavation line.
    arm_active: arm of active force. started from top of soil. ( h + x*D )
    force_passive: force of soil in resisting side under excavation line.
    arm_passive: arm of passive force. started from top of soil in passive side. ( x*D )
    """
    D = symbols("D")

    delta_h_decimal = str(delta_h)[::-1].find('.')
    if delta_h_decimal == -1:
        delta_h_decimal = 0

    surcharge_pressure_copy = copy.deepcopy(surcharge_pressure)
    if type(surcharge_pressure) == int or type(surcharge_pressure) == float:
        sigma_a_copy = copy.deepcopy(sigma_a)
        surcharge_pressure = sigma_a_copy
        for i in range(len(surcharge_pressure)):
            surcharge_pressure[i] = 0

    # control water
    if water_started <= ha[-1]:
        water_pressure, force_active_water, arm_active_water = water_pressure_detail(ha, water_started, unit_system)
    else:
        water_pressure = np.zeros_like(ha)
        # we have no water pressure in this case

    ha = list(ha)
    h_list = list(h_list)
    anchor_number = len(h_list) - 1

    # cantilever span
    cantilever_index = ha.index(h_list[0]) + 1
    force_cantilever, arm_cantilever = force_calculator(ha[:cantilever_index], sigma_a[:cantilever_index])
    if surcharge_pressure != [0]:
        force_cantilever_su, arm_cantilever_su = force_calculator(ha[:cantilever_index],
                                                                  surcharge_pressure[:cantilever_index])
    else:
        force_cantilever_su, arm_cantilever_su = 0, 0
    force_cantilever_w, arm_cantilever_w = force_calculator(ha[:cantilever_index],
                                                            water_pressure[:cantilever_index])
    if type(surcharge_pressure_copy) == int or type(surcharge_pressure_copy) == float:
        arm_cantilever_su = 0
        force_cantilever_su = 0
    arm_cantilever = h_list[0] - arm_cantilever
    arm_cantilever_su = h_list[0] - arm_cantilever_su
    arm_cantilever_w = h_list[0] - arm_cantilever_w
    if force_cantilever_w == 0:
        arm_cantilever_w = 0
    M1 = force_cantilever * arm_cantilever + force_cantilever_su * arm_cantilever_su + force_cantilever_w * arm_cantilever_w
    T1_u = force_cantilever
    T_list = [[0, T1_u]]

    # interior span
    for i in range(anchor_number - 1):
        if i == 0:
            # fist part
            first_index = cantilever_index
            linker = round(h_list[0] + h_list[1], delta_h_decimal)
            last_index = ha.index(linker) + 1
            last_index_last = copy.deepcopy(last_index)
            force, arm = force_calculator(ha[first_index:last_index], sigma_a[first_index:last_index])
            if surcharge_pressure != [0]:
                force_su, arm_su = force_calculator(ha[first_index:last_index],
                                                    surcharge_pressure[first_index:last_index])
            else:
                force_su, arm_su = 0, 0
            force_w, arm_w = force_calculator(ha[first_index:last_index], water_pressure[first_index:last_index])

            if type(surcharge_pressure_copy) == int or type(surcharge_pressure_copy) == float:
                arm_su = 0
                force_su = 0
            T1_l = ((force_su + force + force_w) / 2) + (M1 / h_list[1])
            T2_u = ((force_su + force + force_w) / 2) - (M1 / h_list[1])
            T_list.append([T1_l, T2_u])
        else:
            # other parts
            first_index = last_index_last
            linker = round(sum(h_list[:i + 2]), delta_h_decimal)
            last_index = ha.index(linker) + 1
            force, arm = force_calculator(ha[first_index:last_index], sigma_a[first_index:last_index])
            if surcharge_pressure != [0]:
                force_su, arm_su = force_calculator(ha[first_index:last_index],
                                                    surcharge_pressure[first_index:last_index])
            else:
                force_su, arm_su = 0, 0
            force_w, arm_w = force_calculator(ha[first_index:last_index], water_pressure[first_index:last_index])
            if type(surcharge_pressure_copy) == int or type(surcharge_pressure_copy) == float:
                arm_su = 0
                force_su = 0
            T_u_l = ((force + force_su + force_w) / 2)  # u: upper layer for example T2 an l means lower of this layer
            T_l_u = ((force + force_su + force_w) / 2)  # l: lower layer for example T3 an u means upper of this layer
            T_list.append([T_u_l, T_l_u])
            last_index_last = copy.deepcopy(last_index)

    # embedment span
    # step1: calculate D and D0 ( FS = user defined and FS = 1 )
    first_index = last_index_last
    force_embedment, arm_embedment = force_calculator(ha[first_index:], sigma_a[first_index:])
    if surcharge_pressure != [0]:
        force_embedment_su, arm_embedment_su = force_calculator(ha[first_index:], surcharge_pressure[first_index:])
    else:
        force_embedment_su, arm_embedment_su = 0, 0
    # water pressure here has two part. 1) till excavation line 2) under that.
    # water pressure part one.
    force_embedment_w, arm_embedment_w = force_calculator(ha[first_index:], water_pressure[first_index:])

    if type(surcharge_pressure_copy) == int or type(surcharge_pressure_copy) == float:
        arm_embedment_su = 0
        force_embedment_su = 0
    arm_embedment = arm_embedment - sum(h_list[:-1])
    arm_embedment_su = arm_embedment_su - sum(h_list[:-1])
    arm_embedment_w = arm_embedment_w - sum(h_list[:-1])
    if force_embedment_w == 0:
        arm_embedment_w = 0
    for i in range(len(arm_active)):
        for j in range(len(arm_active[i])):
            arm_active[i][j] = arm_active[i][j] - sum(h_list[:-1])
    for i in range(len(arm_passive)):
        for j in range(len(arm_passive[i])):
            arm_passive[i][j] += h_list[-1]
    driving_force = []
    for i in force_active:
        for j in i:
            driving_force.append(j)
    driving_force += [force_embedment, force_embedment_su, force_embedment_w]
    driving_arm = []
    for i in arm_active:
        for j in i:
            driving_arm.append(j)
    driving_arm += [arm_embedment, arm_embedment_su, arm_embedment_w]
    resisting_force = []
    for i in force_passive:
        for j in i:
            resisting_force.append(j)
    resisting_arm = []
    for i in arm_passive:
        for j in i:
            resisting_arm.append(j)

    delta_h_decimal = str(delta_h)[::-1].find('.')
    if delta_h_decimal == -1:
        delta_h_decimal = 0

    if water_started <= ha[-1]:
        for i in force_active_water:
            for j in i:
                driving_force.append(j)

        for i in arm_active_water:
            for j in i:
                driving_arm.append(h_list[-1] + D - j)

        for i in water_force_passive:
            for j in i:
                resisting_force.append(j)

        for i in water_arm_passive:
            for j in i:
                resisting_arm.append(h_list[-1] + D - j)
    else:
        d = find_D(FS, resisting_force, resisting_arm, driving_force, driving_arm)
        d_0 = find_D(1, resisting_force, resisting_arm, driving_force, driving_arm)

        d = round(d, delta_h_decimal)
        d_0 = round(d_0, delta_h_decimal)

        if d > water_started - ha[-1]:
            for item in [driving_force, resisting_force, driving_arm, resisting_arm]:
                for i in range(len(item)):
                    if type(item[i]) == sympy.core.mul.Mul or type(item[i]) == sympy.core.add.Add:
                        item[i] = item[i].subs(D, D + (water_started - ha[-1]))
            for i in force_active_water:
                for j in i:
                    driving_force.append(j)

            for i in arm_active_water:
                for j in i:
                    driving_arm.append(h_list[-1] + D - j)

            for i in water_force_passive:
                for j in i:
                    resisting_force.append(j)

            for i in water_arm_passive:
                for j in i:
                    resisting_arm.append(h_list[-1] + D - j)

    d = find_D(FS, resisting_force, resisting_arm, driving_force, driving_arm)
    d_0 = find_D(1, resisting_force, resisting_arm, driving_force, driving_arm)

    d = round(d, delta_h_decimal)
    d_0 = round(d_0, delta_h_decimal)

    # step2: calculate force in last anchor with d_0
    # replace d0 in D for all values
    D = symbols("D")
    for item in [sigma_active, sigma_passive, resisting_force, resisting_arm, driving_force,
                 driving_arm]:
        for i in range(len(item)):
            if type(item[i]) == sympy.core.mul.Mul or type(item[i]) == sympy.core.add.Add:
                item[i] = item[i].subs(D, d_0)

    D_array, active_pressure_array = edit_sigma_and_height_general([sigma_active], [d_0], delta_h, d_0)
    D_array, passive_pressure_array = edit_sigma_and_height_general([sigma_passive], [d_0], delta_h, d_0)

    T_end_l = abs(sum(resisting_force) - sum(driving_force))
    T_list.append([T_end_l, 0])

    # edit force in anchors
    T_list_edited = []
    for i in range(len(T_list) - 1):
        item1 = float(T_list[i][1])
        item2 = float(T_list[i + 1][0])
        T_list_edited.append([item1, item2])

    # calculate final force in any anchor according to upper, lower and anchor spacing
    # NOTE: all anchor forces are horizontal.
    anchor_force = []
    for anchor in T_list_edited:
        force = sum(anchor) * spacing
        anchor_force.append(force)
    anchor_force = np.array(anchor_force)
    return d, d_0, anchor_force, sigma_active, sigma_passive, D_array, active_pressure_array, passive_pressure_array
