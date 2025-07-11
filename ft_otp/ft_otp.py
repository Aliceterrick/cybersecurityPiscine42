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
        hexa = bytes.fromhex(key)
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
            f.write(fernet.encrypt(hexa))
    except Exception as e:
        print('error saving key', e)
        return
    print("Key saved to ft_otp.key")

def generate_otp(file):
    try:
        with open('.key','rb') as f:
            fkey = f.read()
        fkey = Fernet(fkey)
    except:
        print('Error reading the hidden file .key')
        return None
    try:
        with open(file, 'rb') as f:
            encr_key = f.read()
        key_bytes = fkey.decrypt(encr_key)

    except:
        print('Error reading the key')
        return None
    counter = int(time.time() // 30)
    counter = counter.to_bytes(8, byteorder='big')
    hs = hmac.new(key_bytes, counter, "sha1")
    hs = hs.digest()
    offset = hs[-1] & 0x0F
    p = hs[offset:offset+4]
    code = int.from_bytes(p, byteorder='big') & 0x7FFFFFFF
    totp = code % 1000000
    print(f"your OTP is : {totp:06d}")
    return f"{totp:06d}"

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