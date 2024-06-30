<h1 align="center" id="title">Easysense.py</h1>

![easysense.py](https://socialify.git.ci/Saladrian/easysense.py/image?font=Inter&forks=1&issues=1&language=1&owner=1&pattern=Solid&pulls=1&stargazers=1&theme=Auto)

<p align="center">
    <img src="https://img.shields.io/badge/Made%20with%20Love%E2%9D%A4%EF%B8%8F-black?style=for-the-badge" alt="made with love">
    <img src="https://img.shields.io/badge/Python%20-FFD147?style=for-the-badge&logo=python&logoColor=%23" alt="asyncio">
    <img src="https://img.shields.io/github/actions/workflow/status/Saladrian/easysense.py/publish.yml?style=for-the-badge" alt="build status">
    <img src="https://img.shields.io/pypi/v/easysense?style=for-the-badge" alt="pypi version">
    <img src="https://img.shields.io/pypi/dm/easysense?style=for-the-badge" alt="pypi downloads">
</p>

A CLI tool providing pre-written sensor implementations for Wiresense, designed to simplify sensor integration and data collection.

## 🛠️Features

- Select the sensor you have
- Select the measurement rate
- Easy to use, only basic knowledge required
- Uses Wiresense for data visualization:
- Automaticly save data into csv files

For more info about Wiresense see: https://github.com/Wiresense

## 📖Usage

Install with pip

```bash
pip install easysense
```
Make sure you have [Python](https://wiki.python.org/moin/BeginnersGuide/Download) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed!

Run Easysense

```bash
easysense
```

Simply follow the instructions in the terminal to get started 

Or edit the config.yaml so you dont need to configure it every time. (csv path can only be changed in config.yaml)
You can open the config with: `easysense config`

```yaml
settings:
  selected_sensor: ""  # Exact name of the sensor (see /sensors folder for the names) (leave empty to get a prompt every time)
  read_interval: -1  # Measurement inverval in seconds (set to -1 to get a prompt every time)
  csv_folder_path: "./data"  # Where to say all created csv files. (For best functionality, use absolute path)
  print_data_in_cmd: null  # Boolean whether the sensor output should also be printed in the cmd (set to null to get a prompt every time)
```

## 📡 Sensors
All currently availably sensors can be found in this Repo: https://github.com/Saladrian/easysense.py-sensors
Simply use the name of the folder to install the sensor:
```bash
easysense install <sensor-name>
```


---

If you have a sensor that is not yet implemented, feel free to open a issue or contribute it yourself.

For more info about how you can implement a sensor see: [src/easysense/sensors/_example_sensor.py](https://github.com/Saladrian/easysense.py/blob/main/src/easysense/sensors/.example/main.py)


## 📜License

[MIT](https://choosealicense.com/licenses/mit/)

## ✍️Authors

- [@saladrian](https://github.com/saladrian)