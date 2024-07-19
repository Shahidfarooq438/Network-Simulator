import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import threading
import time
import random
import ipaddress

# Define classes for different network components

class EndDevice:
    def __init__(self, name):
        self.name = name
        self.ports = {}

    def receive(self, src_port, dest_port, data):
        st.write(f"{self.name} received data from port {src_port} to port {dest_port}: {data}")


class Hub:
    def __init__(self, name):
        self.name = name
        self.ports = {}

    def add_port(self, device, port):
        self.ports[port] = device

    def receive(self, port, data):
        st.write(f"Hub {self.name} received data on port {port}: {data}")
        for p, device in self.ports.items():
            if p != port:
                device.receive(port, p, data)


class Switch:
    def __init__(self, name):
        self.name = name
        self.ports = {}
        self.mac_table = {}

    def add_port(self, device, port):
        self.ports[port] = device

    def receive(self, src_port, dest_port, data):
        st.write(f"Switch {self.name} received data from port {src_port} to port {dest_port}: {data}")
        if dest_port in self.mac_table:
            out_port = self.mac_table[dest_port]
            self.ports[out_port].receive(src_port, out_port, data)
        else:
            for p, device in self.ports.items():
                if p != src_port:
                    device.receive(src_port, p, data)

    def update_mac_table(self, mac_address, port):
        self.mac_table[mac_address] = port


class Router:
    def __init__(self, name):
        self.name = name
        self.ports = {}
        self.routing_table = []

    def add_port(self, device, port):
        self.ports[port] = device

    def add_route(self, network, mask, next_hop):
        self.routing_table.append({"network": network, "mask": mask, "next_hop": next_hop})

    def lookup_route(self, destination_ip):
        longest_match = None
        best_route = None
        for route in self.routing_table:
            network = ipaddress.ip_network(f"{route['network']}/{route['mask']}", strict=False)
            if ipaddress.ip_address(destination_ip) in network:
                if longest_match is None or network.prefixlen > longest_match.prefixlen:
                    longest_match = network
                    best_route = route
        return best_route


# Class for transport layer functionality
class TransportLayer:
    def __init__(self):
        self.connections = {}  # {port: (device, process)}
        self.next_ephemeral_port = 49152

    def assign_port(self, device, process, port=None):
        if port is None:
            port = self.next_ephemeral_port
            self.next_ephemeral_port += 1
        self.connections[port] = (device, process)
        return port

    def send(self, src_port, dest_port, data):
        if dest_port in self.connections:
            dest_device, dest_process = self.connections[dest_port]
            dest_process.receive(src_port, dest_port, data)
        else:
            st.write(f"Port {dest_port} is not assigned")

    def receive(self, src_port, dest_port, data):
        if dest_port in self.connections:
            dest_device, dest_process = self.connections[dest_port]
            dest_process.receive(src_port, dest_port, data)
        else:
            st.write(f"Port {dest_port} is not assigned")


# Class for the Go-Back-N protocol
class GoBackNProtocol:
    def __init__(self, transport_layer, window_size=4):
        self.transport_layer = transport_layer
        self.window_size = window_size
        self.send_base = 0
        self.next_seq_num = 0
        self.timer = None
        self.acknowledged = []

    def send(self, src_port, dest_port, data):
        if self.next_seq_num < self.send_base + self.window_size:
            packet = (self.next_seq_num, data)
            self.transport_layer.send(src_port, dest_port, packet)
            self.next_seq_num += 1
            if self.send_base == self.next_seq_num - 1:
                self.start_timer()
        else:
            st.write("Window is full, cannot send data")

    def receive_ack(self, ack_num):
        self.send_base = ack_num + 1
        if self.send_base == self.next_seq_num:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(3.0, self.timeout)
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def timeout(self):
        self.next_seq_num = self.send_base
        self.start_timer()


# Application layer service: FTP
class FTPService:
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.files = {}

    def store_file(self, port, filename, data):
        self.files[filename] = data
        st.write(f"File {filename} stored on port {port}")

    def retrieve_file(self, port, filename):
        if filename in self.files:
            data = self.files[filename]
            st.write(f"File {filename} retrieved from port {port}")
            return data
        else:
            st.write(f"File {filename} not found on port {port}")
            return None


# Application layer service: Telnet
class TelnetService:
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer

    def send_command(self, src_port, dest_port, command):
        st.write(f"Sending command '{command}' to port {dest_port}")
        self.transport_layer.send(src_port, dest_port, command)

    def receive_response(self, src_port, dest_port, response):
        st.write(f"Received response '{response}' from port {src_port} to port {dest_port}")
        return response


def main():
    # Initialize transport layer
    transport_layer = TransportLayer()

    # Initialize application services
    ftp_service = FTPService(transport_layer)
    telnet_service = TelnetService(transport_layer)

    # Streamlit UI
    st.title("Tranport and Application Layer")

    # Initialize session state
    if "end_devices" not in st.session_state:
        st.session_state.end_devices = {}

    if "hubs" not in st.session_state:
        st.session_state.hubs = {}

    if "switches" not in st.session_state:
        st.session_state.switches = {}

    if "routers" not in st.session_state:
        st.session_state.routers = {}

    if "connections" not in st.session_state:
        st.session_state.connections = []

    if "ports" not in st.session_state:
        st.session_state.ports = {}

    # Add device
    device_name = st.text_input("Device Name")
    device_type = st.selectbox("Device Type", options=["End Device", "Hub", "Switch", "Router"])

    if st.button("Add Device"):
        if device_type == "End Device":
            st.session_state.end_devices[device_name] = EndDevice(device_name)
        elif device_type == "Hub":
            st.session_state.hubs[device_name] = Hub(device_name)
        elif device_type == "Switch":
            st.session_state.switches[device_name] = Switch(device_name)
        elif device_type == "Router":
            st.session_state.routers[device_name] = Router(device_name)
        st.write(f"{device_type} '{device_name}' added.")

    # Add connection
    src_device = st.selectbox("Source Device", options=list(st.session_state.end_devices.keys()) + list(st.session_state.hubs.keys()) + list(st.session_state.switches.keys()) + list(st.session_state.routers.keys()))
    dest_device = st.selectbox("Destination Device", options=list(st.session_state.end_devices.keys()) + list(st.session_state.hubs.keys()) + list(st.session_state.switches.keys()) + list(st.session_state.routers.keys()))

    if st.button("Add Connection"):
        if src_device in st.session_state.end_devices:
            src_obj = st.session_state.end_devices[src_device]
        elif src_device in st.session_state.hubs:
            src_obj = st.session_state.hubs[src_device]
        elif src_device in st.session_state.switches:
            src_obj = st.session_state.switches[src_device]
        elif src_device in st.session_state.routers:
            src_obj = st.session_state.routers[src_device]

        if dest_device in st.session_state.end_devices:
            dest_obj = st.session_state.end_devices[dest_device]
        elif dest_device in st.session_state.hubs:
            dest_obj = st.session_state.hubs[dest_device]
        elif dest_device in st.session_state.switches:
            dest_obj = st.session_state.switches[dest_device]
        elif dest_device in st.session_state.routers:
            dest_obj = st.session_state.routers[dest_device]

        src_obj.ports[dest_device] = dest_obj
        dest_obj.ports[src_device] = src_obj
        st.session_state.connections.append((src_device, dest_device))
        st.write(f"Connection added between {src_device} and {dest_device}.")

    # Visualize network
    G = nx.Graph()
    for device in list(st.session_state.end_devices.keys()) + list(st.session_state.hubs.keys()) + list(st.session_state.switches.keys()) + list(st.session_state.routers.keys()):
        G.add_node(device)
    for src, dest in st.session_state.connections:
        G.add_edge(src, dest)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold")
    st.pyplot(plt)

    # Add process communication
    src_device = st.selectbox("Source Device for Communication", options=list(st.session_state.end_devices.keys()))
    dest_device = st.selectbox("Destination Device for Communication", options=list(st.session_state.end_devices.keys()))

    if st.button("Assign Port"):
        src_process = random.randint(1000, 9999)
        dest_process = random.randint(1000, 9999)
        src_port = transport_layer.assign_port(st.session_state.end_devices[src_device], src_process)
        dest_port = transport_layer.assign_port(st.session_state.end_devices[dest_device], dest_process)
        st.session_state.ports[(src_device, dest_device)] = (src_port, dest_port)
        st.write(f"Assigned port {src_port} to process {src_process} on device {src_device}")
        st.write(f"Assigned port {dest_port} to process {dest_process} on device {dest_device}")

    # Add Go-Back-N protocol
    if st.button("Send Data using Go-Back-N"):
        if (src_device, dest_device) in st.session_state.ports:
            src_port, dest_port = st.session_state.ports[(src_device, dest_device)]
            protocol = GoBackNProtocol(transport_layer)
            data = "Hello, this is a test message."
            protocol.send(src_port, dest_port, data)
            st.write(f"Data sent from port {src_port} to port {dest_port} using Go-Back-N")
        else:
            st.write("Ports not assigned for the selected devices")

    # Add FTP functionality
    if st.button("Store File via FTP"):
        if (src_device, dest_device) in st.session_state.ports:
            src_port, dest_port = st.session_state.ports[(src_device, dest_device)]
            filename = "test.txt"
            data = "This is a test file."
            ftp_service.store_file(src_port, filename, data)
            st.write(f"File '{filename}' stored on port {src_port}")
        else:
            st.write("Ports not assigned for the selected devices")

    if st.button("Retrieve File via FTP"):
        if (src_device, dest_device) in st.session_state.ports:
            src_port, dest_port = st.session_state.ports[(src_device, dest_device)]
            filename = "test.txt"
            data = ftp_service.retrieve_file(dest_port, filename)
            if data:
                st.write(f"File content: {data}")
        else:
            st.write("Ports not assigned for the selected devices")

    # Add Telnet functionality
    if st.button("Send Command via Telnet"):
        if (src_device, dest_device) in st.session_state.ports:
            src_port, dest_port = st.session_state.ports[(src_device, dest_device)]
            command = "ls"
            telnet_service.send_command(src_port, dest_port, command)
            st.write(f"Command '{command}' sent to port {src_port}")
        else:
            st.write("Ports not assigned for the selected devices")

    if st.button("Receive Response via Telnet"):
        if (src_device, dest_device) in st.session_state.ports:
            src_port, dest_port = st.session_state.ports[(src_device, dest_device)]
            response = telnet_service.receive_response(dest_port, src_port, "response")
            if response:
                st.write(f"Response: {response}")
        else:
            st.write("Ports not assigned for the selected devices")
