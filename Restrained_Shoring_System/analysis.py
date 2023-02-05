import copy
import sys
import json

from sympy import symbols
from sympy.solvers import solve
import numpy as np
import scipy.integrate as spi

from plot import plotter_shear, plotter_moment


class analysis:
    def __init__(self, T, h1, depth, sigma, delta_h, unit_system):
        self.T = T
        self.h1 = h1
        self.depth = depth
        self.sigma = sigma
        self.delta_h = delta_h
        self.unit_system = unit_system

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
