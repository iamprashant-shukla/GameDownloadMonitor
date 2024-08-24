import psutil
import time
import os
import sys
import tkinter as tk  # GUI library
from threading import Thread  # Allows running background tasks
from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"G:\VS projects\build\assets\frame0") #The line is specific to your file system, pointing to a directory where your GUI assets (like images) are stored. This hardcoded path won't work for other users unless they have the exact same directory structure on their system.


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


# Define the NetworkMonitorApp class with your GUI layout and monitoring logic
class NetworkMonitorApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Download Tracker")
        self.geometry("394x202")
        self.configure(bg="#FFFFFF")
        self.resizable(False, False)

        self.monitor_thread = None
        self.monitoring = False  # Flag to control the monitoring loop
        self.countdown_running = False  # Flag to control the countdown process

        self.canvas = Canvas(
            self,
            bg="#FFFFFF",
            height=202,
            width=394,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Output text area for monitoring information
        self.entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        self.entry_bg_1 = self.canvas.create_image(196.5, 82.5, image=self.entry_image_1)

        self.output = Text(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.output.place(x=6.0, y=14.0, width=381.0, height=135.0)

        # Start and Stop buttons
        self.button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        self.start_button = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.stop_monitoring,
            relief="flat"
        )
        self.start_button.place(x=264.0, y=160.0, width=99.0, height=34.0)

        self.button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
        self.stop_button = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.start_monitoring,
            relief="flat"
        )
        self.stop_button.place(x=30.0, y=160.0, width=99.0, height=34.0)

        # Other UI elements
        self.image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(158.0, 177.0, image=self.image_image_1)

        self.image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
        self.image_2 = self.canvas.create_image(197.0, 177.0, image=self.image_image_2)

        self.image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
        self.image_3 = self.canvas.create_image(236.0, 175.0, image=self.image_image_3)

        self.threshold_mbps = 0.01  # Threshold in MBps for shutdown

    def get_download_speed(self):
        # Measure download speed in MBps
        net_before = psutil.net_io_counters()
        time.sleep(1)  # Measure over 1 second
        net_after = psutil.net_io_counters()
        bytes_received = net_after.bytes_recv - net_before.bytes_recv
        download_speed_mbps = bytes_received / (1024 * 1024)  # Convert to MBps
        return download_speed_mbps

    def monitor_network(self):
        while self.monitoring:
            download_speed = self.get_download_speed()
            self.output.insert(tk.END, f"Current download speed: {download_speed:.6f} MBps\n")
            self.output.see(tk.END)

            if download_speed < self.threshold_mbps:
                self.output.insert(tk.END, "Download speed is close to zero. Initiating shutdown.\n")
                self.start_countdown()  # Start the countdown to shut down
                break
            
            time.sleep(10)  # Check every 10 seconds

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = Thread(target=self.monitor_network)
            self.monitor_thread.start()  # Start monitoring in a separate thread

    def stop_monitoring(self):
        self.monitoring = False  # Stop the monitoring loop
        self.stop_countdown()  # Stop the shutdown countdown if running

    def start_countdown(self, countdown_time=25):
        self.countdown_running = True
        self.output.insert(tk.END, "Starting shutdown countdown...\n")
        for remaining in range(countdown_time, 0, -1):
            if not self.countdown_running:  # Stop countdown if flag is False
                self.output.insert(tk.END, "Shutdown cancelled.\n")
                break
            self.output.insert(tk.END, f"Shutting down in {remaining} seconds...\n")
            self.output.see(tk.END)
            time.sleep(1)
        
        if self.countdown_running:  # If countdown wasn't stopped
            if sys.platform == "win32":
                os.system("shutdown /s /t 0")
            elif sys.platform == "darwin" or sys.platform.startswith("linux"):
                os.system("shutdown -h now")

    def stop_countdown(self):
        self.countdown_running = False  # Stop the countdown process


# Create and run the app
if __name__ == "__main__":
    app = NetworkMonitorApp()
    app.mainloop()
