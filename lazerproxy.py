#!/usr/bin/env python3
"""
    TODO: make this multi-threaded
    Create interactive mode (intercept w/ or w/o filters)
    logging
    user-friendly output
    
"""

import socket
import threading
import select
import sys
import argparse
import re

from lazerprocess import process_incoming, process_outgoing

def main():
    """ Main function """

    # Parse arguments into ARGS global variable
    parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ARGS.listener, ARGS.listener_port))
        sock.listen(5)

        while True:
            conn, addr = sock.accept()
            print(f"[*] Successfully bound to {ARGS.listener}:{ARGS.listener_port}")
            handle_connection(conn)
        
def handle_connection(conn):
    """ Handle connection made to proxy socket """

    conn.setblocking(0)

    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward_sock.connect((ARGS.target, ARGS.target_port))
    forward_sock.setblocking(0)

    print(f"[*] Connection established: {ARGS.target}:{ARGS.target_port}")

    client_data = b''
    forward_data = b''
    while True:
        inputs = [conn, forward_sock]
        outputs = []

        if len(client_data) > 0:
            outputs.append(conn)

        if len(forward_data) > 0:
            outputs.append(forward_sock)

        try:
            inputs_ready, outputs_ready, errors_ready = select.select(inputs, outputs, [], 1.0)
        except Exception as e:
            #TODO: Handle exception
            break

        for r_input in inputs_ready:
            if r_input == conn:
                # The proxy receives the data that will be forwarded to the "remote" port
                try:
                    data = conn.recv(4096)
                except Exception as e:
                    pass

                if data != None:
                    if len(data) > 0:
                        forward_data += data
                    else:
                        conn.shutdown(socket.SHUT_RDWR)
                        conn.close()
                        forward_sock.shutdown(socket.SHUT_RDWR)
                        forward_sock.close()
                        return
            elif r_input == forward_sock:
                # The proxy receives data from the remote host
                try:
                    data = forward_sock.recv(4096)
                except Exception as e:
                    pass

                if data != None:
                    if len(data) > 0:
                        client_data += data
                    else:
                        conn.shutdown(socket.SHUT_RDWR)
                        conn.close()
                        forward_sock.shutdown(socket.SHUT_RDWR)
                        forward_sock.close()
                        return

        for r_output in outputs_ready:
            if r_output == conn and len(client_data) > 0:
                # Receive data from remote host, send to client
                # Process 'incoming' data here!!!!

                client_data = process_incoming(client_data)

                written = conn.send(client_data)
                if written > 0:
                    client_data = client_data[written:]
            elif r_output == forward_sock and len(forward_data) > 0:
                # Forward data to remote host
                # Process 'outgoing' data here!!!

                forward_data = process_outgoing(forward_data)

                written = forward_sock.send(forward_data)
                if written > 0:
                    forward_data = forward_data[written:] 

def parse_args():
    """ Parse arguments
    Arguments are stored in global ARGS variable """

    global ARGS

    parser = argparse.ArgumentParser(description="Layer 3 TCP proxy")
    parser.add_argument("--target", "-t")
    parser.add_argument("--target_port", "-tp", type=int)
    parser.add_argument("--listener", "-l")
    parser.add_argument("--listener_port", "-lp", type=int)

    ARGS = parser.parse_args()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting... ")
        exit()
