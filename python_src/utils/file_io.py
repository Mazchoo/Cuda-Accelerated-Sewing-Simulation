""" File reading helpers """
from pathlib import Path
import json


def read_json(path: str) -> dict:
    """ Read json from file """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_mtl_file_exists(obj_path: str) -> str:
    ''' Get corresponding .mtl for current .obj file '''
    obj_path = Path(obj_path)
    mtl_path = obj_path.parent / (obj_path.stem + '.mtl')

    if not mtl_path.exists():
        raise FileNotFoundError(f"Mtl {mtl_path} cannot be found.")

    return str(mtl_path)


def parse_material(line, file_path):
    ''' Read material line and check it refers to an image e.g. Texture_2.png '''
    material_path = Path(file_path).parent / line

    if not material_path.exists():
        raise FileNotFoundError(f'Material {line} does not exist')
    if material_path.suffix != '.png':
        raise AttributeError('Only .png image type supported.')

    return str(material_path)
