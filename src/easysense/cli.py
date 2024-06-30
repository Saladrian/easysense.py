import os
import subprocess

from easysense import Easysense


def display_start():
    print("╔═════════════════════════════╗")
    print("║          Easysense          ║")
    print("║      -----------------      ║")
    print("║         Pre-written         ║")
    print("║    sensor implementations   ║")
    print("║        for Wiresense        ║")
    print("╚═════════════════════════════╝")
    print("https://github.com/Saladrian/easysense.py")
    print()
    print("All available sensors: https://github.com/Saladrian/easysense.py-sensors")
    print()
    print()


def list_sensors():
    print("Downloaded sensors:")
    sorted_sensors = sorted(Easysense.sensors.keys())
    if sorted_sensors:
        for i, s in enumerate(sorted_sensors, 1):
            print(f"{i}. {s}")
        print()
    else:
        print("No sensors found!")
        print("Please install one first: 'easysense install <sensor>'")
        print("Check out the GitHub repo for all available sensors: https://github.com/Saladrian/easysense.py-sensors")
        exit(0)


def open_it(path: str, is_folder: bool = False):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The path does not exist: '{path}'")
    if is_folder and not os.path.isdir(path):
        raise NotADirectoryError(f"The path is not a valid directory: '{path}'")

    if os.name == "nt":  # For Windows
        os.startfile(path)
    elif os.name == "posix":  # For macOS and Linux
        subprocess.call(("xdg-open", path))
    else:
        raise RuntimeError(f"Unsupported OS: '{os.name}'. This currently only supports 'nt' (Windows) and 'posix' (Linux & macOS). Please open it manually: '{path}'")
