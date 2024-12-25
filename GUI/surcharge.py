import numpy as np
import scipy.integrate as spi
import math


class DepthDiscretization:
    """
    Helper class to manage a depth array from 0 to H with a chosen delta_h.

    Parameters
    ----------
    H : float
        Total height (or depth) in consistent units.
    delta_h : float, optional
        Increment in the depth array. Defaults to 0.1 or less if
        user-supplied value is too large or invalid.

    Attributes
    ----------
    H : float
        The positive total depth.
    depth : np.ndarray
        The array of discrete depth values from 0 to H.

    Raises
    ------
    ValueError
        If H <= 0 or user-supplied delta_h is invalid.
    """

    def __init__(self, H: float, delta_h: float = 0.1):
        if H <= 0:
            raise ValueError("Depth 'H' must be > 0.")
        if delta_h <= 0 or delta_h > H:
            # Provide a fallback if user gives invalid delta_h
            delta_h = 0.1

        self.H = float(H)

        # Build depth array with uniform increments
        steps = int(math.ceil(self.H / delta_h))
        self.depth = np.linspace(0, self.H, steps + 1, endpoint=True)

    def normalized_depth(self) -> np.ndarray:
        """
        Returns an array of dimensionless depth 'n = z/H'.
        """
        return self.depth / self.H


class Surcharge:
    """
    Abstract base class for different surcharge types.
    """

    def __init__(self, discretization: DepthDiscretization):
        self.discretization = discretization

    def get_pressure_distribution(self) -> np.ndarray:
        """
        Returns an array of the same length as self.discretization.depth
        representing the lateral pressure at each depth.

        Subclasses must implement this method.
        """
        raise NotImplementedError


class UniformSurcharge(Surcharge):
    """
    Uniform Surcharge over the entire depth.
    The lateral pressure is constant = q.
    """

    def __init__(self, discretization: DepthDiscretization, q: float, effective_depth):
        super().__init__(discretization)
        self.q = abs(q)  # in psf or consistent unit
        if effective_depth == 0:
            self.effective_depth = max(self.discretization.depth)
        else:
            self.effective_depth = abs(effective_depth)
    def get_pressure_distribution(self) -> np.ndarray:
        depth_array = self.discretization.depth
        # Pressure is constant with depth
        sigma_h = []

        for z in depth_array:
            if z > self.effective_depth:
                sigma_h.append(0)
            else:
                sigma_h.append(self.q)

        return np.array(sigma_h, dtype=float)


class PointSurcharge(Surcharge):
    """
    Point Surcharge at some horizontal distance l from the wall.
    Optionally an angle theta in degrees.

    Uses formulas from (like your original code) to compute sigma_h at each depth.
    """

    def __init__(self, discretization: DepthDiscretization, q: float, l: float, theta_deg: float = 0.0,
                 effective_depth: float = 0.0):
        super().__init__(discretization)
        self.q = abs(q)
        self.l = abs(l)
        self.theta = math.radians(theta_deg)  # convert to radians
        if effective_depth == 0:
            self.effective_depth = max(self.discretization.depth)
        else:
            self.effective_depth = abs(effective_depth)
    def get_pressure_distribution(self) -> np.ndarray:
        H = self.discretization.H
        depth = self.discretization.depth  # e.g. array from 0..H
        n = depth / H  # dimensionless depth

        sigma_h = []
        m = self.l / H
        for i, z in enumerate(depth):
            if z == 0.0 or z > self.effective_depth:
                # at surface (z=0), no pressure
                sigma_h.append(0.0)
            else:
                if m <= 0.4:
                    val = 0.28 * self.q * (n[i] ** 2) / (H ** 2 * (0.16 + n[i] ** 2) ** 3)
                else:
                    val = 1.77 * self.q * (n[i] ** 2) * (m ** 2) / (H ** 2 * ((m ** 2) + (n[i] ** 2)) ** 3)
                # angle factor
                if self.theta != 0.0:
                    val *= math.cos(1.1 * self.theta) ** 2
                sigma_h.append(val)

        return np.array(sigma_h, dtype=float)


class LineSurcharge(Surcharge):
    """
    Line Surcharge of magnitude q at some distance l from the wall (like your code).
    """

    def __init__(self, discretization: DepthDiscretization, q: float, l: float, effective_depth: float = 0.0):
        super().__init__(discretization)
        self.q = abs(q)
        self.l = abs(l)
        if effective_depth == 0:
            self.effective_depth = max(self.discretization.depth)
        else:
            self.effective_depth = abs(effective_depth)
    def get_pressure_distribution(self) -> np.ndarray:
        H = self.discretization.H
        depth = self.discretization.depth
        n = depth / H
        m = self.l / H

        sigma_h = []
        for i, z in enumerate(depth):
            if z == 0.0 or z > self.effective_depth:
                sigma_h.append(0.0)
            else:
                if m <= 0.4:
                    val = 0.2 * self.q * n[i] / (H * (0.16 + n[i] ** 2) ** 2)
                else:
                    val = 1.28 * self.q * n[i] * (m ** 2) / (H * ((m ** 2) + n[i] ** 2) ** 2)
                sigma_h.append(val)

        return np.array(sigma_h, dtype=float)


class StripSurcharge(Surcharge):
    """
    Strip Surcharge between distances l1 and l2 from the wall,
    magnitude q. (From your original formula.)

    If l2 < l1 is passed, automatically swap them.
    """

    def __init__(self, discretization: DepthDiscretization, q: float, l1: float, l2: float,
                 effective_depth: float = 0.0):
        super().__init__(discretization)
        self.q = abs(q)
        if effective_depth == 0:
            self.effective_depth = max(self.discretization.depth)
        else:
            self.effective_depth = abs(effective_depth)

        if l1 > l2:
            l1, l2 = l2, l1
        self.l1 = l1
        self.l2 = l2
        self.a = self.l2 - self.l1

    def get_pressure_distribution(self) -> np.ndarray:
        if abs(self.a) < 1e-6:
            # effectively zero strip
            return np.zeros_like(self.discretization.depth, dtype=float)

        H = self.discretization.H
        depth = self.discretization.depth

        sigma_h = []
        for z in depth:
            if z == 0 or z > self.effective_depth:
                sigma_h.append(0.0)
            else:
                alpha = math.atan((self.l1 + self.a / 2.0) / z)
                teta1 = math.atan(self.l1 / z)
                teta2 = math.atan(self.l2 / z)
                beta = teta2 - teta1
                val = 2.0 * self.q * (beta - math.sin(beta) * math.cos(2.0 * alpha)) / math.pi
                sigma_h.append(val if val >= 0 else 0.0)
        return np.array(sigma_h, dtype=float)


def sum_surcharge_pressures(surcharges) -> np.ndarray:
    """
    Given a list of Surcharge objects, returns the sum
    of their pressure distributions at each depth.
    """
    if not surcharges:
        return np.array([])

    # Get the depth discretization from the first surcharge
    depth = surcharges[0].discretization.depth
    total = np.zeros_like(depth, dtype=float)

    for s in surcharges:
        total += s.get_pressure_distribution()

    return total


def integrate_lateral_pressure(depth: np.ndarray, pressure: np.ndarray):
    """
    Returns total lateral force (area under p-z curve) and
    the depth of the resultant (centroid) from the top.
    """
    # Force
    F = spi.simps(pressure, depth)  # or np.trapz(pressure, depth)
    # Centroid
    M = spi.simps(pressure * depth, depth)
    if abs(F) < 1e-9:
        return 0.0, 0.0
    centroid = M / F
    return F, centroid


import plotly.graph_objects as go
import numpy as np


def create_soil_pressure_plot(z, pressure, z_r, p_r):
    """
    Creates a soil lateral pressure diagram (0-10 ft depth)
    and saves the figure as a PNG.
    """
    # ------------------------------------------
    # 1) Example Data
    # ------------------------------------------
    # Depth from 0 (top) to 10 ft (bottom)
    # z = np.linspace(0, 10, 50)
    # Some imaginary lateral pressure in psf (just for demonstration)
    # Let's create a curve that grows from ~1.5 psf at top down to ~1.0 psf near 2 ft
    # and then up to ~1.7 psf at 10 ft to mimic a non-linear shape
    #     pressure = 1.5 - 0.5*np.exp(-0.3*z) + 0.2*np.sin(z/2)

    # "Resultant" (illustrative): Suppose it’s at z_r = 4 ft, p_r = 1.5 psf

    # ------------------------------------------
    # 2) Build Figure
    # ------------------------------------------
    fig = go.Figure()

    # Plot the pressure curve as a "fill"
    fig.add_trace(go.Scatter(
        x=pressure,  # X-axis is horizontal pressure (psf)
        y=z,  # Y-axis is depth (ft)
        mode='lines',
        fill='tozerox',  # fill area under the curve toward x=0
        fillcolor='lightsteelblue',
        line=dict(color='black', width=2),
        name='Soil Pressure'
    ))

    # ------------------------------------------
    # 3) Format Axes & Layout
    # ------------------------------------------
    # Reverse the y-axis so 0 is at top
    fig.update_yaxes(autorange="reversed")
    # X-axis range: start at 0, leave some room beyond max(pressure)
    x_max = max(pressure) + 0.2
    fig.update_xaxes(range=[0, x_max])

    fig.update_layout(
        title="Soil Lateral Pressure Diagram",
        xaxis_title="Pressure (psf)",
        yaxis_title="Depth z (ft)",
        template="simple_white",
        width=600,
        height=700
    )

    # ------------------------------------------
    # 4) Add Annotations / Arrows
    # ------------------------------------------
    # Example: Arrow marking the resultant depth
    fig.add_annotation(
        x=1.1 * max(pressure),
        y=z_r,
        ax=1.1 * max(pressure) + 0.6,  # adjust arrow length
        ay=z_r,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        arrowhead=2,
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor="red",
        text="",  # no text at arrow head
    )
    # Label "Zr" near that point
    fig.add_annotation(
        x=0.8 * max(pressure),
        y=z_r / 2,
        text=f"Zr = {round(z_r, 1)}",
        showarrow=False,
        font=dict(color="red", size=12)
    )
    # Another arrow from the curve to the left, labeling "Pr" or similar
    fig.add_annotation(
        x=0.2,
        y=z_r,
        ax=1.1 * max(pressure),  # left side
        ay=z_r,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        arrowhead=2,
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor="red",
        text="",
    )
    # Another arrow from the curve to the left, labeling "Pr" or similar
    fig.add_annotation(
        x=0.7 * max(pressure),
        y=z_r,
        ax=0.7 * max(pressure),  # left side
        ay=0,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        arrowhead=1,
        arrowsize=1.2,
        arrowwidth=1,
        arrowcolor="red",
        text="",
    )
    fig.add_annotation(
        x=1.1 * max(pressure) / 2,
        y=z_r + 0.2,  # small offset
        text=f"Pr = {round(p_r, 1)}",
        showarrow=False,
        font=dict(color="red", size=12)
    )

    # ------------------------------------------
    # 5) Save as PNG and Show
    # ------------------------------------------
    # Save the figure as PNG (requires kaleido or orca)
    fig.write_image("final_plot.png", width=600, height=700)
    fig.write_html("final_plot.html")
    # Now display in interactive window
    # fig.show()


if __name__ == "__main__":
    # 1) Create a depth discretization for H=10 ft
    discretization = DepthDiscretization(H=10.0, delta_h=0.1)

    # 2) Create some surcharge objects
    point = PointSurcharge(discretization, q=10000.0, l=7.0, theta_deg=30)
    line = LineSurcharge(discretization, q=12000.0, l=5.0)

    # 3) Sum them up
    total_pressure = sum_surcharge_pressures([line, point])

    # 4) Integrate for net force & centroid
    F, centroid = integrate_lateral_pressure(discretization.depth, total_pressure)

    print(f"Total Lateral Force = {F:.2f} lb/ft (if psf * ft used)")
    print(f"Resultant Depth from Top = {centroid:.2f} ft")

    # # 5) (Optional) Plot the distribution
    create_soil_pressure_plot(discretization.depth, total_pressure, centroid, F)
    print("Plot saved as 'final_plot.png' and shown in an interactive window.")

    # import matplotlib.pyplot as plt
    #
    # plt.plot(total_pressure, discretization.depth, label="Combined Surcharge")
    # plt.gca().invert_yaxis()  # Depth downward
    # plt.xlabel("Lateral Pressure (psf)")
    # plt.ylabel("Depth (ft)")
    # plt.legend()
    # plt.show()
