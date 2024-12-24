class SoilTheory:
    def get_parameters(self):
        raise NotImplementedError


class UserDefinedTheory(SoilTheory):
    def __init__(self):
        self.distribution_type = "Triangle"
        self.h1 = 0
        self.h2 = 0
        self.sigma_a = 0

    def get_parameters(self):
        return ['EFP Active', 'EFP Passive', 'Distribution Type']

    def set_distribution(self, distribution_type, h1=0, h2=0, sigma_a=0):
        self.distribution_type = distribution_type
        self.h1 = h1
        self.h2 = h2
        self.sigma_a = sigma_a

    def get_distribution_params(self):
        return {
            "type": self.distribution_type,
            "h1": self.h1,
            "h2": self.h2,
            "sigma_a": self.sigma_a
        }


class RankineTheory(SoilTheory):
    def get_parameters(self):
        return ['φ', 'γ', 'c']


class CoulombTheory(SoilTheory):
    def get_parameters(self):
        return ['φ', 'γ', 'c', 'δ']


# Factory Pattern for Soil Theories
class SoilTheoryFactory:
    @staticmethod
    def create_theory(theory_name):
        theory_name = theory_name.lower().replace(" ", "")
        if "userdefined" in theory_name:
            return UserDefinedTheory()
        elif "rankine" in theory_name:
            return RankineTheory()
        elif "coulomb" in theory_name:
            return CoulombTheory()
        else:
            raise ValueError(f"Invalid theory name: {theory_name}")
