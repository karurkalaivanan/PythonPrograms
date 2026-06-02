import time
from dlms_client import DLMSClient, AARE, AARQ, RLRQ, RLRP, COSEMObject, AttributeDescriptor

def main():
    # Initialize the DLMS client with appropriate connection parameters
    # Here we assume a serial connection for simplicity, but in real scenarios, 
    # this could be over TCP/IP or other communication methods
    client = DLMSClient(port='COM29', baudrate=9600, timeout=5)
    
    try:
        # Establish association with the meter (this step might vary based on setup)
        association_request = AARQ()
        association_response = client.associate(association_request)
        
        if association_response.state == AARE.ASSOCIATED:
            print("Association with the meter established successfully.")
            
            # Define the COSEM object for the serial number
            # The OBIS code for the serial number might be different based on the meter
            # Here we assume it's '0.0.96.1.0.255'
            serial_number_object = COSEMObject(obis_code='0.0.96.1.0.255', class_id=1)
            
            # Create an attribute descriptor for the attribute we want to read
            # Assuming the serial number is attribute 2 of this object
            attribute_descriptor = AttributeDescriptor(object=serial_number_object, attribute_id=2)
            
            # Construct the Read Long Request
            read_request = RLRQ(attribute_descriptor=attribute_descriptor, 
                                from_value=0, to_value=0, block_number=1)
            
            # Send the request and wait for the response
            read_response = client.read_long(read_request)
            
            if isinstance(read_response, RLRP):
                # Extract the serial number from the response
                serial_number = read_response.get_data()
                print(f"Serial Number of the Energy Meter: {serial_number}")
            else:
                print("Unexpected response type received.")
        
        else:
            print("Failed to associate with the meter.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Always ensure to release the association
        client.release_association()
        print("Association released.")

if __name__ == "__main__":
    main()