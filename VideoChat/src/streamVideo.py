import subprocess
import atexit

p = subprocess.Popen(["bash","streamVideo.sh","234.4.4.4","1000"],stdout=subprocess.DEVNULL)

def closeVideoChat():
    print("Closing")
    p.kill()
    subprocess.run(["killall", "-9", "gst-launch-1.0"])


atexit.register(closeVideoChat)
# outs, errs = p.communicate()
# print(outs, errs)


inp = input("Press c to close video chat")
while inp != "c":
    inp = input("Press c to close video chat")