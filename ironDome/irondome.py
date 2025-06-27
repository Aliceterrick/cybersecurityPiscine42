import os
import sys
import time
import argparse
import logging
import subprocess
import hashlib
import math
import psutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ======================
# CONFIGURATION
# ======================
BACKUP_INTERVAL = 86400
ENTROPY_THRESHOLD = 0.15
DISK_READ_THRESHOLD = 100 * 1024 * 1024
CPU_CRYPTO_THRESHOLD = 85.0
MEMORY_LIMIT = 100 * 1024 * 1024

# ======================
# INITIALIZATION
# ======================
def check_root():
    if os.geteuid() != 0:
        sys.exit("Error: Should be exectuted as root")

def setup_logging():
    log_dir = "/var/log/irondome"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        filename=os.path.join(log_dir, "irondome.log"),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Iron Dome started")

# ======================
# WATCHING MECANISMES
# ======================
class EntropyMonitor:
    """Watching on files entropy changes"""
    def __init__(self):
        self.file_entropy = {}
    
    def calculate_entropy(self, file_path):
        if not os.path.isfile(file_path):
            return 0.0
            
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                if not data:
                    return 0.0
                    
                entropy = 0.0
                for x in range(256):
                    p_x = data.count(x) / len(data)
                    if p_x > 0:
                        entropy += -p_x * math.log2(p_x)
                return entropy
        except Exception:
            return 0.0

    def check_entropy_change(self, file_path):
        current_entropy = self.calculate_entropy(file_path)
        previous_entropy = self.file_entropy.get(file_path, current_entropy)
        
        if previous_entropy == 0:
            change = 0.0
        else:
            change = abs(current_entropy - previous_entropy) / previous_entropy
        
        self.file_entropy[file_path] = current_entropy
        
        if change > ENTROPY_THRESHOLD:
            logging.warning(f"Suspect entropy change: {file_path} "
                           f"({change*100:.2f}%)")

class ActivityMonitor:
    """Watch on system activity"""
    def __init__(self, target_path):
        self.target_path = target_path
        self.last_disk_stats = self.get_disk_stats()
        self.last_check = time.time()
    
    def get_disk_stats(self):
        disk_stats = {}
        for part in psutil.disk_partitions():
            if part.mountpoint == self.target_path:
                usage = psutil.disk_io_counters(perdisk=True).get(part.device, None)
                if usage:
                    disk_stats[part.device] = usage.read_bytes
        return disk_stats
    
    def check_disk_abuse(self):
        current_stats = self.get_disk_stats()
        current_time = time.time()
        time_diff = current_time - self.last_check
        
        for device, current_read in current_stats.items():
            last_read = self.last_disk_stats.get(device, current_read)
            read_rate = (current_read - last_read) / time_diff
            
            if read_rate > DISK_READ_THRESHOLD:
                logging.warning(f"Read disk abuse detected on {device}: "
                               f"{read_rate/1024/1024:.2f} MB/s")
        
        self.last_disk_stats = current_stats
        self.last_check = current_time
    
    def check_crypto_activity(self):
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > CPU_CRYPTO_THRESHOLD:
                    logging.warning(f"Suspect cryptographic activity: "
                                   f"PID={proc.info['pid']} "
                                   f"Process={proc.info['name']} "
                                   f"CPU={proc.info['cpu_percent']:.1f}%")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

# ======================
# Backups
# ======================
class BackupManager:
    """Managing incremential backups"""
    def __init__(self, source_path):
        self.source_path = source_path
        self.backup_dir = os.path.join(os.path.expanduser("~"), "ironbackup")
        os.makedirs(self.backup_dir, exist_ok=True)
        self.last_backup_time = time.time()
    
    def perform_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(self.backup_dir, timestamp)
        
        try:
            subprocess.run([
                "rsync", "-a", "--link-dest=../latest",
                self.source_path + "/", backup_path
            ], check=True)
            
            latest_link = os.path.join(self.backup_dir, "latest")
            if os.path.exists(latest_link):
                os.unlink(latest_link)
            os.symlink(backup_path, latest_link)
            
            logging.info(f"Backup saved at: {backup_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Saving error: {e}")

# ======================
# DAEMON & MONITORING
# ======================
class FileEventHandler(FileSystemEventHandler):
    """Managing File Events"""
    def __init__(self, entropy_monitor):
        super().__init__()
        self.entropy_monitor = entropy_monitor
    
    def on_modified(self, event):
        if not event.is_directory:
            self.entropy_monitor.check_entropy_change(event.src_path)

def daemonize():
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    
    os.chdir('/')
    os.setsid()
    os.umask(0)
    
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def memory_guard():
    process = psutil.Process(os.getpid())
    if process.memory_info().rss > MEMORY_LIMIT:
        logging.critical("Memory limit reached. Restarting.")
        os.execv(sys.argv[0], sys.argv)

# ======================
# POINT D'ENTRÉE
# ======================
def main():
    # Validation initiale
    check_root()
    
    # Configuration
    parser = argparse.ArgumentParser(description='IronDome - Monitoring system')
    parser.add_argument('path', help='Critical path to watch')
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        sys.exit(f"Error: {args.path} does not exist")
    
    # Transformation en daemon
    daemonize()
    setup_logging()
    
    # Initialisation des composants
    entropy_monitor = EntropyMonitor()
    activity_monitor = ActivityMonitor(args.path)
    backup_manager = BackupManager(args.path)
    event_handler = FileEventHandler(entropy_monitor)
    
    # Surveillance de fichiers
    observer = Observer()
    observer.schedule(event_handler, args.path, recursive=True)
    observer.start()
    
    # Boucle principale
    try:
        while True:
            memory_guard()
            
            # Vérifications périodiques
            activity_monitor.check_disk_abuse()
            activity_monitor.check_crypto_activity()
            
            # Sauvegarde selon l'intervalle
            if time.time() - backup_manager.last_backup_time > BACKUP_INTERVAL:
                backup_manager.perform_backup()
                backup_manager.last_backup_time = time.time()
            
            time.sleep(10)
            
    except Exception as e:
        logging.exception("Unknown error: ")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()