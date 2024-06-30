# This is an example of how to implement a new sensor.
# Create a new folder, make sure to name it exactly like the sensor name.
# (e.g., if the sensor is named 'BME280', then call your folder "bme280")

# Always name the file with the easysense class implementation "main.py".
# If your sensor needs additional files, such as a config file or another Python file, just put them in the folder as well.

# Also, make sure to define everything within your class that inherits from Easysense.
# If you need to initialize something, do it in the __init__() method (see below).
# (Note: All folders with a leading "_" or "." will be ignored.)

# An example folder structure should look like this, including at least a main.py:
# bme280/
#  ├─ main.py
#  ├─ requirements.txt (if extra modules are required)
#  └─ config.json (optional: any other files you need)

# Import all your modules just as you normally would.
# !!! Don't forget to create a requirements.txt including all non-built-in modules.
from easysense import Easysense
import numpy as np


# Create a class that inherits from Easysense
class Example(Easysense):

    def __init__(self):
        # Initialize any required attributes or perform setup tasks here
        self.my_sensor = np.random.randint

    def give_data(self):
        # Implement the actual sensor reading logic here
        value = self.my_sensor(0, 10)

        # Return the data as a dictionary with key-value pairs
        # The key is the name displayed in the Wiresense chart
        return {"Number": value}
