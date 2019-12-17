HOST=$1
PORT=$2
gst-launch-1.0 udpsrc address=$HOST port=$PORT caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, payload=(int)96, encoding-name=(string)H264" ! queue ! rtph264depay ! queue ! avdec_h264 ! queue ! videoconvert ! queue ! xvimagesink > /dev/null &
echo $! # pid of last backgrounded task, gstreamer in this case
