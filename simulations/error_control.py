import streamlit as st

def binary_division(dividend, divisor):
    x = int(''.join(map(str, dividend)), 2)
    y = int(''.join(map(str, divisor)), 2)
    rem = x % y
    remainder = format(rem, 'b')
    return remainder

def CRC_sender(data, generator):
    aug = len(generator) - 1
    aug = aug * str(0)
    aug_data = data + aug
    a = int(''.join(map(str, aug_data)), 2)
    aug_data = format(a, 'b')
    rem = binary_division(aug_data, generator)
    codeword = aug_data + rem
    return codeword

def CRC_receiver(code, generator):
    r = binary_division(code, generator)
    if r == "0":
        return "The data has no error"
    else:
        return "Error in data"

def main():
    st.title("CRC (Cyclic Redundancy Check) Simulation")

    st.sidebar.header("Input Parameters")
    data = st.sidebar.text_input("Enter the data string", "11101010101")
    generator = st.sidebar.text_input("Enter the generator string", "1011")

    if st.sidebar.button("Generate Codeword"):
        codeword = CRC_sender(data, generator)
        st.write(f"Data: {data}")
        st.write(f"Generator: {generator}")
        st.write(f"Codeword: {codeword}")

    received_code = st.text_input("Enter the received codeword to check for errors")

    if st.button("Check Codeword"):
        if received_code:
            result = CRC_receiver(received_code, generator)
            st.write(result)
        else:
            st.write("Please enter a received codeword.")

if __name__ == "__main__":
    main()
