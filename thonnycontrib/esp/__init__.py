from thonnycontrib.micropython import MicroPythonProxy
from thonny.globals import get_workbench

class ESPProxy(MicroPythonProxy):
    pass
        
class ESP8266Proxy(ESPProxy):
    @property
    def __known_usb_vids_pids(self):
        return {
            (0x10C4, 0xEA60) : "Adafruit Feather Huzzah"
        }
        
class ESP32Proxy(ESPProxy):
    @property
    def known_usb_vids_pids(self):
        return {
            (0x10C4, 0xEA60) : "ESP-WROOM-32"
        }
        

def load_early_plugin():
    print("LOADING ESP")
    get_workbench().add_backend("ESP8266", ESP8266Proxy)
    get_workbench().add_backend("ESP32", ESP32Proxy)
    