import streamlit as st
import random
import matplotlib.pyplot as plt
import ipaddress
import os
# import layer1, layer2, error_control, ipaddressing, slidingwindow, transportlayer



def main():
    st.title("Network Simulator")


    st.sidebar.title("Select Simulation")
    page = st.sidebar.selectbox("Select",("Layer 1","Layer 2","Error Control","Access Control", "Sliding Window","IP Addressing","Transport Layer"))

    
        
    if page == "Layer 1":
        from simulations import layer1
        layer1.main()
    elif page == "Layer 2":
        from simulations import layer2
        layer2.main()
    elif page == "Error Control":
        from simulations import error_control
        error_control.main()
    elif page == "Access Control":
        from simulations import access_control
        access_control.main()
    elif page == "Sliding Window":
        from simulations import slidingwindow
        slidingwindow.main()
    elif page == "IP Addressing":
        from simulations import ipaddressing
        ipaddressing.main()
    elif page == "Transport Layer":
        from simulations import  transportlayer
        transportlayer.main()
    
if __name__ == "__main__":
    main()