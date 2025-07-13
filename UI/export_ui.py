''' Export .ui file as a .py file '''
from PyQt5 import uic

INPUT_PATH = "./UI/sewing_simulation.ui"

if __name__ == '__main__':
    with open("UI/SewingSimulationUI.py", "w", encoding="utf-8") as f:
        uic.compileUi(INPUT_PATH, f)
