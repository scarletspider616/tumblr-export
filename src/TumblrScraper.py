import json 
import pytumblr
import re
import calendar
import sys # remove me
from datetime import datetime
from XMLPost import *

import xml.etree.cElementTree as tree

global_test = None

# import exceptions

# https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


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
		self._bodies = dict()
		self._photos = dict()
		self._dates = dict()
		self._tags = dict()
		self._categories = dict()
		for post in self._posts:
			post_id = str(post['id'])
			self._titles[post_id], self._bodies[post_id] = self.get_title_and_body(post)
			self._photos[post_id] = self._get_photos(post, post['id'])
			self._dates[post_id] = self._get_date(post)
			self._tags[post_id] = self._get_tags(post)
			self._categories[post_id] = self._get_category(post_id)


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


	''' Returns a dict obj with keys of post id and values of an ordered
	list of urls for photos associated with that post
	'''
	def get_photos(self):
		return self._photos

	'''Returns a dict obj with keys of post id and values of a list of (str) tags associated
	with that post
	'''
	def get_tags(self):
		return self._tags

	'''Returns a list of the tags associated with that post
	'''
	def _get_tags(self, post):
		return post['tags']


	''' Parses a post entry for the title 

	Of all methods in this lib, this is the sketchiest, as its based entirely on parsing Taylor's blog, which 
	just uses a header at the top of the post as a title. As far as I know, Tumblr does not have an official 
	"Title" field, although I may be wrong
	'''
	def get_title_and_body(self, post):
		if str(post['id']) == "50829013836":
			# skipping this problematic video post for now, can do manually if needed
			return "", ""
		if self._posts_without_titles(str(post['id'])):
			return self._posts_without_titles(str(post['id'])), ""
		try:
			text = self._parse_out_text(str(post['trail']), post['id'])
		except:
			return "", ""  # post has no text whatsoever
		title_match = re.search(r'<p>(.*?)</p>\n(.*)', text)
		if title_match:
			print(cleanhtml(title_match.group(1)), title_match.group(2))
			return cleanhtml(title_match.group(1)), title_match.group(2)
		title_match = re.search(r'<p><h2><center>(.*?)</center></h2>(.*)', text)
		if title_match:
			return cleanhtml(title_match.group(1)), title_match.group(2)
		title_match = re.search(r'<p><h2><center><b>(.*?)</b></center></h2><p><b>', text)
		if title_match:
			return cleanhtml(title_match.group(1)), title_match.group(2)
		title_match = re.search(r'<p><h2>(.*?)</h2><p>(.*)', text)
		if title_match:
			return cleanhtml(title_match.group(1)), title_match.group(2)
		title_match = re.search(r'<p><center><h2>(.*?)</h2></center><p>(.*)', text)
		if title_match:
			return cleanhtml(title_match.group(1)), title_match.group(2)
		title_match = re.search(r'<p><h2>(.*)</h2>\\n<p>(.*)', text)
		if title_match:
			return cleanhtml(title_match.group(1)), title_match.group(2)
		music_playlist_match = re.search(r'<p><b>1\..*?</b></p><p>.*?<p><b>2\.', text)
		if music_playlist_match:
			# if it matched that nonsense, its almost definitely an OLD music playlist post that didn't have a title
			# in the post
			# get the month & year and throw that in the title
			date = str(post['date'])
			date_match = re.search(r'([0-9]{4})-([0-9]{2})-[0-9]{2}.*', date)
			year = date_match.group(1)
			month = calendar.month_abbr[int(date_match.group(2))]
			return (month + " " + year[2] + year[3] + " Music Playlist"), text
		return "", text

	def get_body(self, post, title):
		if title != "":
			pass

	# TODO Make this configurable over JSON? Or is this whole project whenimolder specific now? 
	def _get_category(self, id):
		tags = self._tags[id]
		if "ootd" in tags:
			return "style"
		if "makeup" in tags:
			return "beauty"
		if "school" in tags:
			return "university"
		if "skincare" in tags:
			return "skincare"
		if "music" in tags:
			return "music"
		else:
			return None

	''' Parses a tumblr api dump of data into the actual post content
	'''
	def _parse_out_text(self, text, post_id):
		first_split = text.split("\'content_raw\': ", 1)
		if (first_split[1].find(", \'is_current_item\': ") < first_split[1].find(", \'content\': ")):
			second_split = first_split[1].split(", \'is_current_item\': ", 1)
		else:
			second_split = first_split[1].split(", \'content\': ", 1)
		result = second_split[0]
		if ((result[-1] != "'" and result[-1] != '"') or (result[0] != "'" and result[0] != '"')):
			print(first_split[1])
			print("\n\n\n\n")
			print(second_split[0])
			print(post_id)
		result = result[:-1]
		result = result[0:]
		return result


	''' These nightmarish exceptions on Taylor's blog HSVE NO TITLES OR HAVE TITLES 
	IN A PHOTO WHICH IS THE WORST THING EVER
	'''
	# todo: turn this nightmare into a dict
	def _posts_without_titles(self, post_id):
	# 	if str(post_id) == "150965735430":
	# 		# exception case, this particular post only has a title in its photo!
	# 		# fun times
	# 		return "Make It Yourself Monday Part 2"
	# 	# if str(post_id) == "143758273428":
	# 	# 	# exception case, this particular post only has a title in its photo!
	# 	# 	# fun times
	# 	# 	return "May Music Playlist" # 2016
	# 	# 	# no doubt one of many may music playlists!
	# 	# if str(post_id) == "142080113913":
	# 	# 	return "April Music Playlist" # 2016
	# 	if str(post_id) == "141149831439":
	# 		return "Exam Writing Tips"
	# 	if str(post_id) == "139916342267":
	# 		return "The Envy Bowdry"
		if str(post_id) == "139490739526":
			return "Paula's Choice Skincare Routine", "temp" # this is the one with the ftc disclaimer
		if str(post_id) == "141035303554":
			# putting an exception here because its late and I'm tired 
			# if future joey wants to fix the regex on this one, feel free. It SHOULD be working
			return "First Aid Beauty Ultra Repair Lip Therapy Review", "temp"
		if str(post_id) == "145965113520":
			return "Benefit Brows Part 2", "temp"
		if str(post_id) == "149083287801":
			return "Joe Fresh Lip Products", "temp"
	# 	if str(post_id) == "139300613151":
	# 		return "12 Movies You Should Watch on Valentine's Day"
	# 	if str(post_id) == "138287515553":
	# 		return "What My Mom Has Taught Me About Relationships"

	# Whenimolder's post formats actually match the standard tumblr structure wrt photos, 
	# so this ends up being MUCH nicer and without all that horrifying parsing stuff. 
	# something to consider in the future: Do we need image sizes?
	def _get_photos(self, post, post_id):
		results = list()
		try:
			for photo in post['photos']:
				results.append(photo["original_size"]["url"]) # thinking OG size is the way to go here
				# if this becomes an issue, we can save every photo size available with its dimensions, 
				# create a dict and pass them all through but then need to find out how wordpress 
				# handles alternate sizes
		except:
			# no photos in this post
			return list()
		return results

	# another straightforward one, lets just grab the date for this post... 
	def _get_date(self, post):
		result = datetime.strptime(post["date"].strip("GMT")[:-1], '%Y-%m-%d %H:%M:%S')
		return str(result)
			



if __name__ == "__main__":
	scraper = TumblrScraper()
	scraper.initialize()
	# badpracticebadpracticebadpracticebadpractice
	with open("output.xml", "wb") as out_file:
		for post_id in scraper._titles.keys():
			post = XMLPost(post_id, scraper._titles[post_id], scraper._bodies[post_id],
						   scraper._tags[post_id], scraper._photos[post_id], scraper._dates[post_id],
						   scraper._categories[post_id])
			item = post.generate_xml()
			indent(item)
			result = tree.ElementTree(item)
			result.write(out_file, encoding="utf-8")



