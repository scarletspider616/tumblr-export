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

	def __init__(self, filename="../options.json"):
		self._filename = filename

	''' TumblrScraper Initializer

	Parses the config file for login and blog details
	creates pyTumblr client member var _client
	'''

	def initialize(self):
		self._get_credentials()
		self._get_blog_url()
		self._client = pytumblr.TumblrRestClient(
			self._consumer_key,
			self._consumer_secret,
			self._token,
			self._token_secret)

	''' PRIVATE Parse credentials from json file referenced in the constructor

	saves self._consumer_key, self._consumer_secret to member vars
	save self._token, self._token_secret

	'''
	def _get_credentials(self):
		with open(self._filename, "r") as file:
			file_options = json.load(file)
		self._consumer_key = file_options['consumer_key']
		self._consumer_secret = file_options['consumer_secret']
		self._token = file_options['token']
		self._token_secret = file_options['token_secret']

	''' PRIVATE Parse blog url from json file referenced in the constructor 


	saves blog_url from the json file to member var "self._blog"

	'''
	def _get_blog_url(self):
		with open(self._filename, "r") as file:
			file_options = json.load(file)
		self._blog = file_options['blog_url']


	''' Parse the number of posts for the blog using the blog_info call in the
	api.

	Will return an int with the number if successful, False otherwise
	'''
	def get_number_of_posts(self):
		num_post = 0
		blog_info = self._client.blog_info(self._blog)
		try:
			num_posts = int(blog_info['blog']['posts'])
		except:
			print("TumblrScraper - couldn't get no. posts")
			return False
		return num_posts


	''' Download posts from Tumblr using their api call until we run out 
	of posts to download! 

	Will return a dict obj in the format of Tumblr's regular posts api call
	if successful. Returns False otherwise

	Nothing fancy here, mostly just logic to get all posts from Tumblr
	instead of just the first "x" as per their api
	'''
	def get_all_posts(self):
		num_posts = self.get_number_of_posts()
		if not num_posts:
			print("TumblrScraper - Can't get all posts if we" + \
				" can't get the number!")
			return False
		return self._client.posts(self._blog, limit=num_posts)


	''' Get all post text from Tumblr using their api call until we run out 
	of posts to download! 

	Will return a dict keyed by post-id with titles of posts if successful
	Returns False otherwise

	'''
	def get_all_post_text(self):
		num_posts = self.get_number_of_posts()
		posts = self.get_all_posts()
		if not num_posts or not posts:
			print("TumblrScraper - Can't parse posts...")
			return False
		results = dict()
		for post in posts['posts']:
			results[post['id']] = post['caption']
		return results




if __name__ == "__main__":
	scraper = TumblrScraper()
	scraper.initialize()
	print(scraper.get_all_post_text())