import threading
import socket as s
import sys, tty, termios
import os
import zlib
import struct
import time

from client import ClientState, client_settings
from client_utility import create_packet, extract_packet

def request_connection():

    client_settings.client_state = ClientState.CONNECTING

    packet = create_packet('Connection Request', client_settings.SERVER_PORT)

    print("request_connection packet: ", packet)

    while client_settings.client_state == ClientState.CONNECTING:
        client_settings.client_socket.sendto(packet, (client_settings.SERVER_ADDRESS, client_settings.SERVER_PORT))
        time.sleep(.1)

def wait_for_connection_update():

    while client_settings.client_state == ClientState.CONNECTING:

        packet = client_settings.client_socket.recv(1024)

        print("wait_for_connection_update packet: ", packet)
        
        message, udp_header, correct_checksum, current_checksum = extract_packet(packet)

        #Connection Accepted:9:59000

        message = message.split(':')

        outcome = message[0]

        index = int(message[1])

        assigned_server_port = int(message[2])

        print("Outcome: ", outcome, "Index: ", index, "port: ", assigned_server_port)

        if correct_checksum == current_checksum:
            if outcome == 'Connection Accepted':
                client_settings.assigned_server_port = assigned_server_port
                client_settings.index = index
                print("client_settings: ", client_settings.index, client_settings.assigned_server_port)
                client_settings.client_state = ClientState.CONNECTED
                threading.Thread(target=client_receive, args=())
                print('Connected')
            elif outcome == 'Connection Denied':
                client_settings.client_state = ClientState.DISCONNECTED
                print("Your connection request was denied by server")


def client_receive():

    while client_settings.client_state != ClientState.DISCONNECTED:
        try:
            packet = client_settings.client_socket.recv(1024)

            message, udp_header, correct_checksum, current_checksum = extract_packet(packet)

            print("client_receive message: ", message)

            if correct_checksum == current_checksum:
                if message == 'You are disconnected':
                    print("client_receive disconnect")
                    client_settings.client_state = ClientState.DISCONNECTED
                else:
                    os.system('clear')
                    print("\r", message, end="")
                    time.sleep(.02)
        except Exception as e:
            print(e)


def getch(char_width=1):
    '''get a fixed number of typed characters from the terminal. 
    Linux / Mac only'''
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(char_width)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def client_send():

    while client_settings.client_state == ClientState.CONNECTED:

        key = ord(getch())
        
        if key == 113: #disconnect
            attempts_to_disconnect = 0
            while client_settings.client_state != ClientState.DISCONNECTED:

                if attempts_to_disconnect > 1000:
                    print("client_send disconnect")
                    client_settings.client_state = ClientState.DISCONNECTED

                packet = str(key).encode()

                udp_header = struct.pack("!IIII", client_settings.CLIENT_PORT, client_settings.assigned_server_port, len(packet), zlib.crc32(packet))
        
                udp_packet = udp_header + packet

                print(udp_packet)

                client_settings.client_socket.sendto(udp_packet, (client_settings.SERVER_ADDRESS, client_settings.assigned_server_port))

                attempts_to_disconnect += 1
                print(attempts_to_disconnect)

                
        else:
            packet = str(key).encode()
            
            udp_header = struct.pack("!IIII", client_settings.CLIENT_PORT, client_settings.assigned_server_port, len(packet), zlib.crc32(packet))
            
            udp_packet = udp_header + packet

            print(udp_packet)

            client_settings.client_socket.sendto(udp_packet, (client_settings.SERVER_ADDRESS, client_settings.assigned_server_port))