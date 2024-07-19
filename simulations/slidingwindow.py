import streamlit as st
import time
import random

class SlidingWindowProtocol:
    def __init__(self, window_size):
        self.window_size = window_size
        self.frames = []
        self.acknowledged = []
        self.base = 0
        self.next_seq_num = 0

    def send_frame(self, frame):
        if self.next_seq_num < self.base + self.window_size:
            self.frames.append(frame)
            self.acknowledged.append(False)
            self.next_seq_num += 1
            return True
        return False

    def receive_ack(self, ack_num):
        if ack_num >= self.base:
            for i in range(self.base, ack_num + 1):
                self.acknowledged[i] = True
            self.base = ack_num + 1

    def get_window(self):
        return self.frames[self.base:self.base + self.window_size], self.acknowledged[self.base:self.base + self.window_size]

# Main function to create the Streamlit UI
def main():
    st.title("Sliding Window Protocol Simulation")

    window_size = st.sidebar.slider("Window Size", min_value=1, max_value=10, value=4)
    num_frames = st.sidebar.number_input("Number of Frames to Send", min_value=1, max_value=50, value=10)
    start_simulation = st.sidebar.button("Start Simulation")

    if start_simulation:
        protocol = SlidingWindowProtocol(window_size)

        st.write(f"Sending {num_frames} frames with a window size of {window_size}.")

        frame_num = 0
        ack_num = 0

        simulation_placeholder = st.empty()
        progress_bar = st.progress(0)

        while frame_num < num_frames or protocol.base < num_frames:
            with simulation_placeholder.container():
                st.write(f"Frame Window: {protocol.get_window()[0]}")
                st.write(f"Acknowledged: {protocol.get_window()[1]}")

                if frame_num < num_frames:
                    sent = protocol.send_frame(f"Frame {frame_num}")
                    if sent:
                        st.write(f"Sent Frame {frame_num}")
                        frame_num += 1

                # Simulate receiving acknowledgments
                if random.random() > 0.2:  # 80% chance to receive an acknowledgment
                    if ack_num < frame_num:
                        protocol.receive_ack(ack_num)
                        st.write(f"Received Acknowledgment for Frame {ack_num}")
                        ack_num += 1
                else:
                    st.write(f"Acknowledgment for Frame {ack_num} lost")

                time.sleep(0.5)  # Simulate time delay

                progress = min(protocol.base / num_frames, 1.0)
                progress_bar.progress(progress)

        st.success("All frames sent and acknowledged.")

if __name__ == "__main__":
    main()
