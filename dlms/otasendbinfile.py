import serial
import time
import os

def send_file(file_path, port, baudrate=115200, chunk_size=1024):
    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Opened {port} at {baudrate} baud.")
        
        # Open the file to be sent
        with open(file_path, 'rb') as file:
            file_size = os.path.getsize(file_path)
            print(f"Sending file: {file_path} ({file_size} bytes)")
            
            bytes_sent = 0
            
            while bytes_sent < file_size:
                # Read the next chunk from the file
                chunk = file.read(chunk_size)
                
                if not chunk:
                    break
                
                # Send the chunk over UART
                ser.write(chunk)
                
                # Wait for an acknowledgment from the STM32
                ack = ser.read(1)
                if ack != b'\x06':  # Assuming STM32 sends ACK (0x06)
                    print("Failed to receive ACK. Resending chunk...")
                    file.seek(bytes_sent)  # Rewind to resend the chunk
                    continue
                
                bytes_sent += len(chunk)
                print(f"Sent {bytes_sent}/{file_size} bytes")
                
            print("File transmission complete.")
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except FileNotFoundError:
        print("Error: File not found.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    file_path = "STM32G070RBT6_APP1_40kb.bin"  # Replace with your firmware file path
    port = "COM7"  # Replace with your STM32's serial port
    send_file(file_path, port)
