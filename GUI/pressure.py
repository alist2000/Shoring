"""
Example code showing how to:
1) Define a symbolic embedment depth D for soil pressure distribution.
2) Create numeric arrays for a "temporary" guessed D so you can plot or integrate.
3) Combine the result with your existing surcharge distributions.

Author: <Your Name or Company>
"""

import sympy
import numpy as np
import math
from surcharge import Surcharge, PointSurcharge, StripSurcharge, LineSurcharge, UniformSurcharge, DepthDiscretization, \
    sum_surcharge_pressures

# If you have a separate file "surcharge.py" with these classes, import them:
# from surcharge import (DepthDiscretization, UniformSurcharge, PointSurcharge,
#                        LineSurcharge, StripSurcharge, sum_surcharge_pressures)
# For demonstration, I’ll just copy/paste your Surcharge classes below or assume they’re imported.

###############################################################################
# 1) Symbolic Setup for Soil Pressures
###############################################################################
z = sympy.Symbol('z', nonnegative=True, real=True)
D = sympy.Symbol('D', nonnegative=True, real=True)
# D is embedment depth we don’t know yet;
# we keep it symbolic for some expressions but might do numeric at times.

# Suppose the retained height is H:
H = 10.0  # example numeric: 10 ft (or meters, consistent units)

# Example: We define a piecewise function for active pressure Pa(z)
# Just for demonstration, let’s assume:
#   Pa(z) = Ka * gamma * z  for 0 <= z <= H
#   Pa(z) = Ka * gamma * H  for H < z <= H + D  (i.e., constant in embedment zone)
Ka = 0.33  # example active pressure coefficient
gamma = 120  # example soil unit weight, in lb/ft^3

Pa_expr = sympy.Piecewise(
    (Ka * gamma * z, (z >= 0) & (z <= H)),  # from top to bottom of retained
    (Ka * gamma * H, (z > H) & (z <= H + D)),  # in embedment zone
    (0, True)  # outside 0..(H+D), pressure=0
)

# Similarly, a piecewise function for passive pressure Pp(z).
# e.g., Pp(z) = Kp * gamma * (z - H) for H < z <= H + D,
# but 0 for z < H.
Kp = 3.0  # example passive coefficient
Pp_expr = sympy.Piecewise(
    (0, (z >= 0) & (z <= H)),  # no passive from 0..H
    (Kp * gamma * (z - H), (z > H) & (z <= H + D)),  # passive in embedment
    (0, True)
)

# Now the total “soil lateral pressure” might be:
#   Psoil(z) = Pa_expr - Pp_expr
#   or if you prefer to separate them or add them, it’s up to you:
Psoil_expr = Pa_expr - Pp_expr


###############################################################################
# 2) Converting the Symbolic Expression to a Numeric Array
###############################################################################
def discretize_soil_pressure(H, D_value, delta_z=0.1):
    """
    Given numeric H and a numeric D_value (e.g., a guess or final),
    returns arrays z_array, psoil_array for the total soil pressure
    from z=0 to z=H + D_value.

    Psoil_expr is the symbolic expression for active minus passive.
    """
    # total depth for the distribution
    z_max = H + D_value
    n_steps = int(math.ceil(z_max / delta_z))
    z_vals = np.linspace(0, z_max, n_steps + 1)

    # Evaluate the piecewise expression at each z
    p_vals = [float(Psoil_expr.subs({z: zz, D: D_value})) for zz in z_vals]

    return z_vals, p_vals


# Example usage (TEMPORARY numeric approach):
D_temp = 5.0  # e.g., we just assume embedment depth is 5 ft for demonstration
z_soil, p_soil = discretize_soil_pressure(H, D_temp)


# We now have an array of soil pressures from 0..(H + 5).


###############################################################################
# 3) Combine Soil Pressure with Surcharge Pressure
###############################################################################

# Let’s say we want to combine the soil array from z=0..(H+D)
# with a UniformSurcharge that also goes 0..(H+D).
# We have to be consistent with how we discretize surcharges:
#   * If surcharges originally code up from 0..H only,
#     we can “extend” them to 0..(H+D). Possibly by building a bigger array.

def combine_soil_and_surcharge(H, D_value, soil_z, soil_p, surcharges):
    """
    - H = retained height
    - D_value = numeric embedment (temp or final)
    - soil_z, soil_p = arrays from discretize_soil_pressure
    - surcharges = list of Surcharge objects (which might have a DepthDiscretization up to H + D_value)

    Returns combined arrays z_combined, p_combined.
    """

    # Build one DepthDiscretization for total depth (H + D_value)
    total_depth = H + D_value
    delta_h = soil_z[1] - soil_z[0] if len(soil_z) > 1 else 0.1
    disc = DepthDiscretization(total_depth, delta_h)

    # Evaluate / sum up surcharges
    if surcharges:
        surcharge_pressures = sum_surcharge_pressures(surcharges)
        # That yields array of same length as disc.depth
        # But we have soil_z and disc.depth possibly the same or slightly different
        # due to rounding. Let’s assume they match if we pick same delta.
        # If not, you can do interpolation.
    else:
        surcharge_pressures = np.zeros_like(disc.depth)

    # Interpolate soil pressure onto disc.depth if needed
    # Here we assume soil_z == disc.depth for simplicity.
    p_soil_interpolated = np.interp(disc.depth, soil_z, soil_p)
    shape1 = p_soil_interpolated.shape
    print(shape1)
    shape2 = surcharge_pressures.shape
    print(shape2)

    p_total = p_soil_interpolated + surcharge_pressures
    return disc.depth, p_total


###############################################################################
# 4) Demo Putting It All Together
###############################################################################
if __name__ == "__main__":
    # 1) Symbolic expressions exist for Psoil_expr with unknown D.
    #    For now, pick a numeric D_temp for demonstration:
    D_temp = 5.0
    surcharge_depth = 10
    # 2) Discretize soil pressure
    z_soil, p_soil = discretize_soil_pressure(H, D_temp, delta_z=0.5)
    # Now we have arrays for z=0..15 ft (since H=10, D_temp=5).

    # 3) Suppose we have a uniform surcharge of q=200 psf over 0..(H+D)
    disc_surch = DepthDiscretization(H + D_temp, delta_h=0.5)
    uniform_surch = PointSurcharge(disc_surch, q=200000.0, l=5, effective_depth=surcharge_depth)

    # 4) Combine soil + surcharge
    z_combined, p_combined = combine_soil_and_surcharge(
        H, D_temp,
        soil_z=z_soil,
        soil_p=p_soil,
        surcharges=[uniform_surch]
    )

    # 5) (Optional) Print or plot
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(p_soil, z_soil, label="Soil Pressure (Pa - Pp)")
    plt.plot(p_combined, z_combined, label="Soil + Surcharge")
    plt.gca().invert_yaxis()  # Depth downward
    plt.xlabel("Lateral Pressure (psf)")
    plt.ylabel("Depth (ft)")
    plt.legend()
    plt.title("Soil Pressure Distribution + Surcharge")
    plt.show()

    # Next steps: integrate p_combined(z) for force, shear, etc.
    # You can use your existing “integrate_lateral_pressure” function or similar.
