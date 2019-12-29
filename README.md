# video-chat
Video Chat Over Network Using Gstreamer


## 1.1. Dependencies

* gstreamer
* Python 3 (3.5 or later)
* notify-send



# Transporter- LAN video chat, text chat, file transfer application

* Groups folder holds the currently attended groups. So please do not put a folder called groups near main.py. Otherwise, the script  

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

### Possible problems 

x264enc not found: 
sudo apt-get install gstreamer1.0-plugins-ugly

avdev_h264 no element: 
sudo apt install gstreamer1.0-libav
