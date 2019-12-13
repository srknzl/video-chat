import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from os import system, name
import time
transporterLogo = """
 _____                                      _            
/__   \_ __ __ _ _ __  ___ _ __   ___  _ __| |_ ___ _ __ 
  / /\/ '__/ _` | '_ \/ __| '_ \ / _ \| '__| __/ _ \ '__|
 / /  | | | (_| | | | \__ \ |_) | (_) | |  | ||  __/ |   
 \/   |_|  \__,_|_| |_|___/ .__/ \___/|_|   \__\___|_|   
                          |_|                            
"""


def clear():
    if name == 'nt':  # for windows
        system('cls')
    else:  # for mac and linux
        system('clear')


def print_options():
    print("1. Send message")
    print("2. Mailbox")
    print("3. Online people")
    print("4. Quit")


def get_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
            print("You are not connected to a network chat application will not work.")
    return IP


def send_announce():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as announce_s:
        announce_s.settimeout(0.2)
        announce_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        announce_s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        send_announce_packet_once(announce_s)
        time.sleep(1)
        send_announce_packet_once(announce_s)
        time.sleep(1)
        send_announce_packet_once(announce_s)


def send_announce_packet_once(_announce_socket):
    try:
        _announce_socket.sendto(("[" + str(username) + ", " + str(userip) + ", announce]").encode(
            "utf-8", errors="replace"), ('<broadcast>', 12345))
    except TimeoutError:
        pass


def send_response(_ip, _name):  # _ip is ip of other guy
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as response_s:
        response_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        response_s.connect((_ip, 12345))
        response_s.sendall(("[" + str(username) + ", " + str(userip) +
                            ", response]").encode("utf-8", errors="replace"))
        response_s.shutdown(socket.SHUT_RDWR)

def send_message(_ip, _payload):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as message_s:
        message_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        message_s.connect((_ip, 12345))
        message_s.sendall(
            ("[" + str(username) + ", " + str(userip) + ", message, " + str(_payload) + "]").encode("utf-8", errors="replace"))
        message_s.shutdown(socket.SHUT_RDWR)


def process_messages(_data):
    time.sleep(0.1) # Dont know why but necessary for correct working 
    decoded = _data.decode("utf-8", errors="replace")
    if decoded[0] == "[" and decoded[-1] == "]":
        decoded_striped = str(decoded[1:-1])  # Strip out square parantheses.
        decoded_splitted = decoded_striped.split(",")
        if len(decoded_splitted) < 3:
            print("Got an invalid message " + str(decode))
            return
        message_type = decoded_splitted[2].strip(' ')
        if message_type == 'announce':
            global lasttime, last_udp_packet
            lastip = last_udp_packet["ip"]
            lastname = last_udp_packet["name"]
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            # print("Last time:", time.time()-lasttime)
            # print("Last ip", lastip, "Ip", ip)
            # print("Last name", lastname, "Name", name)

            # print("(name, ip) != (username, userip)",
            #        (name, ip) != (username, userip))
            # print("(name, ip)",(name, ip))
            # print("(username, userip)",(username, userip))
            # print("(name, ip) not in online_people",
            #       (name, ip) not in online_people)
            # print("(name, ip) not in online_people and (name, ip) != (username, userip)",
            #       (name, ip) not in online_people and (name, ip) != (username, userip))

            if(time.time()-lasttime <= 3 and lastip == ip and lastname == name):
                pass
            # not me and also not in online list
            elif (name, ip) not in online_people and (name, ip) != (username, userip):
                online_people.add((name, ip))
                print("New online person:", name, ip)
                executor.submit(send_response, ip, name)
            lasttime = time.time()
            last_udp_packet["ip"] = ip
            last_udp_packet["name"] = name
        elif message_type == 'response':
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            if (name, ip) not in online_people:
                print("New online person:", name, ip)
                online_people.add((name, ip))
                
        elif message_type == 'message':
            if len(decoded_splitted) < 4:
                print("Got an invalid message " + str(decode))
                return
            name = decoded_splitted[0].strip(' ')
            ip = decoded_splitted[1].strip(' ')
            message = decoded_splitted[3].strip(' ')
            print(str(name) + ": " + str(message))
            if (name, ip) in messages:
                messages[(name, ip)].append(message)
            else:
                messages[(name, ip)] = [message]
            if (name, ip) not in online_people:
                print("New online person:", name, ip)
                online_people.add((name, ip))
        else:
            print("Got an invalid message " + str(decode))

    else:  # Invalid message
        print("Got an invalid message " + str(decode))


def listen_messages():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((get_ip(), 12345))
        sock.listen()
        while True:
            conn, addr = sock.accept()
            executor.submit(on_new_connection, conn, addr)


def listen_udp_messages():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)
        sock.bind(("", 12345))
        while True:
            data, addr = sock.recvfrom(1500)
            executor.submit(on_new_udp_connection, data, addr)


def on_new_connection(conn, addr):
    with conn:
        data = conn.recv(1500)
        if data:
            process_messages(data)


def on_new_udp_connection(data, addr):
    if addr != (userip, 12345):
        process_messages(data)


last_udp_packet = {
    "ip": "",
    "name": ""
}

lasttime = 0.0
messages = {}
online_people = set()
username = input("What is your name? \n")
userip = get_ip()

tcplistener = threading.Thread(target=listen_messages, daemon=True)
tcplistener.start()

udplistener = threading.Thread(target=listen_udp_messages, daemon=True)
udplistener.start()


executor = ThreadPoolExecutor(255)

announcer = threading.Thread(target=send_announce, daemon=True)
announcer.start()

while not username:
    print("Please enter a name!")
    username = input("What is your name? \n")

clear()
choice = None
flash_messages = ["Welcome to the transporter app. Have fun! \n"]
while choice != "4":
    clear()
    print(transporterLogo)
    for f_message in flash_messages:
        print(f_message)
    flash_messages.clear()
    print_options()
    choice = input("Select an option: \n")
    if choice == "1":  # Send message
        clear()
        if len(online_people) == 0:
            flash_messages.append("No one is online!\n")
            continue
        temp_dict = {}
        counter = 1
        for person in online_people:
            print(str(counter) + ". Name: " +
                  str(person[0]) + " IP: " + str(person[1]))
            temp_dict[counter] = person
            counter += 1
        person_num = input(
            "Enter a number corresponding to a person given above (To cancel enter cancel): \n")
        while not person_num.isdigit() or int(person_num) > (counter - 1) or int(person_num) < 1:
            if person_num == "cancel":
                break
            person_num = input("Invalid. Please enter again: \n")
        if person_num == "cancel":
            continue
        person_cho = temp_dict[int(person_num)]
        person_ip = person_cho[1]
        message = input("Please enter your message:\n")
        executor.submit(send_message, person_ip, message)
        flash_messages.append("Message on the way! \n")
    elif choice == "2":  # Mailbox
        clear()
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
        entry_num = input("Select an entry (To cancel enter cancel): \n")
        while not entry_num.isdigit() or int(entry_num) > (counter - 1) or int(entry_num) < 1:
            if entry_num == "cancel":
                break
            entry_num = input("Invalid. Select again \n")
        if entry_num == "cancel":
            continue
        entry_cho = temp_dict[int(entry_num)]
        flash_messages.append(str(entry_cho[0]) + " wrote: ")
        for message in messages[entry_cho]:
            flash_messages.append(">> " + str(message))
        flash_messages.append("\n")
    elif choice == "3":  # Online people
        if len(online_people) == 0:
            flash_messages.append("No one is online! \n")
            continue
        counter = 1
        for person in online_people:
            flash_messages.append(
                str(counter) + ". Name: " + str(person[0]) + " IP: " + str(person[1]))
            counter += 1
        flash_messages.append("\n")
    # elif choice == "5":  # Online people
    #     flash_messages.append(threading.active_count())
clear()
print("Goodbye!")
