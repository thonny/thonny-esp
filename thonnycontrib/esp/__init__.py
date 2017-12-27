from thonnycontrib.micropython import MicroPythonProxy
from thonny.globals import get_workbench, get_runner
import os
from thonny import THONNY_USER_BASE
import subprocess
from thonny.ui_utils import SubprocessDialog

class ESPProxy(MicroPythonProxy):
    @property
    def firmware_filetypes(self):
        return [('*.bin files', '.bin'), ('all files', '.*')]
    
    def erase_flash(self):
        env = os.environ.copy()
        env["PYTHONUSERBASE"] = THONNY_USER_BASE # Use Thonny plugins folder instead of regular userbase
        self.disconnect()
        cmd = [get_runner().get_frontend_python(), '-u', '-m', 
                'esptool', 
                '--port', self.port, 
                'erase_flash']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
        dlg = SubprocessDialog(get_workbench(), proc, "Erasing flash", autoclose=False)
        dlg.wait_window()
        
        
class ESP8266Proxy(ESPProxy):
    @property
    def known_usb_vids_pids(self):
        return {
            # eg. Adafruit Feather Huzzah 
            (0x10C4, 0xEA60) : "A device using Silicon Labs CP210x USB to UART Bridge",
            (0x1A86, 0x7523) : "A device using USB-SERIAL CH340",
        }
    
    @property
    def flash_mode(self):
        # "dio" for some boards with a particular FlashROM configuration (e.g. some variants of a NodeMCU board)
        # https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html
        # https://github.com/espressif/esptool/wiki/SPI-Flash-Modes
        
        # TODO: detect the need for this (or provide conf option for the backend)
        return "keep"
        #return "dio"
        
    def construct_firmware_upload_command(self, firmware_path):
        return [get_runner().get_frontend_python(), '-u', '-m', 
                'esptool', 
                '--port', self.port, 
                #'--baud', '460800',  
                'write_flash', 
                #'--flash_size', 'detect',
                #"--flash_mode", self.flash_mode,
                '0x0000', firmware_path]
        
class ESP32Proxy(ESPProxy):
    @property
    def known_usb_vids_pids(self):
        return {
            # eg. ESP-WROOM-32
            (0x10C4, 0xEA60) : "A device using Silicon Labs CP210x USB to UART Bridge"
        }
        
    def construct_firmware_upload_command(self, firmware_path):
        cmd = [get_runner().get_frontend_python(), '-u', '-m', 
                'esptool', 
                #'--chip', 'esp32',
                '--port', self.port, 
                #'--baud', '460800', 
                'write_flash', 
                #'--flash_size=detect',
                '0x1000',
                firmware_path]
        
        cmd.extend = ['0', firmware_path]


def load_early_plugin():
    print("LOADING ESP")
    get_workbench().add_backend("ESP8266", ESP8266Proxy)
    get_workbench().add_backend("ESP32", ESP32Proxy)

def load_plugin():
    def erase_flash():
        proxy = get_runner().get_backend_proxy()
        proxy.erase_flash()
    
    def erase_flash_enabled():
        return isinstance(get_runner().get_backend_proxy(), ESPProxy)
        
    get_workbench().add_command("erasespflash", "tools", "Erase ESP8266/ESP32 flash",
                                erase_flash,
                                erase_flash_enabled,
                                group=120,
                                position_in_group="alphabetic")
    