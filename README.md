# video-chat
Video Chat Over Network Using Gstreamer


## 1.1. Dependencies
* gstreamer
* GTK+3
* Python 2 (2.6 or later) or Python 3 (3.1 or later)
* gobject-introspection (needed for accessing gtk in python.)


Note for gobject: Recent versions of PyGObject and its dependencies are packaged by nearly all major Linux distributions. So, if you use Linux, you can probably get started by installing the package from the official repository for your distribution.

### gstreamer Installation:
```
sudo apt install v4l-utils

sudo apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

sudo apt install gstreamer1.0-plugins-*
```
### PygObject installation 

```
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```
or via pip
```
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
pip3 install pycairo
pip3 install PyGObject
```