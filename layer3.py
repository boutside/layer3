#!/usr/bin/env python3
"""
todo:
    Create interactive mode (intercept w/ or w/o filters)
    logging
"""


import socket
import threading
import select
import sys
import argparse
import re

from proxyprocess import process_incoming, process_outgoing
import proxyio


terminate_all = False # signal for terminating all child threads


def main():
    """ Main function """

    # Parse arguments into ARGS global variable
    parse_args()
    proxyio.init(ARGS.verbose)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((ARGS.listener, ARGS.listener_port))
        except Exception as e:
            proxyio.error(f"Interface {ARGS.listener}:{ARGS.listener_port} is busy, exiting...")
            exit(1)
        sock.listen(5)

        proxyio.echo(f"Listening on interface {ARGS.listener}:{ARGS.listener_port}...")

        while True:
            try:
                conn, addr = sock.accept()
                proxyio.echo(f"Successfully bound to {ARGS.listener}:{ARGS.listener_port}") 
                ProxyThread(conn).start() 
            except KeyboardInterrupt:
                terminate_all = True 
                proxyio.echo(f"Terminating all threads...")
                break


class ProxyThread(threading.Thread):
    """ Proxy thread for paralell processing """

    def __init__(self, connection):
        """ Init thread and set connection """
        threading.Thread.__init__(self)
        self.__conn = connection 

    def run(self):
        """ Handle connection made to proxy socket """

        self.__conn.setblocking(0)

        forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward_sock.connect((ARGS.target, ARGS.target_port))
        forward_sock.setblocking(0)

        proxyio.echo(f"Connection established: {ARGS.target}:{ARGS.target_port}")

        client_data = b''
        forward_data = b''
        terminate = False
        while not terminate and not terminate_all:
            inputs = [self.__conn, forward_sock]
            outputs = []

            if len(client_data) > 0:
                outputs.append(self.__conn)

            if len(forward_data) > 0:
                outputs.append(forward_sock)

            try:
                inputs_ready, outputs_ready, errors_ready = select.select(inputs, outputs, [], 1.0)
            except Exception as e:
                proxyio.error("No I/O stream available!")
                break

            for r_input in inputs_ready:
                if r_input == self.__conn:
                    # The proxy receives the data that will be forwarded to the "remote" port
                    try:
                        data = self.__conn.recv(4096)
                    except Exception as e:
                        proxyio.warn("Received no data from listener interface")
                        pass

                    if data != None:
                        if len(data) > 0:
                            forward_data += data
                        else:
                            terminate = True
                            
                elif r_input == forward_sock:
                    # The proxy receives data from the remote host
                    try:
                        data = forward_sock.recv(4096)
                    except Exception as e:
                        proxyio.warn("Received no data from target host")
                        pass

                    if data != None:
                        if len(data) > 0:
                            client_data += data
                        else:
                            terminate = True

            for r_output in outputs_ready:
                if r_output == self.__conn and len(client_data) > 0:
                    # Receive data from remote host, send to client
                    # Process 'incoming' data here!!!!

                    proxyio.debug(f"Original data to listener interface:\n{client_data}")
                    client_data = process_incoming(client_data)

                    proxyio.debug(f"Proxied data to listener interface:\n{client_data}")
                    written = self.__conn.send(client_data)
                    if written > 0:
                        client_data = client_data[written:]
                elif r_output == forward_sock and len(forward_data) > 0:
                    # Forward data to remote host
                    # Process 'outgoing' data here!!!

                    proxyio.debug(f"Original data to target host:\n{forward_data}")
                    forward_data = process_outgoing(forward_data)

                    proxyio.debug(f"Proxied data to target host:\n{forward_data}")
                    written = forward_sock.send(forward_data)
                    if written > 0:
                        forward_data = forward_data[written:] 


def parse_args():
    """ Parse arguments
    Arguments are stored in global ARGS variable """

    global ARGS

    parser = argparse.ArgumentParser(description="Layer 3 TCP proxy")
    parser.add_argument("--target", "-t", required=True)
    parser.add_argument("--target_port", "-tp", type=int, required=True)
    parser.add_argument("--listener", "-l", default="127.0.0.1")
    parser.add_argument("--listener_port", "-lp", type=int, default=1234)
    parser.add_argument("-v", "--verbose", action="count", default=0)

    ARGS = parser.parse_args()


if __name__ == "__main__":
    main()
