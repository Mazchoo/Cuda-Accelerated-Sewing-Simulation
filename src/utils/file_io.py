"""File reading helpers"""

from pathlib import Path
import json

from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML

FORMATTER = HtmlFormatter(style="colorful", full=True, noclasses=True)


def read_json(path: str) -> dict:
    """Read json from file"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_mtl_file_exists(obj_path: str) -> str:
    """Get corresponding .mtl for current .obj file"""
    obj_path = Path(obj_path)
    mtl_path = obj_path.parent / (obj_path.stem + ".mtl")

    if not mtl_path.exists():
        raise FileNotFoundError(f"Mtl {mtl_path} cannot be found.")

    return str(mtl_path)


def parse_material(line, file_path):
    """Read material line and check it refers to an image e.g. Texture_2.png"""
    material_path = Path(file_path).parent / line

    if not material_path.exists():
        raise FileNotFoundError(f"Material {line} does not exist")
    if material_path.suffix != ".png":
        raise AttributeError("Only .png image type supported.")

    return str(material_path)


def read_file_str(path: str) -> str:
    """Return file contents as string"""
    return Path(path).open().read()


def show_formatted_cpp(kernel_code: str) -> HTML:
    highlighted_code = highlight(kernel_code, CppLexer(), FORMATTER)
    return HTML(highlighted_code)


def replace_constants_in_kernel(kernel_code: str, variables: dict) -> str:
    for key, value in variables.items():
        kernel_code = kernel_code.replace(key, f"{float(value)}f")
    return kernel_code
