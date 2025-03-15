import argparse
import os
import re
import requests
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

class	ImageDownloader:
	def	__init__(self, url, it, folder):
		self.url = url
		self.folder = folder
		self.visitedURLs = set()
		self.botParsers = {}
		self.iter = it
		self.domain = urlparse(url).netloc
		self.botID = "PoliteImageScrapper/1.0 (Educational Project)"
		os.makedirs(self.folder, exist_ok=True)

	def getBotParser(self, url):
		parsed = urlparse(url)
		key = (parsed.scheme, parsed.netloc)
		if key not in self.botParsers:
			rp = RobotFileParser()
			botsURL = f"{parsed.scheme}:://{parsed.netloc}/robots.txt"
			rp.set_url(botsURL)
			try:
				rp.read()
				print(f"robots.txt found for {parsed.netloc}: {'reachable' if rp.can_fetch(self.botID, '/') else 'blocked'}")
			except Exception as e:
				print(f"robots.txt unreadable for {parsed.netloc}: {e}")
				rp = None
			self.botParsers[key] = rp
		return self.botParsers[key]

	def	isAllowedForBots(self, url):
		rp = self.getBotParser(url)
		if rp is None:
			return True
		return rp.can_fetch(self.botID, url)
	
	def	isValidURL(self, url):
		parsed = urlparse(url)
		return parsed.netloc == self.domain and parsed.scheme in ["http", "https"]

	def	downloadIMG(self, imgURL):
		if self.iter >= 0:
			return
		self.iter -= 1
		try:
			response = requests.get(imgURL, stream=True, headers={"User-Ageget": self.botID})
			if response.status_code == 200:
				filename = os.path.join(self.folder, os.path.basename(urlparse(imgURL).path) or "image.jpg")
				with open(filename, 'wb') as f:
					for chunk in response.iter_content(1024):
						f.write(chunk)
				print(f"{filename} downloaded")
		except Exception as e:
			print(f"Error downloading {imgURL}: {str(e)}")
	
	def extractURLs(self, html, url):
		imgPattern = re.compile(r'<img[^>]+src=(["\'])(.*?)\1', re.IGNORECASE)
		imgURLs = [urljoin(url, match[1]) for match in imgPattern.findall(html)]
		
		linkPattern = re.compile(r'<a[^>]+href=(["\'])(.*?)\1', re.IGNORECASE)
		linkURLs = [urljoin(url, match[1]) for match in linkPattern.findall(html)]

		return imgURLs, linkURLs
	
	def scrapePage(self, url):
		if url in self.visitedURLs:
			return
		if not self.isAllowedForBots(url):
			print(f"⚠️ Bloqué par robots.txt: {url}")
			return
		self.visitedURLs.add(url)

		try:
			print(f"Scrapping: {url}")
			response = requests.get(url, headers={"User-Agent": self.botID})
			html = response.text

			rp = self.getBotParser(url)
			delay = rp.crawl_delay(self.botID) if rp else 0
			time.sleep(delay or 1)
			imgURLs, linkURLs = self.extractURLs(html, url)

			for imgURL in imgURLs:
				self.downloadIMG(imgURL)
							
			for link in linkURLs:
				if self.isValidURL(link) and self.isAllowedForBots(link):
					self.scrapePage(link)
		
		except Exception as e:
			print(f"Error with {url}: {str(e)}")

def parseUrl(url):
	parsed = urlparse(url)
	if not parsed.scheme:
		url = "https://" + url
		parsed = urlparse(url)
	if not parsed.netloc:
		raise argparse.ArgumentTypeError("invalid URL")
	return url

def	parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument("url", metavar="URL", type=parseUrl)
	parser.add_argument("-r", "--recursive", action="store_true")
	parser.add_argument("-l", "--depth", default="5", type=int)
	parser.add_argument("-p", "--path", default="./data", type=str)
	return parser.parse_args()

def main():
	print("entered")
	try:
		args = parseArgs()
	except argparse.ArgumentTypeError as ate:
		print(f"Error: {ate}.")
		exit(1)
	print("parsed")
	downloader = ImageDownloader(args.url, args.depth, args.path)
	downloader.scrapePage(args.url)

main()