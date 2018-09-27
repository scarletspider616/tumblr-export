import json 
import pytumblr
import re
import calendar


class TumblrScraper:

	_posts = None
	_titles = None
	_data = None
	''' TumblrScraper Constructor

	Arguments:
	filename: filename (absolute or cwd) to json file containing config options:
		consumer_key
		consumer_secret
		blog_url
	'''

	def __init__(self, filename="../options.json"):
		self._filename = filename
		self.initialize()

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
		self._posts = self.get_all_posts()
		self.populate_dicts()
		# self._titles = self.get_all_titles()
		# self._data = self.get_all_data()

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

	def populate_dicts(self):
		self._titles = dict()
		for post in self._posts:
			self._titles[str(post['id'])] = self.get_title(post)
			# self._bodies[post['id']] = self._get_body(post)
			# self._photos[post['id']] = self._get_photos(post)
			# self._date[post['id']]   = self._get_date(post)


	''' Download posts from Tumblr using their api call until we run out 
	of posts to download! 

	Will return a dict obj in the format of Tumblr's regular posts api call
	if successful. Returns False otherwise

	Nothing fancy here, mostly just logic to get all posts from Tumblr
	instead of just the first "x" as per their api
	'''
	def get_all_posts(self):
		if not self._posts:
			num_posts = self.get_number_of_posts()
			if not num_posts:
				print("TumblrScraper - Can't get all posts if we" + \
					" can't get the number!")
				return False
			posts = 0
			results = list()
			while posts < num_posts - 49:
				results = results + self._client.posts(self._blog, limit=50, offset=posts)["posts"]
				posts = posts + 50
			results = results + self._client.posts(self._blog, limit=num_posts-posts, offset=posts)["posts"]
			return results
		return self._posts



	''' Parses a post entry for the title 

	Of all methods in this lib, this is the sketchiest, as its based entirely on parsing Taylor's blog, which 
	just uses a header at the top of the post as a title. As far as I know, Tumblr does not have an official 
	"Title" field, although I may be wrong
	'''
	def get_title(self, post):
		text = self._parse_out_text(str(post['trail']))
		title_match = re.match(r'<p><h2>(.*?)</h2><p>', text)
		if title_match:
			return title_match.group(1)
		title_match = re.match(r'<p><h2><center><b>(.*?)</b></center></h2><p><b>', text)
		if title_match:
			return title_match.group(1)
		title_match = re.match(r'<p><h2><center>(.*?)</center></h2>', text)
		if title_match:
			return title_match.group(1)
		title_match = re.match(r'<p><center><h2>(.*?)</h2></center><p>', text)
		if title_match:
			return title_match.group(1)
		title_match = re.match(r'<p><h2>(.*)</h2>\\n<p>', text)
		if title_match:
			return title_match.group(1)

		if self._posts_without_titles(str(post['id'])):
			return self._posts_without_titles(str(post['id']))
		music_playlist_match = re.match(r'<p><b>1\..*?</b></p><p>.*?<p><b>2\.', text)
		if music_playlist_match:
			# if it matched that nonsense, its almost definitely an OLD music playlist post that didn't have a title
			# in the post
			# get the month & year and throw that in the title
			date = str(post['date'])
			date_match = re.match(r'([0-9]{4})-[0-9]{2}-([0-9]{2}).*', date)
			year = date_match.group(1)
			month = calendar.month_abbr[int(date_match.group(2))]
			print(post['id'])
			print(month + " " + year[2] + year[3] + " Music Playlist")
			return (month + " " + year[2] + year[3] + " Music Playlist")



		print("couldnt get match: ")
		print(text)
		print(post['id'])
		exit()


	''' Parses a tumblr api dump of data into the actual post content
	'''
	def _parse_out_text(self, text):
		first_split = text.split("\'content_raw\': ", 1)
		second_split = first_split[1].split(", \'is_current_item\': ", 1)
		result = second_split[0]
		result = result[:-1]
		result = result[1:]
		return result


	''' These nightmarish exceptions on Taylor's blog HSVE NO TITLES OR HAVE TITLES 
	IN A PHOTO WHICH IS THE WORST THING EVER
	'''
	# todo: turn this nightmare into a dict
	def _posts_without_titles(self, post_id):
		if str(post_id) == "150965735430":
			# exception case, this particular post only has a title in its photo!
			# fun times
			return "Make It Yourself Monday Part 2"
		# if str(post_id) == "143758273428":
		# 	# exception case, this particular post only has a title in its photo!
		# 	# fun times
		# 	return "May Music Playlist" # 2016
		# 	# no doubt one of many may music playlists!
		# if str(post_id) == "142080113913":
		# 	return "April Music Playlist" # 2016
		if str(post_id) == "141149831439":
			return "Exam Writing Tips"
		if str(post_id) == "139916342267":
			return "The Envy Bowdry"




if __name__ == "__main__":
	scraper = TumblrScraper()
	for key, value in scraper._titles.items():
		print(key, value)
		print("\n")