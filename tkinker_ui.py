import tkinter as tk
import tkinter.ttk as ttk
from serial import Serial
from serial.tools.list_ports import comports
from tkinter.messagebox import showerror
from threading import Thread, Lock # we'll use Lock later ;)
from typing import Union

class LockedSerial(Serial):
    _lock: Lock = Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, size=1) -> bytes:
        with self._lock:
            return super().read(size)

    def write(self, b: bytes, /) -> Union[int, None]:
        with self._lock:
            super().write(b)

    def close(self):
        with self._lock:
            super().close()

class App(tk.Tk):
    ser: LockedSerial

    def __init__(self):
        super().__init__()

        self.title("LED Blinker")

        self.port = tk.StringVar() # add this
        self.led = tk.BooleanVar()

        ttk.Checkbutton(self, text='Toggle LED', variable=self.led, command=self.update_led).pack()
        ttk.Button(self, text='Send Invalid',command=self.send_invalid).pack()
        ttk.Button(self, text='Disconnect', default='active',command=self.disconnect).pack()

        SerialPortal(self) # and this

    def detached_callback(f):
        return lambda *args, **kwargs: Thread(target=f, args=args, kwargs=kwargs).start()

    def connect(self):
        self.ser = LockedSerial(self.port.get())

    @detached_callback
    def update_led(self):
        self.write(bytes([self.led.get()]))

    @detached_callback
    def send_invalid(self):
        self.write(bytes([0x10]))
        
    def disconnect(self):
        self.ser.close()
        SerialPortal(self) # display portal to reconnect
    
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.disconnect()


    def write(self, b: bytes):
        S_OK: int = 0xaa
        S_ERR: int = 0xff
        try:
            self.ser.write(b)
            if int.from_bytes(self.ser.read(), 'big') == S_ERR:
                showerror('Device Error', 'The device reported an invalid command.')
        except SerialException:
            showerror('Serial Error', 'Write failed.')
        # send `value` somehow??



class SerialPortal(tk.Toplevel):
    
    def __init__(self, parent: App):
        super().__init__(parent)

        self.parent = parent
        self.parent.withdraw() # hide App until connected

        ttk.OptionMenu(self, parent.port, '', *[d.device for d in comports()]).pack()
        ttk.Button(self, text='Connect', command=self.connect, default='active').pack()

    def connect(self):
        self.parent.connect()
        self.destroy()
        self.parent.deiconify() # reveal App
    

if __name__ == '__main__':
    with App() as app:
        app.mainloop()