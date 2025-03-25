import argparse
import os
import re
import requests
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class	ImageDownloader:
	def	__init__(self, url, it, folder, bot):
		self.url = url
		self.folder = folder
		self.visitedURLs = set()
		self.botParsers = {}
		self.depth = it
		self.bot = bot
		self.domain = urlparse(url).netloc
		self.botID = "PoliteImageScrapper/1.0 (Educational Project)"
		self.validExtends = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
		self.mimeExtends = {'image/jpeg' : '.jpeg',
							'image/jpg' : '.jpg',
							'image/png' : '.png',
							'image/gif' : '.gif',
							'image/bmp' : '.bmp'}
		self.increm = 0

		os.makedirs(self.folder, exist_ok=True)

	def getBotParser(self, url):
		if not self.bot:
			return None
		parsed = urlparse(url)
		key = (parsed.scheme, parsed.netloc)
		if key not in self.botParsers:
			rp = RobotFileParser()
			botsURL = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
			rp.set_url(botsURL)
			try:
				rp.read()
				print(f"robots.txt found for {parsed.netloc}")
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
		return parsed.netloc.endswith(self.domain) and parsed.scheme in ["http", "https"]

	def	downloadIMG(self, imgURL):
		try:
			response = requests.get(imgURL, stream=True, headers={"User-Agent": self.botID}, timeout=10)
			if response.status_code == 200:
				content = response.headers.get('Content-Type', '')
				if not content.startswith('image/'):
					print(f"Invalid MIME type: {content} for {imgURL}")
					return
				extension = self.mimeExtends.get(content, 'not supported')
				if extension == 'not supported':
					print(f"Image type not supported : {imgURL}")
					return
				filename = os.path.join(self.folder, os.path.basename(urlparse(imgURL).path) or f"image{self.increm}.jpg")
				if filename == f"image{self.increm}.jpg":
					self.increm += 1
				elif not filename.endswith(extension, re.IGNORECASE):
					if extension != ".jpeg" and extension:
						filename += extension
					elif not filename.endswith(".jpg", re.IGNORECASE) and not filename.endswith(".JPG", re.IGNORECASE):
						filename += extension
				with open(filename, 'wb') as f:
					for chunk in response.iter_content(1024):
						f.write(chunk)
				print(f"Image successfully downloaded : {imgURL}")
			else:
				print(f"Error  {response.status_code} downloading {imgURL}")
		except Exception as e:
			print(f"Error downloading {imgURL}: {str(e)}")
	
	def extractURLs(self, html, url):
		imgPattern = re.compile(r'<img[^>]+(?:src|srcset|data-src)=["\'](.*?)["\']', re.IGNORECASE)
		imgURLs = []
		for src in imgPattern.findall(html):
			firstUrl = src.split(',')[0].split()[0]
			imgURLs.append(urljoin(url, firstUrl))
		linkPattern = re.compile(r'<a[^>]+href=(["\'])(.*?)\1', re.IGNORECASE)
		linkURLs = [
			urljoin(url, match[1]) 
			for match in linkPattern.findall(html) 
			if match[1].strip()
		]
		return imgURLs, linkURLs
	
	def spider(self, url, currentDepth=0):
		if url in self.visitedURLs or currentDepth > self.depth:
			return
		if self.bot and not self.isAllowedForBots(url):
			print(f"⚠️  Blocked by robots.txt")
			return
		self.visitedURLs.add(url)
		print(f"\033[1;31mVisiting: {url}, depth: {currentDepth}\033[0m")
		try:
			response = requests.get(url, headers={"User-Agent": self.botID})
			html = response.text
			rp = self.getBotParser(url)
			delay = rp.crawl_delay(self.botID) if self.bot and rp else 0
			time.sleep(delay or 0.3)
			imgURLs, linkURLs = self.extractURLs(html, url)
			for imgURL in imgURLs:
				self.downloadIMG(imgURL)
							
			for link in linkURLs:
				if self.isValidURL(link):
					self.spider(link, currentDepth + 1)
		
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
	parser.add_argument("-b", "--bot", action="store_true")
	return parser.parse_args()

def main():
	try:
		args = parseArgs()
		if not args.recursive:
				args.depth = 0
	except argparse.ArgumentTypeError as ate:
		print(f"Error: {ate}.")
		exit(1)
	downloader = ImageDownloader(args.url, args.depth, args.path, args.bot)
	downloader.spider(args.url)

main()