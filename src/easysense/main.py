import argparse
import asyncio
import importlib.util
import inspect
import logging
import os
import socket
import subprocess
import time
import warnings
from typing import Optional, List, Any


import yaml
from wiresense import Wiresense

from . import cli
from easysense import Easysense

# Constants
PATH = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
SENSOR_FOLDER = os.path.join(PATH, "sensors")
CONFIG_FILE = os.path.join(PATH, "config.yaml")
REPO_URL = "https://github.com/Saladrian/easysense.py-sensors"


# Default Config
config = {
    "selected_sensor": "",  # Exact name of the sensor (see /sensors folder for the names) (leave empty to get a prompt every time)
    "read_interval": -1,  # Measurement inverval in seconds (set to -1 to get a prompt every time)
    "csv_folder_path": "./data",  # Where to say all created csv files. (For best functionality, use absolute path)
    "print_data_in_cmd": None  # Boolean whether the sensor output should also be printed in the cmd (set to null to get a prompt every time)
}
active_sensors = {}

# Logging config
date = time.strftime("%d-%m-%Y")
log_file_path = f"{PATH}/logs/log_{date}.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(filename=log_file_path, mode="a")
    ]
)

log = logging.getLogger(__name__)


def load_config() -> None:
    if not os.path.exists(CONFIG_FILE):
        warn_msg = "config.yaml is missing! -> You will always be prompted to select required parameter"
        log.warning(warn_msg)
        print(warn_msg)

    with open(CONFIG_FILE, "r") as f:
        user_config = yaml.safe_load(f) or {}

    global config
    config.update(user_config)


def load_installed_sensors() -> None:
    for filename in os.listdir(SENSOR_FOLDER):
        module_folder_path = os.path.normpath(os.path.join(SENSOR_FOLDER, filename))
        if os.path.isdir(module_folder_path) and not filename.startswith("_") and not filename.startswith("."):
            module_path = os.path.join(module_folder_path, "main.py")
            Easysense.sensors[filename] = module_path
    log.info(f"Loaded {len(Easysense.sensors)} sensors.")


# Depricated
def load_sensors() -> None:
    for filename in os.listdir(SENSOR_FOLDER):
        module_folder_path = os.path.normpath(os.path.join(SENSOR_FOLDER, filename))
        if os.path.isdir(module_folder_path) and not filename.startswith("_") and not filename.startswith("."):
            module_path = os.path.join(module_folder_path, "main.py")
            spec = importlib.util.spec_from_file_location(filename, module_path)
            module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(module)
                Easysense.sensors[filename] = module
                log.info(f"Sensor '{filename}' loaded!")
            except ImportError as ie:
                error_msg = f"There was an error importing the sensor module '{filename}': {ie}"
                print(error_msg)
                log.error(error_msg)
            except Exception as e:
                warn_msg = f"Sensor '{filename}' not loaded!\nExtension raised an error: {e}"
                log.warning(warn_msg)
                warnings.warn(warn_msg)
    log.info(f"Loaded {len(Easysense.sensors)} sensors.")


def ask_valid_input(prompt: str, d_type: type, *, x_range: Optional[List[float]] = None, error_msg: str = "Please enter valid data.") -> Any:
    user_input = input(prompt)
    try:
        value = d_type(user_input)
        if d_type in [int, float] and x_range:
            if not x_range[0] <= value <= x_range[1]:
                raise ValueError
        elif d_type is bool:
            if user_input.strip().lower() in "yn":
                return user_input.lower() == "y"
            else:
                raise ValueError
        return value

    except ValueError:
        print(error_msg)
        return ask_valid_input(prompt, d_type, x_range=x_range, error_msg=error_msg)


def select_sensor() -> (str, Easysense):
    s_sensor = config.get("selected_sensor")

    if s_sensor and type(s_sensor) is str:
        matching_sensor = Easysense.sensors.get(s_sensor)
        if matching_sensor:
            print(f"Auto-selected Sensor from config.yaml: {s_sensor}")
            log.info(f"Auto-selected Sensor from config.yaml: {s_sensor}")
            return s_sensor
        else:
            print(f"Sensor selected in config.yaml not found: '{s_sensor}'")
            log.info("Sensor selected in config.yaml not found -> Prompting user to select sensor manually")

    cli.list_sensors()
    numb = ask_valid_input(
        prompt="Enter the number of the sensor you want to use: ",
        d_type=int,
        x_range=[1, len(Easysense.sensors)],
        error_msg="This number is not in the list."
    )

    s_name = sorted(Easysense.sensors.keys())[numb - 1]
    print(f"Selected Sensor: {s_name}")
    log.info(f"Selected Sensor: {s_name}")

    return s_name


def select_interval() -> float:
    s_interval = config.get("read_interval")
    x_range = [0, float("inf")]

    if x_range[0] < s_interval:
        selected_interval = s_interval
        print(f"Auto-selected Interval from config.yaml: {selected_interval}")
        log.info(f"Auto-selected Interval from config.yaml: {selected_interval}")
        return selected_interval
    elif s_interval != -1:
        print(f"Invalid read_interval in config.yaml")
        log.warning(f"Invalid read_interval in config.yaml -> Prompting user to enter interval manually")

    selected_interval = ask_valid_input(
        prompt="Enter the interval at which the data of the selected sensor should be read (in seconds): ",
        d_type=float,
        x_range=x_range,
        error_msg="Interval must be a float >= 0"
    )
    print(f"Selected Interval: {selected_interval}")
    log.info(f"Selected Interval: {selected_interval}")
    return selected_interval


def select_print_data() -> bool:
    s_print_data = config.get("print_data_in_cmd")

    if s_print_data is None:
        selected_print_data = ask_valid_input(
            prompt="Should the data be printed here too? (Y/n): ",
            d_type=bool,
            error_msg="Input must be 'Y' or 'n'."
        )
        print(f"Selected Print cmd: {selected_print_data}")
        log.info(f"Selected Print cmd: {selected_print_data}")
    else:
        selected_print_data = s_print_data
        print(f"Auto-selected Print data from config.yaml: {selected_print_data}")
        log.info(f"Auto-selected Print data from config.yaml: {selected_print_data}")

    return selected_print_data


def use_sensor(s_name: str) -> Easysense:
    if s_name in active_sensors:
        sensor = active_sensors.get(s_name)

        for name, obj in inspect.getmembers(sensor, inspect.isclass):
            if issubclass(obj, Easysense) and obj is not Easysense:
                sensor_class = obj
                sensor_instance = sensor_class()
                return sensor_instance
        else:
            log.error(f"This sensor seems to be not correctly implemented: No subclass inheriting from Easysense found in sensor '{s_name}'")
            raise RuntimeError(f"No subclass inheriting from Easysense found in sensor '{s_name}'")
    else:
        log.error(f"Selected Sensor '{s_name}' not found! Please install it using: 'easysense install {s_name}'")
        raise RuntimeError(f"Selected Sensor '{s_name}' not found!")


async def setup_wiresense(s_name, interval, csv_file_path, print_data) -> None:
    log.info("Configuring Wiresense...")
    await Wiresense.config({
        "port": 8080
    })

    sensor = use_sensor(s_name)
    selected_sensor = Wiresense(s_name, sensor.give_data, csv_file_path)

    log.info("Wiresense Configured")
    try:
        print("Now Running, press CTRL + C to exit.")
        log.info("Running sensor.execute() in an infinite loop...")
        if print_data:
            while True:
                payload = await selected_sensor.execute()
                values = [f"{key}: {value}" for key, value in payload.get("data").items()]
                print(", ".join(values))
                await asyncio.sleep(interval)
        else:
            while True:
                await selected_sensor.execute()
                await asyncio.sleep(interval)
    except KeyboardInterrupt:
        log.info("Exited App: KeyboardInterrupt")
        exit(0)


def setup_sensor(sensor_name: str) -> None:
    install_requirements(sensor_name)

    spec = importlib.util.spec_from_file_location(sensor_name, Easysense.sensors.get(sensor_name))
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
        log.info(f"Sensor '{sensor_name}' loaded!")
        global active_sensors
        active_sensors[sensor_name] = module
    except ImportError as ie:
        error_msg = f"There was an error importing the sensor module '{sensor_name}': {ie}"
        print(error_msg)
        log.error(error_msg)
    except Exception as e:
        warn_msg = f"Sensor '{sensor_name}' not loaded!\nExtension raised an error: {e}"
        log.warning(warn_msg)
        warnings.warn(warn_msg)


def install_requirements(sensor_name: str) -> None:
    requirements_path = os.path.join(SENSOR_FOLDER, sensor_name, "requirements.txt")
    if os.path.exists(requirements_path):
        print("Checking all modules are installed and installing those missing...")
        os.system(f"pip install -r {requirements_path}")
        print("Done!")


def run_program() -> None:
    cli.display_start()

    load_installed_sensors()

    s_name = select_sensor()
    sel_interval = select_interval()
    print_data = select_print_data()

    setup_sensor(s_name)

    csv_folder = config.get("csv_folder_path")
    os.makedirs(csv_folder, exist_ok=True)
    file_path = os.path.join(csv_folder, f"{s_name}.csv")

    print("Click here to view your Data: https://wiresense.github.io/frontend/")

    asyncio.run(setup_wiresense(s_name, sel_interval, file_path, print_data))


def check_internet_connection() -> bool:
    try:
        socket.create_connection(("1.1.1.1", 80), timeout=5)
        log.info("Internet connection available!")
        return True
    except OSError:
        log.warning("No internet connection available!")
        return False


def is_git_installed() -> bool:
    try:
        result = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def sensor_install(sensor_name: str) -> None:
    if not os.path.exists(os.path.join(SENSOR_FOLDER, ".git")):
        os.system(f"cd {SENSOR_FOLDER} && git init && git remote add origin {REPO_URL}")

    sensor_path = os.path.join(SENSOR_FOLDER, sensor_name)
    if not os.path.exists(sensor_path):
        if is_git_installed():
            os.system(f"cd {SENSOR_FOLDER} && git fetch --all && git checkout origin/main -- {sensor_name}")
            print(f"Sensor '{sensor_name}' successfully installed!")
        else:
            print("Can't download sensor: git is not installed!")
            log.error("Git is not installed!")
    else:
        print(f"'{sensor_name}' is already installed!")


def main():
    parser = argparse.ArgumentParser(description='EasySense CLI')
    parser.add_argument("command", choices=["config", "install", "sensors"], nargs="?",
                        help="Command to execute ('config': Open the config file; 'install': Install new sensors; 'sensors': Open the sensor folder)")
    parser.add_argument("sensor_name", nargs="?", help="Name of the sensor to install")

    args = parser.parse_args()

    if args.command == "sensors":
        print("Open sensor folder...")
        cli.open_it(SENSOR_FOLDER, True)
    elif args.command == "config":
        print("Open config file...")
        cli.open_it(CONFIG_FILE)
    elif args.command == "install":
        if args.sensor_name:
            if check_internet_connection():
                sensor_install(args.sensor_name)
            else:
                print("No internet connection available!")
        else:
            print("Please provide a sensor name to install.")
    else:
        run_program()


if __name__ == '__main__':
    load_config()
    main()
