import paho.mqtt.client as paho

from Crypto.Cipher import AES

import time

mqttBroker = "io.eclipse.org"
#mqttBroker = IP_ADDRESS
client = paho.Client(client_id="ground_station", userdata=None, protocol=paho.MQTTv5)
chunk_size = 64*1024


print("Establishing uplink with Satellites...")
client.connect(mqttBroker, port=1883)

print("Uplink established")

# Counter to generate different image names
global counter 
# The key that will be received from the satellite
global key
# The header data from the satellite that will be used for the decryption
global IV
counter = 0
key = b''
IV = 0

#O n message function that will be called everytime a message is received
def on_message(client, userdata, message):
    global counter
    global key
    global IV
    global file_size

    # Different action depending to the topic
    # The header has the file_size that will be used for the creation of the decoded image's size and the IV that will be used for the decryption along with the key
    if message.topic == "encrypted_data/aes/header":
        header = message.payload
        IV = header[16:32]
        file_size_bytes = header[:16]
        file_size = int.from_bytes(file_size_bytes, byteorder='big')  # Convert bytes to integer
        global received_chunks
        received_chunks = []
        counter += 1 
    elif message.topic == "encrypted_data/aes/key":
        key = message.payload
    #H ere the encrypted data of the image are being received
    else:
        # Receive chunks with sequence numbers and store them
        seq_number = int(message.topic.split("/")[-1])
        received_chunks.append((seq_number, message.payload))
        
        # Check if all chunks have been received
        if len(received_chunks) == (file_size + chunk_size - 1) // chunk_size:

            # Sort the received chunks by sequence number
            received_chunks.sort(key=lambda x: x[0])
            
            # Reassemble the encoded image
            encoded_payload = b''.join(chunk[1] for chunk in received_chunks)
            
            decryptor = AES.new(key, AES.MODE_CBC, IV)
            with open("./images_satellite_1_decrypted/"+ str(counter) +".png", "wb") as outf:
                encrypted_data = encoded_payload
                while True:
                    if len(encrypted_data) == 0:
                        break
                    chunk = encrypted_data[:chunk_size]
                    encrypted_data = encrypted_data[chunk_size:]
                    decoded_data = decryptor.decrypt(chunk)
                    outf.write(decoded_data)
            print("Received image " + str(counter))


print("Awaiting for messages...")

client.loop_start()

client.subscribe("encrypted_data/aes/#", qos=0)
client.on_message = on_message

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Received KeyboardInterrupt. Exiting...")
    client.loop_stop()
    client.disconnect()