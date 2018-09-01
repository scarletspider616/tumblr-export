import json 
import pytumblr


class TumblrScraper:

	''' TumblrScraper Constructor

	Arguments:
	filename: filename (absolute or cwd) to json file containing config options:
		consumer_key
		consumer_secret
		blog_url
	'''

	def __init__(self, filename="options.json"):
		self.filename = filename

	''' TumblrScraper Initializer

	Parses the 
	'''

	def initialize(self):
		self._get_credentials()
		self._get_blog_url()

	''' PRIVATE Parse credentials from json file referenced in the constructor

	saves self.consumer_key, self.consumer_secret to member vars

	'''
	def _get_credentials(self):
		with open(self.filename, "r") as file:
			file_options = json.load(file)
		self.consumer_key = file_options['consumer_key']
		self.consumer_secret = file_options['consumer_secret']


	''' PRIVATE Parse blog url from json file referenced in the constructor 


	saves blog_url from the json file to member var "self.blog"

	'''
	def _get_blog_url(self):
		with open(self.filename, "r") as file:
			file_options = json.load(file)
		self.blog = file_options['blog_url']


if __name__ == "__main__":
	scraper = TumblrScraper()
	scraper.initialize()
	

