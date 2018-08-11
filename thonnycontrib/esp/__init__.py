from thonny.plugins.micropython import MicroPythonProxy, MicroPythonConfigPage,\
    add_micropython_backend
from thonny import get_workbench, get_runner
import os
import subprocess
from thonny.ui_utils import SubprocessDialog
from thonny.running import get_frontend_python
from time import sleep

class ESPProxy(MicroPythonProxy):
    def _finalize_repl(self):
        # In some cases there may be still something coming.
        sleep(0.1)
        remainder = self._serial.read_all().decode("utf-8", "replace").strip()
        # display it unless it looks like an extra raw prompt
        if remainder and (len(remainder) > 40 or "raw REPL; CTRL-B to exit" not in remainder):
            self._send_error_to_shell(remainder)
            
    @property
    def firmware_filetypes(self):
        return [('*.bin files', '.bin'), ('all files', '.*')]
    
    def erase_flash(self):
        self.disconnect()
        cmd = [get_frontend_python(), '-u', '-m', 
                'esptool', 
                '--port', self.port, 
                'erase_flash']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
        dlg = SubprocessDialog(get_workbench(), proc, "Erasing flash", autoclose=False)
        dlg.wait_window()
    
    def _supports_directories(self):
        return True
        
        
class ESP8266Proxy(ESPProxy):
    description = "MicroPython on ESP8266"
    config_page_constructor = "ESP8266"
    
    @property
    def known_usb_vids_pids(self):
        return super().known_usb_vids_pids | {
            # eg. Adafruit Feather Huzzah 
            (0x10C4, 0xEA60), # Silicon Labs CP210x USB to UART Bridge,
            (0x1A86, 0x7523), # USB-SERIAL CH340,
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
        return [get_frontend_python(), '-u', '-m', 
                'esptool', 
                '--port', self.port, 
                #'--baud', '460800',  
                'write_flash', 
                #'--flash_size', 'detect',
                #"--flash_mode", self.flash_mode,
                '0x0000', firmware_path]
        
    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp8266_api_stubs")
    
class ESP32Proxy(ESPProxy):
    @property
    def known_usb_vids_pids(self):
        return super().known_usb_vids_pids | {
            # eg. ESP-WROOM-32
            (0x10C4, 0xEA60), # Silicon Labs CP210x USB to UART Bridge
        }
        
    def construct_firmware_upload_command(self, firmware_path):
        return [get_frontend_python(), '-u', '-m', 
                'esptool', 
                #'--chip', 'esp32',
                '--port', self.port, 
                #'--baud', '460800', 
                'write_flash', 
                #'--flash_size=detect',
                '0x1000',
                firmware_path]

    def _get_api_stubs_path(self):
        return os.path.join(os.path.dirname(__file__), "esp32_api_stubs")
    
class ESP8266ConfigPage(MicroPythonConfigPage):
    pass

class ESP32ConfigPage(MicroPythonConfigPage):
    pass

def load_plugin():
    add_micropython_backend("ESP8266", ESP8266Proxy, "MicroPython on ESP8266", ESP8266ConfigPage)
    add_micropython_backend("ESP32", ESP32Proxy, "MicroPython on ESP32", ESP32ConfigPage)

    def upload_micropython():
        proxy = get_runner().get_backend_proxy()
        proxy.select_and_upload_micropython()
    
    def upload_micropython_enabled():
        proxy = get_runner().get_backend_proxy()
        return (getattr(proxy, "micropython_upload_enabled", False)
                and isinstance(proxy, ESPProxy))
        
    def erase_flash():
        proxy = get_runner().get_backend_proxy()
        proxy.erase_flash()
    
    def erase_flash_enabled():
        return (isinstance(get_runner().get_backend_proxy(), ESPProxy)
                and get_runner().get_backend_proxy().micropython_upload_enabled)
        
    get_workbench().add_command("uploadmicropythonesp", "device", "Install MicroPython to ESP8266/ESP32 ...",
                                upload_micropython,
                                upload_micropython_enabled,
                                group=40)

    get_workbench().add_command("erasespflash", "device", "Erase ESP8266/ESP32 flash",
                                erase_flash,
                                tester=erase_flash_enabled,
                                group=40)
    