from serial import Serial, SerialException

with Serial('COM6', 9600) as ser:
    ser.write(bytes([0x1]))
#    input()
    assert ser.read() == bytes([0xaa])
    input()
    ser.write(bytes([0x0]))
    assert ser.read() == bytes([0xaa])
    input()
    ser.write(bytes([0x2]))
    assert ser.read() == bytes([0xff])

    input()
