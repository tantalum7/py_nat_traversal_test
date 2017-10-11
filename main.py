
# Library imports
import socket, multiprocessing, stun
import time
from Queue import Empty


class Client(object):

    def __init__(self):

        # Perform stun lookup
        self.stun_info = self.stun_lookup()

        # If nat type is full or restrictive cone, raise an exception
        if self.stun_info['nat_type'] != stun.FullCone or self.stun_info['nat_type'] == stun.RestricPortNAT:
            raise Exception( "NAT type not suitable ({0})".format(self.stun_info['nat_type']) )

        # Start UDP listener on our external port
        self.start_listener(self.stun_info['external_port'])

    def stun_lookup(self):
        return dict( zip( ["nat_type", "external_ip", "external_port"], stun.get_ip_info() ) )

    def start_listener(self, listen_port):
        # Create process safe receive queue and kill event
        self._rx_queue = multiprocessing.Queue()
        self._kill = multiprocessing.Event()

        # Instantiate the process and start it
        self._process = multiprocessing.Process(target=self._server_process, args=([listen_port]))
        self._process.daemon = True
        self._process.start()

    def stop_listener(self):
        # Trigger the process kill event
        self._kill.set()

    def get_packet(self):
        # Try and grab the next packet from the receive queue
        try:
            packet = self._rx_queue.get_nowait()

        # If we receive an Empty exception, return None
        except Empty:
            return None

        # Re-raise any other exceptions:
        except:
            raise

        # If we receive a packet, return it
        else:
            return packet

    def put_packet(self, packet, ip_port_tuple):
        # Create socket and send packet
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(packet, ip_port_tuple)

    @property
    def external_ip(self):
        return self.stun_info['external_ip']

    @property
    def external_port(self):
        return self.stun_info['external_port']

    @property
    def nat_type(self):
        return self.stun_info['nat_type']

    def _server_process(self, listen_port):

        # Create and bind the listening socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        sock.bind(("", listen_port))

        # Loop forever unless kill event occurs
        while not self._kill.is_set():

            # Perform blocking read from socket
            try:
                data_addr_tuple = sock.recvfrom(4096)

            # Ignore socket timeout exceptions
            except socket.timeout:
                pass

            # Re-raise any other exceptions
            except:
                raise

            # We received something from the socket, put it on the receive queue
            else:
                self._rx_queue.put(data_addr_tuple)


if __name__ == "__main__":

    cli = Client()

    while True:

        data_addr_tuple = cli.get_packet()
        if data_addr_tuple:
            print(data_addr_tuple)
