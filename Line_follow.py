import serial
import time
import json

# Serial Port Configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Replace with your port (e.g., /dev/ttyS0 or COMx)
BAUD_RATE = 115200

# Bang-Bang Control Parameters
MAX_SPEED = 0.5  # Maximum speed for the wheels
TURN_SPEED = 0.3  # Speed adjustment for turning
DELAY = 0.1  # Delay between control updates (seconds)

# Initialize Serial Communication
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connected to the robot via serial port.")
except Exception as e:
    print(f"Failed to connect to the robot: {e}")
    exit()

def send_json_command(command):
    """Send a JSON command to the robot."""
    try:
        ser.write((json.dumps(command) + '\n').encode())
        print(f"Sent: {command}")
    except Exception as e:
        print(f"Failed to send command: {e}")

def main():
    try:
        while True:
            # Request sensor data from the robot
            sensor_request = {"T": 130}  # CMD_BASE_FEEDBACK
            send_json_command(sensor_request)

            # Read and parse feedback from the robot
            feedback = ser.readline().decode('utf-8').strip()
            if feedback:
                print(f"Received: {feedback}")
                try:
                    sensor_data = json.loads(feedback)
                    left_sensor = sensor_data.get("L", 0)
                    right_sensor = sensor_data.get("R", 0)

                    # Bang-Bang Logic
                    if left_sensor == 1 and right_sensor == 0:
                        # Line detected on the left; turn right
                        command = {"T": 1, "L": TURN_SPEED, "R": MAX_SPEED}
                    elif left_sensor == 0 and right_sensor == 1:
                        # Line detected on the right; turn left
                        command = {"T": 1, "L": MAX_SPEED, "R": TURN_SPEED}
                    elif left_sensor == 0 and right_sensor == 0:
                        # Line detected in the center; go straight
                        command = {"T": 1, "L": MAX_SPEED, "R": MAX_SPEED}
                    else:
                        # Line lost; stop
                        command = {"T": 1, "L": 0, "R": 0}

                    # Send movement command
                    send_json_command(command)

                except json.JSONDecodeError as e:
                    print(f"Failed to parse sensor feedback: {e}")

            time.sleep(DELAY)
    except KeyboardInterrupt:
        print("Exiting program...")
        send_json_command({"T": 1, "L": 0, "R": 0})  # Stop the robot
    finally:
        ser.close()

if __name__ == "__main__":
    main()
