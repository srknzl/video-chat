# video-chat
Video Chat Over Network Using Gstreamer


## 1.1. Dependencies
* gstreamer
* GTK+3
* Python 2 (2.6 or later) or Python 3 (3.1 or later)
* gobject-introspection (needed for accessing gtk in python.)
* notify-send


Note for gobject: Recent versions of PyGObject and its dependencies are packaged by nearly all major Linux distributions. So, if you use Linux, you can probably get started by installing the package from the official repository for your distribution.

# Transporter- LAN video chat, text chat, file transfer application


## System Requirements
psmisc -> for killall command if you do not have it installed 
gstreamer -> for streaming video and audio, also for rendering them.
notify-send -> for visual notification of messages or app related information.
### gstreamer Installation:
```
sudo apt install v4l-utils

sudo apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

sudo apt install gstreamer1.0-plugins-*
```
### notify-send Installation
sudo apt-get install libnotify-bin