"""
input.py

Responsible for:
1. Collecting all necessary GUI inputs (in a structured data object).
2. Computing soil & surcharge pressures (independent of shoring type).
3. Instantiating the appropriate shoring calculation class for embedment depth D.
4. Returning final results (e.g., total pressure array, D, etc.).

Author: Your Name / Company
"""

from __future__ import annotations
from typing import List, Dict, Any, Protocol, Optional
import math


# ---------------------------------------------------------------------------
# 1) Data Transfer Objects (DTOs) - Single Responsibility
#    These classes simply hold the data, no business logic.
# ---------------------------------------------------------------------------

class GeneralInfoData:
    """
    DTO for general project info (Title, Job No, etc.).
    """

    def __init__(self,
                 title: str,
                 job_no: str,
                 designer: str,
                 checker: str,
                 company: str,
                 client: str,
                 unit: str,
                 date: str,
                 comment: str):
        self.title = title
        self.job_no = job_no
        self.designer = designer
        self.checker = checker
        self.company = company
        self.client = client
        self.unit = unit
        self.date = date
        self.comment = comment


class GeneralPropertiesData:
    """
    DTO for general engineering properties (FS, E, Pile Spacing, Fy, etc.).
    """

    def __init__(self,
                 fs: float,
                 E: float,
                 pile_spacing: float,
                 fy: float,
                 allowable_deflection: float,
                 section_name: str):
        self.fs = fs
        self.E = E
        self.pile_spacing = pile_spacing
        self.fy = fy
        self.allowable_deflection = allowable_deflection
        self.section_name = section_name


class SoilLayerData:
    """
    DTO for individual soil-layer properties.
    """

    def __init__(self,
                 height: float,
                 properties: Dict[str, float]):
        # e.g., "properties" might contain: {'γ': 120, 'φ': 30, 'c': 0, ...}
        self.height = height
        self.properties = properties


class SoilProfileData:
    """
    DTO for entire soil profile (multiple layers + water table info + theory).
    """

    def __init__(self,
                 theory_name: str,
                 layers: List[SoilLayerData],
                 has_water: bool,
                 water_depth: float):
        self.theory_name = theory_name
        self.layers = layers
        self.has_water = has_water
        self.water_depth = water_depth

    @property
    def total_height(self) -> float:
        """Sum of all layer heights (retaining height)."""
        return sum(layer.height for layer in self.layers)


class SupportData:
    """
    DTO for a single support (Raker or Anchor).
    """

    def __init__(self, distance_from_top: float):
        self.distance_from_top = distance_from_top


class GeometricalSoilData:
    """
    DTO wrapping the soil profile + shoring type + optional supports.
    """

    def __init__(self,
                 shoring_type: str,  # e.g., "Cantilever", "Raker", "Anchor"
                 angle: float,  # angle for rakers/anchors
                 supports: List[SupportData],
                 soil_profile: SoilProfileData):
        self.shoring_type = shoring_type
        self.angle = angle
        self.supports = supports
        self.soil_profile = soil_profile


class SurchargeLoadData:
    """
    DTO for a single surcharge load (type + properties).
    """

    def __init__(self,
                 load_type: str,  # "Uniform", "Point Load", ...
                 properties: Dict[str, float]):
        self.load_type = load_type
        self.properties = properties


class SurchargeData:
    """
    DTO for the entire surcharge profile (loads + Ka_surcharge, etc.).
    """

    def __init__(self,
                 ka_surcharge: float,
                 loads: List[SurchargeLoadData]):
        self.ka_surcharge = ka_surcharge
        self.loads = loads


class LaggingData:
    """
    DTO for lagging (ph_max, fb, timber size, etc.).
    """

    def __init__(self,
                 ph_max: float,
                 fb: float,
                 timber_size: str):
        self.ph_max = ph_max
        self.fb = fb
        self.timber_size = timber_size


class GUIData:
    """
    Consolidates all data from the GUI into one place:
      - General Info
      - General Properties
      - Geometrical/Soil
      - Surcharge
      - Lagging
    """

    def __init__(self,
                 general_info: GeneralInfoData,
                 general_props: GeneralPropertiesData,
                 geo_soil: GeometricalSoilData,
                 surcharge: SurchargeData,
                 lagging: LaggingData):
        self.general_info = general_info
        self.general_props = general_props
        self.geo_soil = geo_soil
        self.surcharge = surcharge
        self.lagging = lagging


# ---------------------------------------------------------------------------
# 2) Interfaces / Protocols for Calculation
#    (Dependency Inversion: we depend on abstractions, not concretions)
# ---------------------------------------------------------------------------

class ISoilPressureCalculator(Protocol):
    """
    Defines the contract for calculating soil pressures
    (active + passive) ignoring surcharges.
    """

    def calculate_soil_pressure(self, geo_soil: GeometricalSoilData) -> List[float]:
        """
        Returns a 1D array of soil lateral pressures at discrete depth points.
        (Or more elaborate data structure if needed.)
        """
        ...


class ISurchargeCalculator(Protocol):
    """
    Defines the contract for combining surcharge loads into a single lateral pressure distribution.
    """

    def calculate_surcharge_pressure(self, surcharge_data: SurchargeData, total_depth: float) -> List[float]:
        ...


class IEmbedmentCalculator(Protocol):
    """
    Defines the contract for calculating embedment depth D based on the total pressure distribution.
    """

    def calculate_embedment_depth(self, total_pressure: List[float]) -> float:
        """
        Return the final embedment depth D (units consistent with input).
        """
        ...


# ---------------------------------------------------------------------------
# 3) Concrete Implementations for Soil Pressure & Surcharge
#    (Single Responsibility: each class just does one type of calculation)
# ---------------------------------------------------------------------------

class SimpleSoilPressureCalculator:
    """
    Example class that calculates a naive distribution of
    (Active - Passive) from 0..H + guessed D.

    In a real design, you'd replace with your real code (Rankine, Coulomb, etc.).
    """

    def __init__(self, guessed_embedment: float = 5.0, dz: float = 0.5):
        """
        guessed_embedment: a temporary numeric guess for D.
        dz: discretization step for pressure arrays.
        """
        self._D_temp = guessed_embedment
        self._dz = dz

    def calculate_soil_pressure(self, geo_soil: GeometricalSoilData) -> List[float]:
        # 1) total retaining height
        H = geo_soil.soil_profile.total_height

        # 2) We'll do a simple approach: from z=0..H+D
        z_max = H + self._D_temp

        # 3) build a numeric distribution (we'll do a naive approach)
        num_points = int(math.ceil(z_max / self._dz)) + 1
        # We store the result in a list of pressures (or you might want pairs of (z, p))
        pressures = []
        for i in range(num_points):
            z = i * self._dz
            # dummy formula:
            # active part: Pa = Ka*g*z from 0..H (capped at Ka*g*H from H..H+D)
            # passive part: Pp from H..H+D
            # Combine them into net pressure
            Ka = 0.33  # example
            Kp = 3.0  # example
            gamma = 120.0  # psf/ft, example

            if z <= H:
                Pa = Ka * gamma * z
                Pp = 0
            else:
                Pa = Ka * gamma * H
                # passive from H..(H+D)
                Pp = Kp * gamma * (z - H)

            net = Pa - Pp  # could be negative below H if Pp > Pa
            pressures.append(net)

        return pressures


class SimpleSurchargeCalculator:
    """
    Example calculator that sums all surcharge loads into a
    single lateral pressure distribution from 0..(H + guessed D).
    """

    def __init__(self, guessed_embedment: float = 5.0, dz: float = 0.5):
        self._D_temp = guessed_embedment
        self._dz = dz

    def calculate_surcharge_pressure(self, surcharge_data: SurchargeData, total_depth: float) -> List[float]:
        """
        We do a dummy uniform approach or could integrate your existing Surcharge classes.
        For demonstration, we assume each load is uniform and just sum them.
        """
        num_points = int(math.ceil(total_depth / self._dz)) + 1
        total_surch = [0.0] * num_points

        for load in surcharge_data.loads:
            if load.load_type == "Uniform":
                q_val = load.properties.get("q", 0)
                # Just add q_val to all points
                for i in range(num_points):
                    total_surch[i] += q_val
            # else if "Point Load", "Line Load", etc., do real logic or call existing classes

        return total_surch


# ---------------------------------------------------------------------------
# 4) Factory for Shoring-based Embedment Calculation
#    (Open/Closed: easily add new types, e.g. "SheetPileCalculator", etc.)
# ---------------------------------------------------------------------------

class CantileverEmbedmentCalculator(IEmbedmentCalculator):
    def calculate_embedment_depth(self, total_pressure: List[float]) -> float:
        """
        Some formula or iterative approach.
        We'll do a dummy 'average pressure' approach for demonstration.
        """
        avg_press = sum(total_pressure) / len(total_pressure) if total_pressure else 0
        # e.g., D might be a function of average pressure
        return 5.0 + 0.01 * avg_press  # TOTALLY made-up logic for demonstration


class RakerEmbedmentCalculator(IEmbedmentCalculator):
    def calculate_embedment_depth(self, total_pressure: List[float]) -> float:
        # Different logic for Raker
        return 4.0  # dummy


class AnchorEmbedmentCalculator(IEmbedmentCalculator):
    def calculate_embedment_depth(self, total_pressure: List[float]) -> float:
        # Different logic for Anchor
        return 3.5  # dummy


class ShoringEmbedmentFactory:
    """
    Simple factory to return the appropriate embedment calculator
    based on string shoring_type.
    """

    @staticmethod
    def get_calculator(shoring_type: str) -> IEmbedmentCalculator:
        shoring_type = shoring_type.lower()
        if shoring_type == "cantilever":
            return CantileverEmbedmentCalculator()
        elif shoring_type == "raker":
            return RakerEmbedmentCalculator()
        elif shoring_type == "anchor":
            return AnchorEmbedmentCalculator()
        else:
            # fallback or raise
            raise ValueError(f"Unknown shoring type: {shoring_type}")


# ---------------------------------------------------------------------------
# 5) CalculationManager - Orchestrates the entire flow (Single Responsibility)
#    This is typically called when the user clicks "Calculate" in the GUI.
# ---------------------------------------------------------------------------

class CalculationManager:
    """
    Orchestrates:
    1) Gathering input data from GUIData
    2) Creating / calling soil pressure + surcharge calculators
    3) Summing results
    4) Using ShoringEmbedmentFactory to get D
    5) Returning final results
    """

    def __init__(self,
                 soil_calc: ISoilPressureCalculator,
                 surcharge_calc: ISurchargeCalculator):
        """
        We inject the calculators, ensuring we depend on abstractions
        (D in SOLID: Dependency Inversion).
        """
        self.soil_calc = soil_calc
        self.surcharge_calc = surcharge_calc

    def run_calculation(self, gui_data: GUIData) -> Dict[str, Any]:
        """
        Main method invoked on "Calculate" button.
        Returns a dictionary of final results (pressures, D, etc.).
        """

        # 1) Gather geometry info
        geo_soil = gui_data.geo_soil
        H = geo_soil.soil_profile.total_height

        guessed_D = 5.0  # We might guess 5 ft or gather from user or an iteration

        # 2) Get soil pressure array
        soil_pressures = self.soil_calc.calculate_soil_pressure(geo_soil)

        # 3) For surcharges, we need the total depth = H + guessed_D or we can do more advanced iteration
        total_depth = H + guessed_D
        surcharge_pressures = self.surcharge_calc.calculate_surcharge_pressure(gui_data.surcharge, total_depth)

        # 4) Combine arrays
        if len(soil_pressures) != len(surcharge_pressures):
            # In real code, handle mismatch by interpolation or rebuilding arrays.
            # For simplicity, assume same length now:
            min_len = min(len(soil_pressures), len(surcharge_pressures))
            soil_pressures = soil_pressures[:min_len]
            surcharge_pressures = surcharge_pressures[:min_len]

        total_pressure = [s + sc for (s, sc) in zip(soil_pressures, surcharge_pressures)]

        # 5) Call the factory for embedment
        embedment_calculator = ShoringEmbedmentFactory.get_calculator(geo_soil.shoring_type)
        final_D = embedment_calculator.calculate_embedment_depth(total_pressure)

        # You might do a second pass: recalculate soil + surcharge with final_D,
        # if your method requires iterative approach. For demonstration, we do it once.

        # 6) Build results dictionary
        results = {
            "soil_pressures": soil_pressures,
            "surcharge_pressures": surcharge_pressures,
            "total_pressures": total_pressure,
            "final_embedment": final_D
        }

        return results


# ---------------------------------------------------------------------------
# 6) Usage Example
#    In practice, you’d call something like this from your main GUI code.
# ---------------------------------------------------------------------------
def example_usage():
    """
    Demo code simulating how you'd integrate with the GUI.
    """
    # Step A: Imagine we have read everything from GUI into these DTOs:
    gen_info = GeneralInfoData(
        title="Demo Project",
        job_no="123",
        designer="Engineer A",
        checker="Engineer B",
        company="ACME Co.",
        client="XYZ",
        unit="ft-lb",
        date="2024-12-24",
        comment="Example"
    )

    gen_props = GeneralPropertiesData(
        fs=1.5,
        E=29000,
        pile_spacing=3.0,
        fy=50,
        allowable_deflection=0.5,
        section_name="W12x40"
    )

    # 1 Soil layer with height=10 ft:
    layer = SoilLayerData(height=10.0, properties={"γ": 120, "φ": 30})
    soil_profile = SoilProfileData(
        theory_name="Rankine",
        layers=[layer],
        has_water=False,
        water_depth=0.0
    )

    # No supports for Cantilever
    geo_soil = GeometricalSoilData(
        shoring_type="Cantilever",
        angle=0.0,
        supports=[],
        soil_profile=soil_profile
    )

    # Example Surcharge: 1 uniform load
    from math import inf
    surch_load = SurchargeLoadData("Uniform", {"q": 200.0})
    surcharge_data = SurchargeData(
        ka_surcharge=1.0,
        loads=[surch_load]
    )

    lagging = LaggingData(ph_max=1000, fb=2000, timber_size="4 x 12")

    # Consolidate
    gui_data = GUIData(
        general_info=gen_info,
        general_props=gen_props,
        geo_soil=geo_soil,
        surcharge=surcharge_data,
        lagging=lagging
    )

    # Step B: We create the calculation manager with
    # #   a particular SoilPressureCalculator + SurchargeCalculator
    # soil_calc = SimpleSoilPressureCalculator(guessed_embedment=5.0, dz=0.5)
    # surch_calc = SimpleSurchargeCalculator(guessed_embedment=5.0, dz=0.5)
    # calc_manager = CalculationManager(soil_calc, surch_calc)
    #
    # # Step C: Run the calculation
    # results = calc_manager.run_calculation(gui_data)
    #
    # # Print or post-process results
    # print("== Calculation Results ==")
    # print(f"Soil Pressures: {results['soil_pressures']}")
    # print(f"Surcharge Pressures: {results['surcharge_pressures']}")
    # print(f"Total Pressures: {results['total_pressures']}")
    # print(f"Final Embedment Depth (D) = {results['final_embedment']} ft")


# If run as a script:
if __name__ == "__main__":
    example_usage()
