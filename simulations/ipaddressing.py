import streamlit as st
import ipaddress
import random
import networkx as nx
import matplotlib.pyplot as plt


# Define the Device, ARPTable, Router, Packet, and RIP classes
class Device:
    def __init__(self, name, ip, mac, connected_router=None):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.connected_router = connected_router


class ARPTable:
    def __init__(self):
        self.table = {}

    def add_entry(self, ip, mac):
        self.table[ip] = mac

    def get_mac(self, ip):
        return self.table.get(ip, None)


class Router:
    def __init__(self, name):
        self.name = name
        self.routing_table = []
        self.arp_table = ARPTable()
        self.interfaces = {}

    def add_interface(self, interface_name, ip):
        mac = self._generate_mac()
        self.interfaces[interface_name] = {'ip': ip, 'mac': mac}
        self.arp_table.add_entry(ip, mac)

    def _generate_mac(self):
        return "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255),
                                            random.randint(0, 255),
                                            random.randint(0, 255))

    def add_static_route(self, network, mask, next_hop):
        self.routing_table.append({'network': network, 'mask': mask, 'next_hop': next_hop})

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

    def handle_packet(self, packet):
        destination_ip = packet.destination_ip
        route = self.lookup_route(destination_ip)
        if route:
            next_hop_ip = route['next_hop']
            next_hop_mac = self.arp_table.get_mac(next_hop_ip)
            if next_hop_mac:
                st.write(f"Packet forwarded to {next_hop_mac} via next hop {next_hop_ip}")
            else:
                st.write(f"Next hop MAC address not found for IP {next_hop_ip}")
        else:
            st.write(f"No route found for destination {destination_ip}")


class Packet:
    def __init__(self, source_ip, destination_ip):
        self.source_ip = source_ip
        self.destination_ip = destination_ip


class RIP:
    def __init__(self, router):
        self.router = router
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def send_update(self):
        for neighbor in self.neighbors:
            st.write(f"Sending routing update from {self.router.name} to {neighbor.name}")
            for route in self.router.routing_table:
                neighbor.receive_update(self.router.name, route)

    def receive_update(self, neighbor_name, route):
        st.write(f"Received routing update from {neighbor_name}")
        network = ipaddress.ip_network(f"{route['network']}/{route['mask']}", strict=False)
        if not any(ipaddress.ip_network(f"{r['network']}/{r['mask']}", strict=False) == network for r in
                   self.router.routing_table):
            self.router.add_static_route(route['network'], route['mask'], route['next_hop'])


# Main function to create the Streamlit UI
def main():
    st.title("Network Simulator")

    # Initialize session state
    if 'routers' not in st.session_state:
        st.session_state.routers = {}
        st.session_state.devices = {}
        st.session_state.connections = []
        st.session_state.device_connections = []
        st.session_state.rip_instances = {}

    # Add router
    with st.sidebar.form(key='add_router_form'):
        router_name = st.text_input('Router Name')
        add_router = st.form_submit_button('Add Router')

    if add_router and router_name:
        st.session_state.routers[router_name] = Router(router_name)
        st.session_state.rip_instances[router_name] = RIP(st.session_state.routers[router_name])

    # Add device
    with st.sidebar.form(key='add_device_form'):
        device_name = st.text_input('Device Name')
        device_ip = st.text_input('Device IP')
        connected_router = st.selectbox('Connected Router', options=list(st.session_state.routers.keys()))
        add_device = st.form_submit_button('Add Device')

    if add_device and device_name and device_ip and connected_router:
        device_mac = "02:00:00:%02x:%02x:%02x" % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        st.session_state.devices[device_name] = Device(device_name, device_ip, device_mac, connected_router)
        st.session_state.routers[connected_router].arp_table.add_entry(device_ip, device_mac)

    # Add connection
    with st.sidebar.form(key='add_connection_form'):
        router1 = st.selectbox('Router 1', options=list(st.session_state.routers.keys()))
        router2 = st.selectbox('Router 2', options=list(st.session_state.routers.keys()))
        network = st.text_input('Network (e.g., 192.168.1.0)')
        mask = st.text_input('Mask (e.g., 24)')
        add_connection = st.form_submit_button('Add Connection')

    if add_connection and router1 and router2 and network and mask:
        ip1 = str(ipaddress.ip_network(f"{network}/{mask}")[1])
        ip2 = str(ipaddress.ip_network(f"{network}/{mask}")[2])
        st.session_state.routers[router1].add_interface(f"{router1}-eth0", ip1)
        st.session_state.routers[router2].add_interface(f"{router2}-eth0", ip2)
        st.session_state.routers[router1].add_static_route(network, mask, ip2)
        st.session_state.routers[router2].add_static_route(network, mask, ip1)
        st.session_state.rip_instances[router1].add_neighbor(st.session_state.routers[router2])
        st.session_state.rip_instances[router2].add_neighbor(st.session_state.routers[router1])
        st.session_state.connections.append((router1, router2))

    # Display routers and devices
    st.subheader("Routers")
    for router in st.session_state.routers.values():
        st.write(f"Router: {router.name}, Interfaces: {router.interfaces}")

    st.subheader("Devices")
    for device in st.session_state.devices.values():
        st.write(
            f"Device: {device.name}, IP: {device.ip}, MAC: {device.mac}, Connected Router: {device.connected_router}")

    st.subheader("Connections")
    for conn in st.session_state.connections:
        st.write(f"Connection: {conn[0]} <--> {conn[1]}")

    # Visualize network topology
    G = nx.Graph()

    for router_name in st.session_state.routers.keys():
        G.add_node(router_name, type='router')

    for device_name, device in st.session_state.devices.items():
        G.add_node(device_name, type='device')
        G.add_edge(device_name, device.connected_router)

    for conn in st.session_state.connections:
        G.add_edge(conn[0], conn[1])

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True,
            node_color=['lightblue' if G.nodes[node]['type'] == 'router' else 'lightgreen' for node in G.nodes],
            node_size=3000, font_size=12, font_weight='bold')
    plt.title('Network Topology')
    st.pyplot(plt)

    # Simulate data transfer
    st.subheader("Simulate Data Transfer")
    with st.form(key='data_transfer_form'):
        src_device = st.selectbox('Source Device', options=list(st.session_state.devices.keys()))
        dest_device = st.selectbox('Destination Device', options=list(st.session_state.devices.keys()))
        transfer_data = st.form_submit_button('Transfer Data')

    if transfer_data and src_device and dest_device:
        src_ip = st.session_state.devices[src_device].ip
        dest_ip = st.session_state.devices[dest_device].ip
        packet = Packet(src_ip, dest_ip)

        src_router = st.session_state.routers[st.session_state.devices[src_device].connected_router]
        src_router.handle_packet(packet)
        dest_router = st.session_state.routers[st.session_state.devices[dest_device].connected_router]
        dest_router.handle_packet(packet)


if __name__ == "__main__":
    main()
