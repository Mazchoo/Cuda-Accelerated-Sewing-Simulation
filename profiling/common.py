import sys
import os
from pathlib import Path

from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML
import numpy as np

FORMATTER = HtmlFormatter(style="colorful", full=True, noclasses=True)


def read_file_str(path: str) -> str:
    return Path(path).open().read()


def show_formatted_cpp(kernel_code: str) -> HTML:    
    highlighted_code = highlight(kernel_code, CppLexer(), FORMATTER)
    return HTML(highlighted_code)


def save_numpy_array(filename: str, arr: np.ndarray):
    np.save(f'./numpy/{filename}', arr)


def load_numpy(filename: str) -> np.ndarray:
    return np.load(f'./numpy/{filename}')
