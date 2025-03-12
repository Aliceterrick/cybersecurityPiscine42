import	argparse as ap
from	urllib.parse import urlparse

def	parseUrl(url):
	parsed = urlparse(url)
	if not parsed.scheme or not parsed.netloc:
		Raise argparse.ArgumentTypeError("Invalid URL")
	return parsed

def	parseArgs():
	parser = ap.ArgumentParser()
	parser.add_argument("url", metavar="URL", type="parseUrl", required="true")
	parser.add_argument("-r", action="store_true")
	parser.add_argument("-l", default="5", type="int")
	parser.add_argument("-p", default="./data", type="str")
	return parser.parse_args()

def main():
	try:
		args = parseArgs()
	except argparse.ArgumentTypeError as ate:
		print(f"Error: {ate}.")
		exit(1)
	
