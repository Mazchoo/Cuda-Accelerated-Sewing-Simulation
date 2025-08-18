""" Struct that contains all the lighting parameters for materials """
from typing import NamedTuple
import numpy as np

from src.parameters import (DEFAULT_AMBIENT_WEIGHTING, DEFAULT_DIFFUSE_WEIGHTING,
                            DEFAULT_SPECULAR_WEIGHTING, DEFAULT_SPECULAR_EXPONENT,
                            DEFAULT_OPACITY, DEFAULT_SPECULAR_TINT)


class MaterialParameters(NamedTuple):
    """Named tuple containing all lighting-related parameters for materials.

    Attributes:
        ambient_weighting: RGB weights for ambient lighting (3D vector)
        diffuse_weighting: RGB weights for diffuse lighting (3D vector)
        specular_weighting: RGB weights for specular lighting (3D vector)
        specular_exponent: Exponent controlling specular highlight size
        opacity: Material opacity (0.0 to 1.0)
        specular_tint: Tint factor for specular highlights
    """
    ambient_weighting: np.ndarray = np.array(DEFAULT_AMBIENT_WEIGHTING, dtype=np.float32)  # RGB for ambient lighting
    diffuse_weighting: np.ndarray = np.array(DEFAULT_DIFFUSE_WEIGHTING, dtype=np.float32)  # RGB for diffuse lighting
    specular_weighting: np.ndarray = np.array(DEFAULT_SPECULAR_WEIGHTING, dtype=np.float32)  # RGB for specular lighting
    specular_exponent: float = DEFAULT_SPECULAR_EXPONENT  # Specular exponent/shininess
    opacity: float = DEFAULT_OPACITY  # Material opacity
    specular_tint: float = DEFAULT_SPECULAR_TINT  # Specular tint factor
