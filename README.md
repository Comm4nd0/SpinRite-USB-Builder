# SpinRite-USB-Builder

This tool is a USB builder for SpinRite. 
It's purpose is to automate the task of downloading FreeDos, 
installing FreeDos a USB and adding your SpinWrite.exe to the USB too.

After running the tool your USB will be ready to use as a bootable device
straight away.

*Note: This too does need to be run as root! The reason is because it needs
access to your block devices and only root can do this by default.*

### OS
I've developed this tool on Ubuntu 17.10, however i don't see any reason why
it won't work with most versions of Linux. Let me know if you have any issues
or feel free to do a pull request.

### Prerequisites
##### SpinRite.exe
Go buy it from [grc.com](https://www.grc.com/). It's a GREAT tool by Steve Gibson.
##### Internet
The tool downloads FreeDos to your computer as part of the installation.
##### Python 3.X
The tool is written in Python3, it's a great language.
##### A USB
Yep, you'll need one of these...

### Install
Clone this repository
```bash
git clone https://github.com/Comm4nd0/SpinRite-USB-Builder.git
```
Run the installer
```bash
sudo ./install.sh
```
Run the tool!
```bash
sudo ./spinrite.py
```
And that's it.

###Instructions
After installing the tool make sure you have your USB inserted into your
computer. Then you can launch the tool with the following command:
```bash
sudo ./spinrite.py
```
1. Browse and select your SpinRite.exe file.
2. Select your USB device from the list.
3. Click 'Build'!

You will need an internet connection for the tool to work as the first thing
it does is downloads FreeDos to your computer. Speeds will vary depending on
d/l speeds. You'll see your USB detach and reattach but do not remove it
until the message says it's complete.

Hope you enjoy the tool and find it as useful as I do!