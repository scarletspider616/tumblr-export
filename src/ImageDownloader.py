from TumblrScraper import TumblrScraper
import requests

class ImageDownloader:

	''' ImageDownloader Constructor

	Arguments:
	filename (optional): filename (absolute or cwd) to the dir to store imgs
	'''

	def __init__(self, filename='assets'):
		self._filename = filename

	def _download_image(self, tumblr_scraper):
		used_urls = []
		for post_id, picture_list in tumblr_scraper.get_photos().items():
			photo_number = 0
			for picture in picture_list:
				save_at = self._filename + "/" + str(post_id) + "_" + str(photo_number) + ".jpg"
				request = requests.get(picture, allow_redirects=True)
				open(save_at, 'wb').write(request.content)
				photo_number = photo_number + 1



if __name__ == "__main__":
	scraper = TumblrScraper()
	# lets dependency inject some magic friends
	downloader = ImageDownloader()
	downloader._download_image(scraper)


	

