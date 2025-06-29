import sys
import hmac
from cryptography.fernet import Fernet
import time
from qrcode_generator import qr_gen

def save_key(filename):
    try:
        with open(filename, 'r') as f:
            key = f.read()
    except:
        print(f"Error opening {filename}")
        return
    if len(key) < 64:
        print("key length must be at least 64 chars")
        return
    try:
        dec = int(key, 16)
        hexa = str(key)
    except:
        print("key must be hexadecimal")
        return
    fernet_key = Fernet.generate_key()
    fernet = Fernet(fernet_key)
    try:
        with open('.key', 'wb') as f:
            f.write(fernet_key)
    except:
        print('error saving fernet_key')
        return
    try:
        with open('ft_otp.key', 'wb') as f:
            f.write(fernet.encrypt(hexa.encode()))
    except:
        print('error saving key')
        return
    print("Key saved to ft_otp.key")

def compress(p):
    res = bytearray()
    res.append(p[0] & 0x7f)
    for b in p[1:]:
        res.append(b & 0xFF)
    return res

def generate_otp(file):
    try:
        with open('.key','rb') as f:
            fkey = f.read()
        fkey = Fernet(fkey)
    except:
        print('Error reading the .key')
        return
    try:
        with open(file, 'rb') as f:
            key = f.read()
        key = fkey.decrypt(key)
    except:
        print('Error reading the key')
        return
    counter = int(time.time() // 30)
    counter = counter.to_bytes(8, byteorder='big')
    hs = hmac.new(key, counter, "sha1")
    hs = hs.digest()
    offset = hs[19] & 0b1111
    p = hs[offset:offset+4]
    totp = compress(p)
    totp = int(totp.hex(), 16)
    totp = str(totp % 10 ** 6)
    while len(totp) < 6:
        totp += '0'
    print(f"your OTP is : {totp}")
    return totp

def main():
    if len(sys.argv) != 3:
        print("Usage: python ft_otp.py (-g <filename> | -k <filename> | -q <filename>)")
        sys.exit(1)

    action = sys.argv[1]
    filename = sys.argv[2]

    if action == '-g':
        save_key(filename)
    elif action == '-k':
        generate_otp(filename)
    elif action == '-q':
        qr_gen(generate_otp(filename))
    else:
        print("Invalid action. Use -g to generate a key or -k to generate an OTP.")

if __name__ == "__main__":
    main()