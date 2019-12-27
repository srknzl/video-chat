import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from os import system, name, path, walk, mkdir, remove, kill
import signal
import subprocess
import re
import time
import atexit
from enum import Enum


transporterLogo = """
 _____                                      _            
/__   \_ __ __ _ _ __  ___ _ __   ___  _ __| |_ ___ _ __ 
  / /\/ '__/ _` | '_ \/ __| '_ \ / _ \| '__| __/ _ \ '__|
 / /  | | | (_| | | | \__ \ |_) | (_) | |  | ||  __/ |   
 \/   |_|  \__,_|_| |_|___/ .__/ \___/|_|   \__\___|_|   
                          |_|                            
"""


#! UDP SECTION

class UdpMessageTypes(Enum):
    announce = 1
    allgroupsrequest = 2
    groupvideochatstart = 3
    groupvideochatleave = 4
    generalleave = 5

#! GENERAL UDP FUNCTION


def send_udp_packet(packet_type, groupname):  # General udp packet sending function
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_s:
        udp_s.settimeout(0.2)
        udp_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if packet_type == UdpMessageTypes.announce:
            send_announce_packet(udp_s)
            # time.sleep(1)
            send_announce_packet(udp_s)
            # time.sleep(1)
            # send_announce_packet(udp_s)
        elif packet_type == UdpMessageTypes.allgroupsrequest:
            send_allgroups_req_packet(udp_s)
            send_allgroups_req_packet(udp_s)
            # send_allgroups_req_packet(udp_s)
        elif packet_type == UdpMessageTypes.groupvideochatstart:
            send_group_videochat_start_packet(udp_s, groupname)
            send_group_videochat_start_packet(udp_s, groupname)
            # send_group_videochat_start_packet(udp_s, groupname)
        elif packet_type == UdpMessageTypes.groupvideochatleave:
            send_group_videochat_leave_packet(udp_s, groupname)
            send_group_videochat_leave_packet(udp_s, groupname)
            # send_group_videochat_leave_packet(udp_s, groupname)
        elif packet_type == UdpMessageTypes.generalleave:
            send_general_leave(udp_s)
            send_general_leave(udp_s)
        

# Send announce to everyone when logging in, via udp
def send_announce_packet(socket):
    try:
        socket.sendto(("[" + str(username) + ", " + str(userip) + ", announce]").encode(
            "utf-8", errors="replace"), ('<broadcast>', 12345))
    except Exception as e:
        print("An error occured when broadcasting", e)
        time.sleep(1)


# Send allgroups request to everyone, everyone send all their groups as reply, via udp
def send_allgroups_req_packet(socket):
    try:
        socket.sendto(("[" + str(username) + ", " + str(userip) + ", allgroups]").encode(
            "utf-8", errors="replace"), ('<broadcast>', 12345))
    except Exception as e:
        print("An error occured when broadcasting all groups request", e)
        time.sleep(1)


# Send everyone that I am starting a videochat in group 'groupname'
def send_group_videochat_start_packet(socket, groupname):
    try:
        socket.sendto(("[" + str(username) + ", " + str(userip) + ", announce_videochat_enter, " + str(groupname) + "]").encode(
            "utf-8", errors="replace"), ('<broadcast>', 12345))
    except Exception as e:
        print("An error occured when broadcasting video start message", e)
        time.sleep(1)


# Send everyone that I am leaving a videochat in group 'groupname'
def send_group_videochat_leave_packet(socket, groupname):
    try:
        socket.sendto(("[" + str(username) + ", " + str(userip) + ", announce_videochat_leave, " + str(groupname) + "]").encode(
            "utf-8", errors="replace"), ('<broadcast>', 12345))
    except Exception as e:
        print("An error occured when broadcasting video start message", e)
        time.sleep(1)


def send_general_leave(socket): # Send to everyone that I am leaving the application
    try:
        socket.sendto(("[" + str(username) + ", " + str(userip) + ", general_leave]").encode(
            "utf-8", errors="replace"), ('<broadcast>', 12345))
    except Exception as e:
        print("An error occured when broadcasting general leave message", e)
        time.sleep(1)    


#! TCP SECTION


class TcpMessageTypes(Enum):
    response = 1
    message = 2
    call = 3
    acceptcall = 4
    startcall = 5
    cancelcall = 6
    mygroups = 7
    responsegroupchatenter = 8
    videochatleave = 9

#! GENERAL TCP FUNCTION


# General tcp packet sending function
def send_tcp_packet(packet_type, ip, payload, groups, groupname):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_s:
        if packet_type == TcpMessageTypes.response:
            send_response_packet(tcp_s, ip)
        elif packet_type == TcpMessageTypes.message:
            send_message_packet(tcp_s, ip, payload)
        elif packet_type == TcpMessageTypes.call:
            send_call_packet(tcp_s, ip)
        elif packet_type == TcpMessageTypes.acceptcall:
            send_accept_call_packet(tcp_s, ip)
        elif packet_type == TcpMessageTypes.startcall:
            send_start_call_packet(tcp_s, ip)
        elif packet_type == TcpMessageTypes.cancelcall:
            send_cancel_call_packet(tcp_s, ip)
        elif packet_type == TcpMessageTypes.mygroups:
            send_my_groups_packet(tcp_s, ip, groups)
        elif packet_type == TcpMessageTypes.responsegroupchatenter:
            send_response_videochat_enter_packet(tcp_s, ip, groupname)
        elif packet_type == TcpMessageTypes.videochatleave:
            send_videochat_leave(tcp_s, ip)


# Send response message to a user with ip 'ip', via tcp
def send_response_packet(socket, ip):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(("[" + str(username) + ", " + str(userip) +
                        ", response]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when responding to an announce message", e)
        time.sleep(1)


# Send message 'payload' to a user with ip 'ip', via tcp
def send_message_packet(socket, ip, payload):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", message, " + str(payload) + "]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when message is sending", e)
        time.sleep(1)


# Send call request message to a user with ip 'ip', via tcp
def send_call_packet(socket, ip):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", call]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when sending call message", e)
        time.sleep(1)


# Send ok message to a call request, sent after getting a call to a user with ip 'ip', via tcp
def send_accept_call_packet(socket, ip):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", acceptcall]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when sending accept call message", e)
        time.sleep(1)


# Starting response, sent after call is accepted by other party, to a user with ip 'ip', via tcp
def send_start_call_packet(socket, ip):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", startcall]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when sending start call message", e)
        time.sleep(1)


# Sent when 1-1 call is canceled, to a user with ip 'ip', via tcp
def send_cancel_call_packet(socket, ip):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", cancelcall]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when sending cancel call message", e)
        time.sleep(1)


# Send my groups 'groups' to a person that has requested my groups with ip 'ip', via tcp
def send_my_groups_packet(socket, ip, groups):
    try:
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        if len(groups) == 0:
            socket.sendall(
                ("[" + str(username) + ", " + str(userip) + ", mygroups]").encode("utf-8", errors="replace"))
        else:
            mygroups_string = ", ".join(groups)
            socket.sendall(
                ("[" + str(username) + ", " + str(userip) + ", mygroups, " + mygroups_string + "]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print("An error occured when sending my groups", e)
        time.sleep(1)


def send_response_videochat_enter_packet(socket, ip, groupname): # Send to the newly entered person to the group chat in order he or she to know who are already group chatting  
    try:
        socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", response_videochat_enter, " + str(groupname) + "]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print(
            "An error occured when sending videochat attendence info to someoone", e)
        time.sleep(1)


def send_videochat_leave(socket, ip): # Send to the person I am currently having video chat with, to make kill his or her render processes
    try:
        socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.connect((ip, 12345))
        socket.sendall(
            ("[" + str(username) + ", " + str(userip) + ", videochat_leave]").encode("utf-8", errors="replace"))
        socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print(
            "An error occured when sending videochat leave info to someoone", e)
        time.sleep(1)

#! Communication related


def process_messages(data):  # Process incoming data
    decoded = data.decode("utf-8", errors="replace")
    print(decoded)
    if decoded[0] == "[" and decoded[-1] == "]":
        decoded_striped = str(decoded[1:-1])  # Strip out square parantheses.
        decoded_splitted = decoded_striped.split(",")
        if len(decoded_splitted) < 3:
            print("Got an invalid message " + str(decode))
            return
        message_type = decoded_splitted[2].strip(' ')
        if message_type == 'announce':
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            add_new_people(name, ip)
            if ip != userip:
                executor.submit(send_response, ip)
        elif message_type == 'response':
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            add_new_people(name, ip)
        elif message_type == 'call':
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            subprocess.run(["notify-send", "New call from " +
                            name + ".\n" + "To accept, go to calls."])
            if (name, ip) not in calls:
                calls.append((name, ip))
        elif message_type == 'acceptcall':
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            print("Call accepted by", name, "starting video chat...")
            send_start_call(ip)
            start_video_chat(ip)
        elif message_type == 'startcall':
            global start_call_in_three_seconds
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            if ip == accepted_call_ip:
                start_call_in_three_seconds = True
        elif message_type == "cancelcall":
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            subprocess.run(
                ["notify-send", name + " canceled a call."])
            try:
                calls.remove((name, ip))
            except ValueError:
                pass
        elif message_type == "allgroups":
            ip = decoded_splitted[1].strip(' ')
            if ip != userip:
                sync_groups()
                send_my_groups_to(ip, groups)
        elif message_type == "mygroups":
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            for i in range(3, len(decoded_splitted)):
                group = decoded_splitted[i].strip(' ')
                all_groups.add(group)
        elif message_type == "announce_videochat_enter":
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            groupname = decoded_splitted[3].strip(' ')
            # print("call_started",call_started)
            # print("active_video_chat_group",active_video_chat_group)
            # print("groupname", groupname)
            # print("active_video_chat_attendees",active_video_chat_attendees)
            # print("ip",ip, "userip",userip)
            if call_started and active_video_chat_group == groupname and (name, ip) not in active_video_chat_attendees and ip != userip:
                active_video_chat_attendees.append((name, ip))
                render_video_chat(name, ip)
                send_response_videochat_enter_packet(ip, groupname)
        elif message_type == "announce_videochat_leave":
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            groupname = decoded_splitted[3].strip(' ')
            # subprocess.run(["notify-send", name + " leaved the video chat."])
            if active_video_chat_group == groupname and (name, ip) in active_video_chat_attendees:
                active_video_chat_attendees.remove((name, ip))
                subprocess.run(["notify-send", name + " left the video chat."])
                if (name, ip) in active_video_chat_attendee_processes:
                    processes = active_video_chat_attendee_processes[(
                        name, ip)]
                    for process in processes:
                        kill(process, signal.SIGKILL)
                    del active_video_chat_attendee_processes[(name, ip)]
        elif message_type == "response_videochat_enter":
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            groupname = decoded_splitted[3].strip(' ')
            if active_video_chat_group != "" and call_started and groupname == active_video_chat_group and (name, ip) not in active_video_chat_attendees:
                active_video_chat_attendees.append((name, ip))
                render_video_chat(name, ip)
        elif message_type == 'message':
            if len(decoded_splitted) < 4:
                print("Got an invalid message " + str(decode))
                return
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            message = decoded_splitted[3].strip(' ')

            subprocess.run(
                ["notify-send", "New message from " + name + ", Message: " + message])
            # print(str(name) + ": " + str(message))
            if (name, ip) in messages:
                messages[(name, ip)].append(message)
            else:
                messages[(name, ip)] = [message]
            add_new_people((name, ip))
        elif message_type == "generalleave":
            ip = decoded_splitted[1].strip(' ')
            for person in online_people:
                if person[1] == ip:
                    subprocess.run(
                    ["notify-send", person[0] + " with ip " + person[1] + " has left the application." + message])
                    online_people.remove(person)
        elif message_type == "videochatleave":
            global close_video_chat
            ip = decoded_splitted[1].strip(' ')
            if active_video_chat_friend_ip == ip:
                close_video_chat = True
        else:
            print("Got an invalid message " + str(decode))

    else:  # Invalid message
        print("Got an invalid message " + str(decode))


def listen_tcp_messages():  # Open a tcp socket and wait, every new connection is handled via a new thread submission to executor pool
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((get_ip(), 12345))
        sock.listen()
        while True:
            conn, addr = sock.accept()
            executor.submit(on_new_tcp_connection, conn, addr)


def listen_udp_messages():  # Open a udp socket and wait, every new connection is handled via a new thread submission to executor pool
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
        sock.bind(("", 12345))
        while True:
            data, addr = sock.recvfrom(1500)
            executor.submit(on_new_udp_connection, data, addr)


# Reads data from tcp connection than sends data to process_messages
def on_new_tcp_connection(conn, addr):
    with conn:
        data = conn.recv(1500)
        if data:
            # time.sleep(0.1)
            process_messages(data)


# Reads data from udp connection than sends data to process_messages
def on_new_udp_connection(data, addr):
    if addr != (userip, 12345):
        # time.sleep(0.1)
        process_messages(data)


def add_new_people(name, ip):  # When a response or announce comes, this is called
    found = False
    for people in online_people:
        # If there is a person with same ip, username is changed.
        if people[1] == ip:
            found = True
            # print("Found ", people, "to have ip ",ip)
            if people[0] != name:
                # Remove old person with old username
                online_people.remove(people)
                # Add a new person with new username
                online_people.add((name, ip))
                subprocess.run(
                    ["notify-send", "User with ip " + ip + " changed his name new name is " + name])

    # If no one is found with the same ip and the new people is not me, add it to online people
    if not found and (name, ip) != (username, userip):
        subprocess.run(
            ["notify-send", "New person online: " + name + ", Ip: " + ip])
        online_people.add((name, ip))


#! Video chat related

def start_video_chat(person_ip):  # Start video chat with a person with ip 'person_ip'
    global call_started, close_video_chat
    call_started = True
    active_video_chat_friend_ip = person_ip
    person_ip_splitted = person_ip.split(".")
    friend_ip = "234." + str(person_ip_splitted[1]) + "." + str(
        person_ip_splitted[2]) + "." + str(person_ip_splitted[3])

    user_ip_splitted = userip.split(".")

    own_ip = "234." + str(user_ip_splitted[1]) + "." + str(
        user_ip_splitted[2]) + "." + str(user_ip_splitted[3])

    subprocess.run(["killall", "-9", "gst-launch-1.0"],  # Kill any other remaining gstreamer instances if any
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Stream own video and audio, render own video, render audio and video of friend
    # Multicast ip is used 234. + last part of the ip
    streamVideoProcess = subprocess.Popen(
        ["bash", "streamVideo.sh", own_ip, "40000"], stdout=subprocess.PIPE)
    outs, errs = streamVideoProcess.communicate()
    # These pid's are used to kill gstreamer processes later on
    streamVideoProcessPid = int(outs.decode())

    streamAudioProcess = subprocess.Popen(
        ["bash", "streamAudio.sh", own_ip, "50000"], stdout=subprocess.PIPE)
    outs, errs = streamAudioProcess.communicate()
    streamAudioProcessPid = int(outs.decode())

    renderOwnVideoProcess = subprocess.Popen(
        ["bash", "renderVideo.sh", own_ip, "40000"], stdout=subprocess.PIPE)
    outs, errs = renderOwnVideoProcess.communicate()
    renderOwnVideoProcessPid = int(outs.decode())

    renderVideoProcess = subprocess.Popen(
        ["bash", "renderVideo.sh", friend_ip, "40000"], stdout=subprocess.PIPE)
    outs, errs = renderVideoProcess.communicate()
    renderVideoProcessPid = int(outs.decode())

    renderAudioProcess = subprocess.Popen(
        ["bash", "renderAudio.sh", friend_ip, "50000"], stdout=subprocess.PIPE)
    outs, errs = renderAudioProcess.communicate()
    renderAudioProcessPid = int(outs.decode())

    print("Video chat started...")

    inp = input("Press c to close video chat")
    while inp != "c" or close_video_chat:
        inp = input("Press c to close video chat")
    close_video_chat = False
    print("Closing")
    call_started = False
    active_video_chat_friend_ip = ""
    # print(streamVideoProcessPid,streamAudioProcessPid,renderOwnVideoProcessPid,renderVideoProcessPid,renderAudioProcessPid)
    # Kill gstreamer processes
    kill(streamVideoProcessPid, signal.SIGTERM)
    kill(streamAudioProcessPid, signal.SIGTERM)
    kill(renderOwnVideoProcessPid, signal.SIGTERM)
    kill(renderVideoProcessPid, signal.SIGTERM)
    kill(renderAudioProcessPid, signal.SIGTERM)

    print("Done closing")


# Render other group members' video audio and add to attendees object
def render_video_chat(name, ip):
    global active_video_chat_attendee_processes
    person_ip_splitted = ip.split(".")
    friend_ip = "234." + str(person_ip_splitted[1]) + "." + str(
        person_ip_splitted[2]) + "." + str(person_ip_splitted[3])
    # Render audio and video of friend
    # Multicast ip is used 234. + last part of the ip
    renderVideoProcess = subprocess.Popen(
        ["bash", "renderVideo.sh", friend_ip, "40000"], stdout=subprocess.PIPE)
    outs, errs = renderVideoProcess.communicate()
    renderVideoProcessPid = int(outs.decode())

    renderAudioProcess = subprocess.Popen(
        ["bash", "renderAudio.sh", friend_ip, "50000"], stdout=subprocess.PIPE)
    outs, errs = renderAudioProcess.communicate()
    renderAudioProcessPid = int(outs.decode())

    # Add the new person to process list to be killed when group chat ends.
    if (name, ip) not in active_video_chat_attendee_processes:
        active_video_chat_attendee_processes[(name, ip)] = [
            renderVideoProcessPid, renderAudioProcessPid]


def start_group_video_chat(groupname):  # Starts group video chat
    global active_video_chat_attendees, active_video_chat_group, call_started
    if groupname not in groups:
        print("GroupChat: You are not in group", groupname)
        sync_groups()
        print_groups(None)
        return False
    subprocess.run(["killall", "-9", "gst-launch-1.0"],  # Kill any running gstreamer in the background
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    call_started = True
    active_video_chat_attendees = []  # Reset attendees
    active_video_chat_group = groupname  # Set current group chat group name
    return True


# Render my own video, also stream my video and audio
def launch_group_chat():
    global active_video_chat_attendees, active_video_chat_attendee_processes, active_video_chat_group, call_started
    call_started = True

    user_ip_splitted = userip.split(".")

    own_ip = "234." + str(user_ip_splitted[1]) + "." + str(
        user_ip_splitted[2]) + "." + str(user_ip_splitted[3])

    streamVideoProcess = subprocess.Popen(
        ["bash", "streamVideo.sh", own_ip, "40000"], stdout=subprocess.PIPE)
    outs, errs = streamVideoProcess.communicate()
    streamVideoProcessPid = int(outs.decode())

    streamAudioProcess = subprocess.Popen(
        ["bash", "streamAudio.sh", own_ip, "50000"], stdout=subprocess.PIPE)
    outs, errs = streamAudioProcess.communicate()
    streamAudioProcessPid = int(outs.decode())

    renderOwnVideoProcess = subprocess.Popen(
        ["bash", "renderVideo.sh", own_ip, "40000"], stdout=subprocess.PIPE)
    outs, errs = renderOwnVideoProcess.communicate()
    renderOwnVideoProcessPid = int(outs.decode())

    print("Group video chat started...")

    inp = input("Press c to close video chat\n")
    # print("Input is ",inp)
    while inp != "c":
        inp = input("Press c to close video chat\n")
    print("Closing group chat")
    send_group_video_chat_leave(active_video_chat_group)
    call_started = False
    active_video_chat_group = ""

    kill(streamVideoProcessPid, signal.SIGKILL)
    kill(streamAudioProcessPid, signal.SIGKILL)
    kill(renderOwnVideoProcessPid, signal.SIGKILL)
    for user_entry in active_video_chat_attendee_processes:
        processes = active_video_chat_attendee_processes[user_entry]
        for pid in processes:
            # print("Killing",pid)
            kill(pid, signal.SIGKILL)
    active_video_chat_attendees = []
    active_video_chat_attendee_processes = {}
    print("Done closing group chat")

#! Groups related


def enter_group(groupname, flash_messages):  # Enter a group
    sync_groups()
    if not isAlphaNumeric(groupname):
        flash_messages.append(
            "EnterGroup: The groupname you entered is not alphanumeric.")
    if groupname not in groups:
        f = open("groups/" + groupname, "w+")
        f.close()
        flash_messages.append("EnterGroup: Entered group " + groupname)
    else:
        flash_messages.append("EnterGroup: You are already in this group")


def leave_group(groupname, flash_messages):  # Leave a group
    sync_groups()
    if not isAlphaNumeric(groupname):
        flash_messages.append(
            "LeaveGroup: The groupname you entered is not alphanumeric.")
        return
    if groupname not in groups:
        flash_messages.append("LeaveGroup: You are not in that group.")
    else:
        flash_messages.append("LeaveGroup: You left group " + groupname)
        remove("groups/" + groupname)


# Print groups if flash_messages is None, else put it inside flash messages
def print_groups(flash_messages):
    if flash_messages != None:
        if len(groups) != 0:
            groups_string = ", ".join(groups)
            flash_messages.append(
                "Groups: You are in these groups: " + groups_string + "\n")
        else:
            flash_messages.append("Groups: You are not in any group")
    else:
        if len(groups) != 0:
            groups_string = ", ".join(groups)
            print("Groups: You are in these groups: " + groups_string + "\n")
        else:
            print("Groups: You are not in any group")


def sync_groups():  # Update groups from groups folder
    global groups
    groups_isdir = path.isdir("groups")
    groups_isfile = path.isfile("groups")
    if groups_isfile:
        remove("groups")
        try:
            mkdir("groups")
        except OSError:
            print("Creation of the directory 'groups' failed")
            time.sleep(2)
        else:
            print("Successfully created the directory 'groups'")
            time.sleep(2)
    elif groups_isdir:
        for (root, dirs, files) in walk("groups"):
            for filename in files:
                if filename == "c":  # Do not allow a group called 'c' as it is used as cancel character.
                    files.remove(filename)
            groups = list(filter(isAlphaNumeric, files))

    else:
        try:
            mkdir("groups")
        except OSError:
            print("Creation of the directory 'groups' failed")
            time.sleep(2)
        else:
            print("Successfully created the directory 'groups'")
            time.sleep(2)


#! Misc functions

def on_exit():  # Kill all gstreamer instances when exiting
    subprocess.run(["killall", "-9", "gst-launch-1.0"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    send_udp_packet(UdpMessageTypes.generalleave)
    if active_video_chat_group != "":
        send_udp_packet(UdpMessageTypes.groupvideochatleave, active_video_chat_group)
    if active_video_chat_friend_ip != "":
        send_tcp_packet(TcpMessageTypes.videochatleave, active_video_chat_friend_ip)
    # Todo send leave message from 1-1 video chat if attended
    # Todo send leave message from group chat if attended
    # Todo Send general leave message to delete the person from online people 


def clear():  # Clear terminal
    if name == 'nt':  # for windows
        system('cls')
    else:  # for mac and linux
        system('clear')


def print_options():  # Print main menu
    print("1. Send message")
    print("2. Mailbox")
    print("3. Online people")
    print("4. Start video chat")
    print("5. Pending video calls")
    print("6. Manage Groups")
    print("7. Send message to a group")
    print("8. Attend video chat in a group")
    print("9. See group video chats going on. ")
    print("q. Quit")


def print_group_manage_options():  # Manage Group Options
    print("1. List of all groups")
    print("2. List of groups I attended")
    print("3. Enter a group")
    print("4. Leave a group")
    print("c. Cancel")


def isAlphaNumeric(word):  # Filter function that checks if a word is alphanumeric
    # Used to ensure group names do not cause problems when sending them in the protocol messages
    if re.fullmatch("^[a-zA-Z0-9_]+$", word):
        return True
    else:
        return False


def get_ip():  # Get my ip in the network, tries to connect to an address via a socket, with that acquires the ip.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
            print("You are not connected to a network chat application will not work.")
    return IP


def init(): # Starts tcp and udp listeners, starts announcer thread, registers on exit function
    tcplistener = threading.Thread(target=listen_tcp_messages, daemon=True)
    tcplistener.start()

    udplistener = threading.Thread(target=listen_udp_messages, daemon=True)
    udplistener.start()

    announcer = threading.Thread(target=send_udp_packet, args=(
        UdpMessageTypes.announce), daemon=True)
    announcer.start()
    atexit.register(on_exit)


def choose_a_username(): # Requires user to choose a username
    while not username:
        print("Please enter a name!")
    username = input("What is your name? \n")

#! Main Code

#! Global vars
messages = {}
sent_messages = {}

calls = []
start_call_in_three_seconds = False
accepted_call_ip = ""
call_started = False
close_video_chat = False

online_people = set()
# online_people.add(("serkan", "192.168.43.224"))
username = input("What is your name? \n")
userip = get_ip()

executor = ThreadPoolExecutor(255)

all_groups = set()
groups = []
active_video_chat_group = ""
active_video_chat_attendees = []
active_video_chat_attendee_processes = {}

active_video_chat_friend_ip = "" # For 1-1 video chat, leaving cause killing of video and audio rendering of the leaving person.
#! Init code

init() # Starts tcp and udp listeners, execute announcer thread, registers on exit function
choose_a_username() # Choose a username
sync_groups()

#! Main loop 

choice = None
flash_messages = ["Welcome to the transporter app. Have fun! \n"]
while choice != "q":
    clear()
    print(transporterLogo)
    if call_started:
        if active_video_chat_group != "":
            print("You are in video chat in group", active_video_chat_group)
        print("Press c to close video chat")
    for f_message in flash_messages:
        print(f_message)
    flash_messages.clear()
    print_options()
    choice = input("Select an option: \n")
    if choice == "1":  # Send message
        clear()
        print("------------------Send Message------------------ \n\n")
        if len(online_people) == 0:
            flash_messages.append("No one is online!\n")
            continue
        temp_dict = {}
        counter = 1
        print("Online people: \n")
        for person in online_people:
            print(str(counter) + ". Name: " +
                  str(person[0]) + " IP: " + str(person[1]))
            temp_dict[counter] = person
            counter += 1

        print()
        person_num = input(
            "Select a person by number. \nTo cancel, type 'c' \n")
        while not person_num.isdigit() or int(person_num) > (counter - 1) or int(person_num) < 1:
            if person_num == "c":
                break
            person_num = input("Invalid person number. Please enter again: \n")
        if person_num == "c":
            continue
        person_cho = temp_dict[int(person_num)]
        person_ip = person_cho[1]

        if person_cho in sent_messages:
            print("You wrote before: ")
            for message in sent_messages[person_cho]:
                print(">> " + str(message))

        message = input("Please enter your message:\n")
        if person_cho in sent_messages:
            sent_messages[person_cho].append(message)
        else:
            sent_messages[person_cho] = [message]
        executor.submit(send_message, person_ip, message)
        print("Message sent! \n")

        while True:
            sendAgain = input("Send again ? [y/n]:")
            while sendAgain.capitalize() != "Y" and sendAgain.capitalize() != "N":
                print("Invalid answer, try again.")
                sendAgain = input("Send again ? [y/n]:")
            if sendAgain.capitalize() == "Y":
                message = input("Please enter your message:\n")
                if person_cho in sent_messages:
                    sent_messages[person_cho].append(message)
                else:
                    sent_messages[person_cho] = [message]
                executor.submit(send_message, person_ip, message)
                print("Message sent! \n")
            elif sendAgain.capitalize() == "N":
                break

    elif choice == "2":  # Mailbox
        clear()
        print("------------------Mailbox------------------ \n\n")

        if len(messages.keys()) == 0:
            flash_messages.append("No message! \n")
            continue
        temp_dict = {}
        counter = 1
        for entry in messages:
            print(str(counter) + ". " + "Name: " +
                  entry[0] + " IP:" + entry[1])
            temp_dict[counter] = entry
            counter += 1
        entry_num = input("Select an entry.\nTo cancel, type 'c': \n")
        while not entry_num.isdigit() or int(entry_num) > (counter - 1) or int(entry_num) < 1:
            if entry_num == "c":
                break
            entry_num = input("Invalid. Select again \n")
        if entry_num == "c":
            continue
        entry_cho = temp_dict[int(entry_num)]
        flash_messages.append(str(entry_cho[0]) + " wrote: ")
        for message in messages[entry_cho]:
            flash_messages.append(">> " + str(message))
        flash_messages.append("\n")
    elif choice == "3":  # Online people
        flash_messages.append("Online People\n")

        if len(online_people) == 0:
            flash_messages.append("No one is online! \n")
            continue
        counter = 1
        for person in online_people:
            flash_messages.append(
                str(counter) + ". Name: " + str(person[0]) + " IP: " + str(person[1]))
            counter += 1
        flash_messages.append("\n")
    elif choice == "4":  # Video chat
        clear()
        print("------------------Video Chat------------------ \n\n")
        if len(online_people) == 0:
            flash_messages.append("No one is online!\n")
            continue
        temp_dict = {}
        counter = 1
        print("Online people: \n")
        for person in online_people:
            print(str(counter) + ". Name: " +
                  str(person[0]) + " IP: " + str(person[1]))
            temp_dict[counter] = person
            counter += 1

        print()
        person_num = input(
            "Select a person by number. \nTo cancel, type 'c' \n")
        while not person_num.isdigit() or int(person_num) > (counter - 1) or int(person_num) < 1:
            if person_num == "c":
                break
            person_num = input("Invalid person number. Please enter again: \n")
        if person_num == "c":
            continue
        if call_started:
            flash_messages.append("First, end your ongoing video chat.")
            continue
        person_cho = temp_dict[int(person_num)]
        person_name = person_cho[0]
        person_ip = person_cho[1]

        send_call(person_ip)
        print("Calling", person_name + ".", "Waiting for response...")
        endCall = input("To cancel call, type 'c'.")
        while endCall != "c" and not call_started:
            print("Invalid answer, try again.")
            endCall = input("To cancel call, type 'c'.")
        if not call_started:
            send_cancel_call(person_ip)
            flash_messages.append("Call canceled.")
    elif choice == "5":  # Calls
        clear()
        print("------------------Pending calls------------------ \n\n")
        if len(calls) == 0:
            flash_messages.append("No pending calls!\n")
            continue
        for i in range(len(calls)):
            print(str(i+1)+".", "Name:", calls[i][0], "Ip:", calls[i][1])
        person_num = input("Select a person to answer. To cancel, type 'c'.\n")

        while not person_num.isdigit() or int(person_num) > len(calls) or int(person_num) < 1:
            if person_num == "c":
                break
            person_num = input("Invalid person number. Please enter again: \n")
        if person_num == "c":
            continue
        if call_started:
            flash_messages.append("First, end your ongoing video chat.")
            continue
        will_be_called_person = calls[int(person_num)-1]
        try:
            calls.remove(will_be_called_person)
        except ValueError:
            pass
        start_call_in_three_seconds = False
        accepted_call_ip = will_be_called_person[1]
        send_accept_call(will_be_called_person[1])  # ip
        print("Please wait..")
        time.sleep(3)
        if start_call_in_three_seconds:
            print("Video call starting... ")
            executor.submit(start_video_chat, will_be_called_person[1])
        else:
            flash_messages.append("No respond from other side in 3 seconds.")
    elif choice == "6":  # Manage Groups
        clear()
        print("------------------Manage Groups------------------ \n\n")
        sync_groups()
        print_groups(flash_messages)
        flash_messages = []
        while True:
            clear()
            for message in flash_messages:
                print(message)
            flash_messages.clear()
            print_group_manage_options()
            gchoice = input("Choose an action: \n")
            if gchoice == "c":
                break
            if gchoice == "1":  # List of all groups
                print("Syncing groups please wait 3 seconds..")
                all_groups.clear()
                send_allgroups_request()
                print("3")
                time.sleep(1)
                print("2")
                time.sleep(1)
                print("1")
                time.sleep(1)
                sync_groups()
                for group in groups:
                    all_groups.add(group)
                if len(all_groups) == 0:
                    flash_messages.append("No groups found")
                else:
                    all_groups_string = ", ".join(all_groups)
                    flash_messages.append("All groups: " + all_groups_string)
            elif gchoice == "2":  # List of groups I attended
                sync_groups()
                print_groups(flash_messages)
            elif gchoice == "3":  # Enter a group
                sync_groups()
                print_groups(None)
                groupname = input(
                    "Enter group name to enter. Remember that only alphanumeric groups are accepted. To cancel type 'c'\n")
                if groupname == "c":
                    continue
                enter_group(groupname, flash_messages)
            elif gchoice == "4":  # Leave a group
                sync_groups()
                print_groups(None)
                groupname = input(
                    "Enter group name to leave. Remember that only alphanumeric groups are accepted. To cancel type 'c'\n")
                if groupname == "c":
                    continue
                leave_group(groupname, flash_messages)
    elif choice == "7":  # todo Send message to a group
        pass
    elif choice == "8":  # Attend video chat in a group
        clear()
        print("------------------Attend Group Video Chat------------------ \n\n")
        if call_started:
            flash_messages.append("First, end your ongoing video chat.")
            continue
        sync_groups()
        print_groups(None)
        group = input("Enter a group name. To cancel type 'c'.\n")
        if group == "c":
            continue
        while not start_group_video_chat(group):
            group = input("Enter a group name. To cancel type 'c'.\n")
            if group == "c":
                break
        # Announce that I am started video chat
        send_udp_packet(UdpMessageTypes.groupvideochatstart, groupname)
        # Render my own video, also stream my video and audio
        launch_group_chat()
    elif choice == "9":  # todo See group video chats going on.
        pass
    elif choice == "t":  # ! testing purposes
        clear()
        print("------------------Testing------------------ \n\n")
        if len(online_people) == 0:
            flash_messages.append("No one is online!\n")
            continue
        temp_dict = {}
        counter = 1

        print("Online people: \n")
        for person in online_people:
            print(str(counter) + ". Name: " +
                  str(person[0]) + " IP: " + str(person[1]))
            temp_dict[counter] = person
            counter += 1

        print()
        person_num = input(
            "Select a person by number. \nTo cancel, type 'c' \n")
        while not person_num.isdigit() or int(person_num) > (counter - 1) or int(person_num) < 1:
            if person_num == "c":
                break
            person_num = input("Invalid person number. Please enter again: \n")
        if person_num == "c":
            continue
        person_cho = temp_dict[int(person_num)]
        person_name = person_cho[0]
        person_ip = person_cho[1]
        # todo: Add testing code
        # executor.submit(send_response,person_ip)
        # responser = threading.Thread(target=send_response, args=[
        #                              person_ip], daemon=True)
        # responser.start()

    # elif choice == "5":  # Online people
    #     flash_messages.append(threading.active_count())
clear()
print("Goodbye!")
