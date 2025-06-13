import time
import serial

"""
A test script to verify that the correct acctuators (LEDs) fires based on signal output
"""

def main():
    port = "COM11"
    baud = 115200
    try:
        ser = serial.Serial(port, baud, timeout=1, write_timeout=1)
    except serial.SerialException as e:
        print(f"couldn't open {port}: {e}")
        return

    cmds = {
        '1': 'UP',
        '2': 'DOWN',
        '3': 'LEFT',
        '4': 'RIGHT',
        '5': 'HARDER',
        '6': 'WEAKER',
        '0': 'OFF',
    }

    print(f"connected to {port}@{baud}bps\n")
    print("enter a number to test:")
    for k, v in cmds.items():
        print(f"  {k} → {v}")
    print("  s → sequential test (1→6→0)")
    print("  q → quit\n")

    try:
        while True:
            choice = input("choice: ").strip().lower()
            if choice == 'q':
                break
            if choice == 's':
                for k in ['1','2','3','4','5','6','0']:
                    cmd = cmds[k]
                    print(f"sending {cmd}")
                    ser.write((cmd+'\n').encode())
                    time.sleep(1)
                print("done sequence\n")
                continue
            if choice in cmds:
                cmd = cmds[choice]
                print(f"sending {cmd}\n")
                ser.write((cmd+'\n').encode())
            else:
                print("invalid, try again\n")
    except KeyboardInterrupt:
        pass
    finally:
        ser.write(b'OFF\n')
        ser.close()
        print("bye")

if __name__ == "__main__":
    main()
