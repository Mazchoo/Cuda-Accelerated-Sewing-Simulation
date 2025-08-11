""" Translation from variable name to shader global variable name """

MATERIAL_PROPERTIES = {
    "ambient_weighting_glob_id": "currentMaterial.ambientWeighting",
    "diffuse_weighting_glob_id": "currentMaterial.diffuseWeighting",
    "specular_weighting_glob_id": "currentMaterial.specularWeighting",
    "specular_exponent_glob_id": "currentMaterial.specularExponent",
    "opacicty_glob_id": "currentMaterial.opacity",
    "specular_tint_glob_id": "currentMaterial.specularTint",
}

LIGHT_PROPERTIES = {
    "position_glob_id": "lightSource.position",
    "color_glob_id": "lightSource.color",
    "strength_glob_id": "lightSource.strength",
    "ambient_strength_glob_id": "lightSource.ambientStrength",
    "min_dist_glob_id": "lightSource.minDistance",
    "max_dist_glob_id": "lightSource.maxDistance"
}
