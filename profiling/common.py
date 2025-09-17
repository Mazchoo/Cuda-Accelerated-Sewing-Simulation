"""Common profiling routines"""

from pathlib import Path

from pygments import highlight
from pygments.lexers.c_cpp import CppLexer
from pygments.formatters.html import HtmlFormatter
from IPython.core.display import HTML

FORMATTER = HtmlFormatter(style="colorful", full=True, noclasses=True)


def read_file_str(path: str) -> str:
    """Return file contents as string"""
    return Path(path).open(encoding="utf-8").read()


def show_formatted_cpp(kernel_code: str) -> HTML:
    """Format a cpp like language into HTML"""
    highlighted_code = highlight(kernel_code, CppLexer(), FORMATTER)
    return HTML(highlighted_code)


def replace_constants_in_kernel(kernel_code: str, variables: dict) -> str:
    """
    Replace constants in a cuda kernel
    Equivalent to defining a macro with constants
    """
    for key, value in variables.items():
        kernel_code = kernel_code.replace(key, f"{float(value)}f")
    return kernel_code
