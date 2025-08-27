"""Common profiling routines"""

from pathlib import Path

from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter
from IPython.core.display import HTML

FORMATTER = HtmlFormatter(style="colorful", full=True, noclasses=True)


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
