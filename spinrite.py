#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfile
import re
import subprocess
import os
import sys
import shutil
import urllib.request
import queue
import threading
import time
import zipfile
import settings

# the GUI main class
class GUI(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        settings.init()
        self.queue = queue.Queue()
        width, height, x, y = settings.center(master, 'master', 525, 355)
        master.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.master.configure(background='#333333')
        self.master.title("Spinrite USB Creator")
        img = tk.Image("photo", file=settings.ICON)
        self.tk.call('wm','iconphoto',root._w,img)
        # causes the full width of the window to be used
        self.columnconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)

        self.make_UI()

    # Generate the UI and set some global styles
    def make_UI(self):
        style = ttk.Style()
        # global style changes
        style.configure(".", background='#333333', foreground='orange', anchor="center")
        style.map("TButton", background=[('hover', '#222222')])
        style.map("TMenubutton", background=[('hover', '#222222')])
        style.map("TEntry", foreground=[('focus', 'blue2'), ('active', 'green2')])
        style.map("TCheckbutton", background=[('hover', '#222222')])
        style.map("TRadiobutton", background=[('hover', '#222222')])

        heading = ttk.Label(self, text="Spinrite USB Creator", font=("Courier", 20))
        heading.grid(column=0, row=1, rowspan=1, columnspan=3, sticky='NWES')

        self.body = ttk.Label(self, font=("Courier", 12), wraplength=520)
        self.body['text'] = "Spinrite which has been created by Steve Gibson of grc.com is required to run " \
                            "within an MsDOS environment. This tool will allow will create a bootable USB with your own " \
                            "spinwrite.exe file contained within."
        self.body.grid(column=0, row=2, rowspan=1, columnspan=3, sticky='W', padx=5, pady=5)

        self.browse_files = ttk.Button(self, text="Add Spinrite.exe", command=self.add_exe, width=14, state='active')
        self.browse_files.grid(column=0, row=3, rowspan=1, columnspan=1, sticky='WENS', padx=5, pady=5)

        self.spinwrite_exe_txt = ttk.Label(self, font=("Courier", 12))
        self.spinwrite_exe_txt['text'] = "No .exe selected"
        self.spinwrite_exe_txt.grid(column=1, row=3, rowspan=1, columnspan=2, sticky='W', padx=5, pady=5)

        devices = self.get_bootable_media()
        row = 4
        self.var = tk.StringVar()
        for part in devices:
            self.part_radio = ttk.Radiobutton(self, text=part, variable=self.var, value=part)
            self.part_radio.grid(column=0, row=row, rowspan=1, columnspan=2, sticky='WENS', padx=5, pady=5)
            row += 1

        #self.refresh_devices = ttk.Button(self, text="Refresh Devices", command=self.get_bootable_media, width=10, state='active')
        #self.refresh_devices.grid(column=0, row=10, rowspan=1, columnspan=1, sticky='WENS', padx=5, pady=5)

        self.build_button = ttk.Button(self, text="Build USB", command=self.build, width=10, state='active')
        self.build_button.grid(column=0, row=10, rowspan=1, columnspan=1, sticky='WENS', padx=5, pady=5)

        self.exit_button = ttk.Button(self, text="Exit", command=self.exit, width=10, state='enabled')
        self.exit_button.grid(column=2, row=10, rowspan=1, columnspan=1, sticky='E', padx=5, pady=5)

        self.status = ttk.Label(self, text='')
        self.status.grid(column=1, row=14, rowspan=1, columnspan=1, sticky='WENS', padx=5, pady=5)

    def add_exe(self):
        # browse to spinrite.exe
        self.fname = askopenfile(title='Select files',  initialdir='~/', defaultextension='.exe', filetypes=[('exe','*.exe'), ('All files','*.*')])

        self.spinwrite_exe_txt.config(text=self.fname.name)
        self.spinwrite_exe_txt.update_idletasks()

    def get_bootable_media(self):
        # get all the bootable media
        df = subprocess.check_output(['sudo', 'fdisk', '-l'])
        devices = []
        for part in df.split(b'\n'):
            if part: #and b'boot' not in part:
                dev = re.match("^Disk /dev/sd.", part.decode('utf-8'))
                parts = part.split()
                if dev:
                    self.device = "{}".format(parts[1].decode('utf-8').replace(':', ''))
                    size = "{} {}".format(parts[2].decode('utf-8'), parts[3].decode('utf-8').replace(',', ''))
                    devices.append("{} {}".format(self.device, size,))
        return devices

    def build(self):
        # handle the exe
        try:
            self.spinrite_path = self.fname.name
            try:
                self.exe_error.destroy()
            except AttributeError as err:
                print(err)
        except AttributeError:
            self.exe_error = ttk.Label(self, font=("Courier", 12))
            self.exe_error['text'] = "No Sinrite.exe selected!"
            self.exe_error.grid(column=1, row=11, rowspan=1, columnspan=1, sticky='N', padx=5, pady=5)

        # handle the bootable device path
        if str(self.var.get()):
            device_path = self.var.get().split()[0]
            try:
                self.device_error.destroy()
            except AttributeError as err:
                print(err)
        else:
            self.device_error = ttk.Label(self, font=("Courier", 12))
            self.device_error['text'] = "No device selected!"
            self.device_error.grid(column=1, row=12, rowspan=1, columnspan=1, sticky='N', padx=5, pady=5)

        if self.spinrite_path and device_path:
            self.prog_bar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
            self.prog_bar.grid(column=0, row=12, rowspan=1, columnspan=3, sticky='N', padx=5, pady=5)

            if not os.path.isdir('dos'):
                os.mkdir('dos')

        self.build_button.config(state="disabled")
        self.build_thread = UsbBuild(self.queue, self.device, self.fname.name)
        self.build_thread.start()
        self.periodiccall()

    def periodiccall(self):
        self.checkqueue()
        if self.build_thread.is_alive():
           self.after(100, self.periodiccall)
        else:
            self.build_button.config(state="active")

    def checkqueue(self):
        prog_jump = 11.1
        while self.queue.qsize():
            try:
                value = self.queue.get(0)
                if value == 0:
                    self.prog_bar.step(0)
                    self.status['text'] = 'Downloading FreeDos...'
                if value == 1:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Unzipping FreeDos files'
                if value == 2:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Clearing data from USB: {}'.format(self.device)
                if value == 3:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Copying FreeDos image to USB: {}'.format(self.device)
                if value == 4:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Mounting USB: {}'.format(self.device)
                if value == 5:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Deleting unnecessary files'
                if value == 6:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Coping SpinWrite.exe to USB: {}'.format(self.device)
                if value == 7:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Editing FreeDos bootfiles'
                if value == 8:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'Unmounting USB: {}'.format(self.device)
                if value == 100:
                    self.prog_bar.step(prog_jump)
                    self.status['text'] = 'SpinRite USB build complete!'

            except queue.Empty:
                print('empty')

    # exit the program
    def exit(self):
        quit()


class UsbBuild(threading.Thread):
    def __init__(self, queue, device, spinrite_path):
        threading.Thread.__init__(self)
        self.queue = queue
        self.device = device
        self.spinrite_path = spinrite_path

    def run(self):
        # pre req
        subprocess.Popen(['sudo', 'umount', 'mnt/'])

        self.queue.put(0)
        # download free dos FD12LITE.zip
        url = 'http://www.freedos.org/download/download/FD12LITE.zip'
        urllib.request.urlretrieve(url, 'dos/dos.zip')
        time.sleep(2)

        self.queue.put(1)
        zipref = zipfile.ZipFile('dos/dos.zip')
        zipref.extractall('dos/')
        zipref.close()
        time.sleep(2)

        self.queue.put(2)
        subprocess.Popen(['sudo', 'dd', 'if=/dev/zero', 'of={}'.format(self.device), 'bs=1k', 'count=2048'])
        time.sleep(2)

        self.queue.put(3)
        subprocess.Popen(['sudo', 'dd', 'if=dos/FD12LITE.img', 'of={}'.format(self.device), 'bs=1M'])
        time.sleep(5)

        self.queue.put(4)
        subprocess.Popen(['sudo', 'mount', '{}1'.format(self.device), 'mnt/'])
        time.sleep(5)

        self.queue.put(5)
        try:
            shutil.rmtree('mnt/FDSETUP/PACKAGES/')
            shutil.rmtree('mnt/FDSETUP/SETUP/')
        except FileNotFoundError as err:
            print(err)
        time.sleep(2)

        self.queue.put(6)
        shutil.copy('{}'.format(self.spinrite_path), 'mnt/')
        time.sleep(2)

        self.queue.put(7)
        with open("mnt/AUTOEXEC.BAT", "r") as file:
            lines = file.readlines()
            lines[len(lines)-2] = "spinrite.exe\n"
        with open("mnt/AUTOEXEC.BAT", "w") as file:
            for line in lines:
                file.write(line)
        time.sleep(2)

        self.queue.put(8)
        subprocess.Popen(['sudo', 'umount', 'mnt/'])
        time.sleep(2)

        # DONE!
        self.queue.put(100)


if __name__ == '__main__':
    # if not root...kick out
    if not os.geteuid() == 0:
        sys.exit("\nYou must be root to run this application as the software needs access to your USB device\nplease use sudo and try again.\n")

    root = tk.Tk()
    window = GUI(root)
    window.pack(fill=tk.X, expand=True, anchor=tk.N)
    root.mainloop()