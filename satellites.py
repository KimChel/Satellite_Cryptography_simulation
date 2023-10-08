import paho.mqtt.client as paho

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import time

from tkinter import *
import tkinter.filedialog as fd
from ttkbootstrap.constants import *
import ttkbootstrap as tb

import os

mqttBroker = "io.eclipse.org"
#mqttBroker = IP_ADDRESS
client = paho.Client(client_id="satellite",
                        userdata=None, protocol=paho.MQTTv5)
chunk_size = 64 * 1024

# Global variables
selected_images = []
encoding_time_aes = 0
encoding_time_aes_text = None
key = get_random_bytes(16)

def encrypt_images_aes():
    global key
    IV = get_random_bytes(16)
    global selected_images
    global encoding_time_aes
    global counter
    encoding_time_aes = 0

    if not selected_images:
        print("No images selected.")
        return

    print("Encrypting images...")
    for image in selected_images:
        image_path = os.path.join(image)
        file_size = os.path.getsize(image_path).to_bytes(16, byteorder='big')

        cipher = AES.new(key, AES.MODE_CBC, IV)
        with open(image_path, 'rb') as image_inp:
            header = file_size + IV
            client.publish("encrypted_data/aes/key", payload=key, qos=0)
            client.publish("encrypted_data/aes/header", payload=header, qos=0)
            image_data = image_inp.read()
            seq_number = 0

            while seq_number * chunk_size < len(image_data):
                chunk_start = seq_number * chunk_size
                chunk_end = (seq_number + 1) * chunk_size
                chunk = image_data[chunk_start:chunk_end]
                if len(chunk) % 16 != 0:
                    chunk = chunk + bytes(16 - len(chunk) % 16)
                start_time = time.time()
                encoded_image = cipher.encrypt(chunk)
                end_time = time.time()

                
                client.publish(f"encrypted_data/aes/{seq_number}", payload=encoded_image, qos=0)
                seq_number += 1

                if encoding_time_aes_text:
                    encoding_time_aes_text.config(
                    text="Encoding time: " + str(encoding_time_aes))

        encoding_time_aes += end_time - start_time

    print(f"All images encoded in: {encoding_time_aes}")






def import_images():
    global selected_images
    selected_images = fd.askopenfilenames(title='Choose images', filetypes=[
                                          ("Image files", "*.png *.jpg *.jpeg")])
    print(f'No. of images selected: {len(selected_images)}')

def create_ui():
    global encoding_time_aes_text
    root = tb.Window(themename="vapor")
    root.title("Satellites")
    root.geometry('700x500')

    label = Label(root, text="Satellite Communication", font=("consolas", 18))
    label.pack(pady=20)

    nb = tb.Notebook(root)
    nb.pack(side="right", padx=20, pady=20, fill="both", expand=True)

    tab1 = tb.Frame(nb)
    tab2 = tb.Frame(nb)
    tab3 = tb.Frame(nb)

    # SATELLITE 1
    satellite_1_label = Label(
        tab1, text="Satellite AES", font=("consolas", 18))
    satellite_1_label.pack(pady=20)

    satellite_1_encrypt_btn = tb.Button(
        tab1, text="Choose images", command=import_images)
    satellite_1_encrypt_btn.pack(pady=20)

    satellite_1_encrypt_btn = Button(
        tab1, text="Encrypt and send", command=encrypt_images_aes)  # Add a command
    satellite_1_encrypt_btn.pack(pady=20)

    encoding_time_aes_text = Label(tab1, font=("consolas"))
    encoding_time_aes_text.pack(pady=20)

    # Satellite 2
    satellite_2_label = Label(
        tab2, text="Satellite RSI", font=("consolas", 18))
    satellite_2_label.pack(pady=20)

    # Satellite 3
    satellite_3_label = Label(
        tab3, text="Satellite DES", font=("consolas", 18))
    satellite_3_label.pack(pady=20)

    nb.add(tab1, text="Satellite 1")
    nb.add(tab2, text="Satellite 2")
    nb.add(tab3, text="Satellite 3")

    root.mainloop()


if __name__ == "__main__":



    print("Establishing downlink with ground station...")

    client.connect(mqttBroker, port=1883)
    client.enable_logger()
    print("Downlink established")
    create_ui()

    client.loop_stop()
