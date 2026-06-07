import os

class ThermalManager:
    def get_cpu_temp(self):
        temp = os.popen("vcgencmd measure_temp").readline()
        return float(temp.replace("temp=", "").replace("'C\n", ""))