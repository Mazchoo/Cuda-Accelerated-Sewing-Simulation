"""Parse material file"""

from typing import Union, Optional

from src.utils.file_io import check_mtl_file_exists, parse_material
from src.utils.common_types import Point3D


def parse_vertex(line: str) -> Point3D:
    """Parse a vertex line e.g. -5.490000 20.340000 4.410002"""
    vertex = [float(x) for x in line.split(" ")]

    if len(vertex) != 3:
        raise ValueError(f"Vertex {line} is wrong length.")

    return vertex


def get_texture(current_dict) -> Optional[Union[str, Point3D]]:
    """Texture will either be a previously read image or a colour from the diffuse weighting"""
    if texture := current_dict.get("texture"):
        return texture
    if texture := current_dict.get("diffuse_weighting"):
        return tuple(texture)
    return None


def parse_material_name(
    current_material: str, current_mtl_data: dict, all_materials: dict
):
    """Texture will be a coordinate or an image or an explicit color vt 0.491723 -0.123703"""
    if current_material:
        current_mtl_data["texture"] = get_texture(current_mtl_data)

        if current_mtl_data["texture"] is None:
            raise KeyError("End of material reached with no texture present.")

        all_materials[current_material] = current_mtl_data


def parse_mtl(obj_path: str) -> dict:
    """Read mtl file into a dictionary"""
    mtl_path = check_mtl_file_exists(obj_path)

    current_mtl_data = {}
    current_material = ""

    all_materials = {}
    with open(mtl_path, "r", encoding="utf-8") as f:
        while line := f.readline():
            line = line.strip()
            flag = line[: line.find(" ")]
            line_content = line[len(flag) + 1 :]

            if flag == "newmtl":
                parse_material_name(current_material, current_mtl_data, all_materials)

                current_material = line_content
                current_mtl_data = {}
            elif flag == "Ns":
                current_mtl_data["specular_exponent"] = float(line_content)
            elif flag == "Ka":
                current_mtl_data["ambient_weighting"] = parse_vertex(line_content)
            elif flag == "Kd":
                current_mtl_data["diffuse_weighting"] = parse_vertex(line_content)
            elif flag == "Ks":
                current_mtl_data["specular_weighting"] = parse_vertex(line_content)
            elif flag == "Ke":
                current_mtl_data["emission_weighting"] = parse_vertex(line_content)
            elif flag == "Ni":
                current_mtl_data["refractive_index"] = float(line_content)
            elif flag == "d":
                current_mtl_data["opacity"] = float(line_content)
            elif flag == "illum":
                current_mtl_data["illumination_model"] = int(line_content)
            elif flag == "map_Kd":
                current_mtl_data["texture"] = parse_material(line_content, mtl_path)
            elif flag == "Ti":
                current_mtl_data["specular_tint"] = float(line_content)

        parse_material_name(current_material, current_mtl_data, all_materials)

    return all_materials
