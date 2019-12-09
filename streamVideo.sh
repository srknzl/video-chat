HOST=$1
PORT=$2

gst-launch-1.0 v4l2src ! queue ! videoconvert ! queue ! x264enc bitrate=500 speed-preset=superfast tune=zerolatency  ! queue  ! rtph264pay ! queue ! udpsink host=$HOST port=$PORT 
