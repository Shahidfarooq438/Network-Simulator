import streamlit as st

class Device:
    def __init__(self, name, mac_address):
        self.name = name
        self.mac_address = mac_address
        self.buffer = []
        self.connected_device = None

    def connect(self, other_device):
        self.connected_device = other_device
        other_device.connected_device = self

    def send(self, data, destination):
        if self.connected_device:
            if self.connected_device.mac_address == destination:
                packet = {"source": self.name, "destination": destination, "data": data}
                self.connected_device.buffer.append(packet)
            else:
                st.write(f"{self.name}: Destination MAC ({destination}) doesn't match connected device.")
        else:
            packet = {"source": self.name, "destination": destination, "data": data}
            hub2.buffer.append(packet.copy())
            hub1.buffer.append(packet.copy())

    def receive(self):
        if self.buffer:
            packet = self.buffer.pop(0)
            st.write(f"{self.name} received data: {packet['data']} from {packet['source']}")


class Hub:
    def __init__(self):
        self.connected_devices = []
        self.buffer = []

    def connect(self, device):
        self.connected_devices.append(device)

    def transmit(self):
        if self.buffer:
            for packet in list(self.buffer):
                for connected_device in self.connected_devices:
                    if connected_device.mac_address != packet["source"]:
                        connected_device.buffer.append(packet.copy())
            self.buffer.clear()


def main():
    # Initialize devices and hubs
    devices = {}
    hubs = {"Hub 1": Hub(), "Hub 2": Hub()}

    # Streamlit UI
    st.title("Layer 1")

    # Add Device
    with st.sidebar:
        st.header("Add Device")
        device_name = st.text_input("Device Name")
        device_mac = st.text_input("MAC Address")
        if st.button("Add Device"):
            devices[device_name] = Device(device_name, device_mac)
            st.success(f"Device {device_name} added.")

    # Connect Devices to Hub
    st.header("Connect Devices to Hubs")
    device_options = list(devices.keys())
    hub_options = list(hubs.keys())

    device_to_hub = st.selectbox("Select Device", device_options)
    hub_selection = st.selectbox("Select Hub", hub_options)
    if st.button("Connect to Hub"):
        hubs[hub_selection].connect(devices[device_to_hub])
        st.success(f"Connected {device_to_hub} to {hub_selection}.")

    # Dedicated Connection
    st.header("Dedicated Connection")
    device1 = st.selectbox("Device 1", device_options, key="dedicated_device1")
    device2 = st.selectbox("Device 2", device_options, key="dedicated_device2")
    if st.button("Establish Dedicated Connection"):
        devices[device1].connect(devices[device2])
        st.success(f"Established dedicated connection between {device1} and {device2}.")

    # Send Data
    st.header("Send Data")
    sender_device = st.selectbox("Sender Device", device_options, key="sender")
    receiver_mac = st.text_input("Receiver MAC Address", key="receiver_mac")
    data_to_send = st.text_area("Data")
    if st.button("Send Data"):
        devices[sender_device].send(data_to_send, receiver_mac)
        st.success(f"Data sent from {sender_device} to MAC {receiver_mac}.")

    # Receive Data
    st.header("Receive Data")
    receiver_device = st.selectbox("Receiver Device", device_options, key="receiver")
    if st.button("Receive Data"):
        devices[receiver_device].receive()

    # Transmit Data via Hub
    st.header("Transmit Data via Hubs")
    if st.button("Transmit Data via Hubs"):
        hubs["Hub 1"].transmit()
        hubs["Hub 2"].transmit()
        st.success("Data transmitted via hubs.")

    st.sidebar.header("Connected Devices")
    for device_name, device in devices.items():
        st.sidebar.write(f"{device_name} - {device.mac_address}")

    st.sidebar.header("Hubs")
    for hub_name, hub in hubs.items():
        st.sidebar.write(hub_name)
        for connected_device in hub.connected_devices:
            st.sidebar.write(f" - {connected_device.name}")


