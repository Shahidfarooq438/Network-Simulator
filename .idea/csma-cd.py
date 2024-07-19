import random
import time


class Device:
    def __init__(self, name, mac_address):
        self.name = name
        self.mac_address = mac_address
        self.buffer = []
        self.connected_device = None  # Placeholder for connected device (not used in this simulation)
        self.collision = False  # Flag to indicate collision

    def generate_data(self, data_size):
        # Simulate data generation (replace with your data creation logic)
        data = ''.join(random.choice('01') for _ in range(data_size))
        return data

    def send(self, switch, destination_mac):
        if not self.buffer:
            # Generate data if buffer is empty
            self.buffer.append({"source_mac": self.mac_address, "destination_mac": destination_mac,
                                "data": self.generate_data(10)})  # Adjust data size as needed
        else:
            print(f"{self.name}: Buffer full, cannot send data.")

        # Carrier Sense Multiple Access (CS)
        carrier_busy = False
        for _ in range(5):  # Simulate checking for carrier signal (replace with switch status if available)
            carrier_busy = random.randint(0, 1)  # Simulate random carrier activity (0 - idle, 1 - busy)
            if not carrier_busy:
                break  # Exit loop if carrier is not busy for a certain duration
            time.sleep(0.1)  # Simulate checking interval

        if carrier_busy:
            print(f"{self.name}: Carrier Busy, deferring transmission.")
            self.collision = True  # Set collision flag for next attempt
            return

        # Collision Detection (CD)
        transmission_time = 1  # Simulate transmission time
        self.collision = False
        for _ in range(transmission_time):
            time.sleep(0.1)  # Simulate transmission duration
            # Simulate potential collision with other devices transmitting at the same time
            if random.randint(0, 1):  # Random chance of collision
                self.collision = True
                print(f"Collision detected on channel!")
                break

        if self.collision:
            # Handle collision (e.g., backoff and retry)
            print(f"{self.name}: Collision occurred, retrying...")
            # Implement backoff strategy (exponential backoff is common)
            backoff_time = random.randint(0, 2 ** len(self.buffer)) * 0.1  # Random backoff time based on retry attempts
            time.sleep(backoff_time)
            self.send(switch, destination_mac)  # Retry transmission after backoff
        else:
            print(f"{self.name} sent data to {destination_mac}")
            # Simulate sending data to switch (replace with actual switch interaction if implemented)
            switch.receive(self.buffer.pop())  # Remove data from buffer after simulated transmission


class Switch:
    def __init__(self):
        self.buffer = []

    def receive(self, packet):
        # Simulate receiving data from device (replace with actual processing if needed)
        print(f"Switch received: {packet}")
        # Forward packet to destination device (not implemented in this simulation)


# Example Usage
switch = Switch()
device1 = Device("Device 1", "1111111")
device2 = Device("Device 2", "2222222")

# Simulate device behavior
for _ in range(10):  # Run simulation for multiple rounds
    device1.send(switch, device2.mac_address)
    time.sleep(1)  # Simulate time between transmissions
    device2.send(switch, device1.mac_address)
    time.sleep(1)

print("Simulation complete.")
