import socket
import threading
import datetime

BUFFER_SIZE = 1024
PORT_NUMBER = 4001

file_path = "MeterList.csv"  # Read IP and NODE ID from CSV file

f = open("PassList" + ".txt", "a")  # Open text file for storing the pass IP list
 
def mid(string, start, length):
    return string[start-1:start-1+length]

def timeout_handler():
    print("Data receive timed out. Exiting...")
    exit()
    
def receive_data(client_socket, client_number,server_address):
    while True:
        try:
            # Send data to the server
            message = "000100100001001F601DA109060760857405080101BE10040E01000000065F1F0400001E5DFFFF"
            byte_data = bytes.fromhex(message)
            for byte in byte_data:
                client_socket.sendall(byte.to_bytes(1, byteorder='big'))
          
            data = client_socket.recv(1024)
            if not data:
                break
            print(data)
            
            MESSAGE = "000100100001000DC001C100010000600100FF0200"
            byte_data = bytes.fromhex(MESSAGE)
            for byte in byte_data:
                client_socket.sendall(byte.to_bytes(1, byteorder='big'))
            data1 = client_socket.recv(1024)
            if not data:
                break
            print(data1)
            
            MESSAGE = "00010010000100056203800100"
            byte_data = bytes.fromhex(MESSAGE)         
            for byte in byte_data:
                client_socket.sendall(byte.to_bytes(1, byteorder='big'))
            data = client_socket.recv(BUFFER_SIZE)
            client_socket.close()
            
            try:
                message1 = mid(data1, 15, 9)
                e = datetime.datetime.now()
                f.write(str(e) + "," + str(server_address) + "," + str(client_number) + "," + message1.decode('utf-8') + ",Pass" +"\n")
            except Exception as e:
                 break

        except Exception as e:
            print(f"Client {client_number}: Error - {e}")
            break

    # client_socket.close()
    print(f"Client {client_number}: Disconnected")

def start_tcp_client(server_address, server_port, client_number):
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    
    try:
        client_socket.connect((server_address, server_port))

        # Start a thread to receive data from the server
        receive_thread = threading.Thread(target=receive_data, args=(client_socket, client_number,server_address))
        receive_thread.start()

    except Exception as e:
        print(f"Client {client_number}: Error - {e}")
        client_socket.close()

def main():

    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read all lines into a list
        lines = file.readlines()
        print(lines)
        print("Total IP : ")
        print(len(lines))
    
 
    try:    
        for line in lines:
            csv_data = line.strip().split(',')
            # Open multiple clients in separate threads with different client numbers and server addresses
            start_tcp_client(csv_data[0], PORT_NUMBER, csv_data[1])
            
        # Keep the main thread alive
        while False:
            pass

    except KeyboardInterrupt:
        print("Server shutting down.")
        
    # file close    
    f.close
    
if __name__ == "__main__":
    main()
    