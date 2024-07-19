import streamlit as st

class Switch:
    def __init__(self):
        self.mac_table = {}
        self.forwarding_table = {}
        self.active_ports = set()
        self.root_bridge = None
        self.root_port = None

    def update_mac_table(self, mac_address, port):
        self.mac_table[mac_address] = port

    def update_forwarding_table(self, destination_mac, port):
        if destination_mac not in self.forwarding_table:
            self.forwarding_table[destination_mac] = [port]
        else:
            if port not in self.forwarding_table[destination_mac]:
                self.forwarding_table[destination_mac].append(port)

    def handle_frame(self, frame, in_port):
        source_mac = frame['source_mac']
        destination_mac = frame['destination_mac']
        self.update_mac_table(source_mac, in_port)

        if destination_mac in self.mac_table:
            out_port = self.mac_table[destination_mac]
            if out_port != in_port:
                st.write(f"Forwarding frame from port {in_port} to port {out_port}")
                self.update_forwarding_table(destination_mac, out_port)
        else:
            st.write(f"Destination MAC {destination_mac} unknown, flooding frame to all ports")
            for port in self.active_ports:
                if port != in_port:
                    st.write(f"Forwarding frame from port {in_port} to port {port}")
                    self.update_forwarding_table(destination_mac, port)

    def add_port(self, port):
        self.active_ports.add(port)

    def remove_port(self, port):
        if port in self.active_ports:
            self.active_ports.remove(port)


class Bridge(Switch):
    def __init__(self):
        super().__init__()
        self.bridge_id = None
        self.cost_to_root = 0

    def update_root_bridge(self, root_bridge_id, root_port):
        if self.root_bridge is None:
            self.root_bridge = root_bridge_id
            self.root_port = root_port
        else:
            if self.cost_to_root > root_bridge_id.cost_to_root:
                self.root_bridge = root_bridge_id
                self.root_port = root_port

    def add_port(self, port):
        super().add_port(port)
        if self.root_bridge is None:
            self.root_bridge = self
            self.root_port = port

    def remove_port(self, port):
        super().remove_port(port)
        if port == self.root_port:
            self.root_bridge = None
            self.root_port = None


def main():
    # Streamlit UI
    st.title("Layer 2")

    # Create switch and bridge
    switch = Switch()
    bridge = Bridge()

    # Add ports to switch
    st.header("Add Ports to Switch")
    switch_port = st.number_input("Port Number (Switch)", min_value=1, max_value=65535, step=1)
    if st.button("Add Port to Switch"):
        switch.add_port(switch_port)
        st.success(f"Port {switch_port} added to switch.")

    # Add ports to bridge
    st.header("Add Ports to Bridge")
    bridge_port = st.number_input("Port Number (Bridge)", min_value=1, max_value=65535, step=1)
    if st.button("Add Port to Bridge"):
        bridge.add_port(bridge_port)
        st.success(f"Port {bridge_port} added to bridge.")

    # Handle frame input for switch
    st.header("Handle Frame for Switch")
    source_mac_switch = st.text_input("Source MAC Address (Switch)")
    destination_mac_switch = st.text_input("Destination MAC Address (Switch)")
    in_port_switch = st.number_input("Incoming Port (Switch)", min_value=1, max_value=65535, step=1)
    if st.button("Handle Frame (Switch)"):
        frame_switch = {'source_mac': source_mac_switch, 'destination_mac': destination_mac_switch}
        switch.handle_frame(frame_switch, in_port_switch)

    # Handle frame input for bridge
    st.header("Handle Frame for Bridge")
    source_mac_bridge = st.text_input("Source MAC Address (Bridge)")
    destination_mac_bridge = st.text_input("Destination MAC Address (Bridge)")
    in_port_bridge = st.number_input("Incoming Port (Bridge)", min_value=1, max_value=65535, step=1)
    if st.button("Handle Frame (Bridge)"):
        frame_bridge = {'source_mac': source_mac_bridge, 'destination_mac': destination_mac_bridge}
        bridge.handle_frame(frame_bridge, in_port_bridge)

    # Display MAC tables
    st.header("MAC Tables")
    if st.button("Show MAC Table for Switch"):
        st.write(switch.mac_table)

    if st.button("Show MAC Table for Bridge"):
        st.write(bridge.mac_table)

    # Display Forwarding tables
    st.header("Forwarding Tables")
    if st.button("Show Forwarding Table for Switch"):
        st.write(switch.forwarding_table)

    if st.button("Show Forwarding Table for Bridge"):
        st.write(bridge.forwarding_table)
