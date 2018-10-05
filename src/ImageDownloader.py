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
		for post_id, data_tuple in tumblr_scraper.get_images():
			save_at = self._filename + post_id + ".jpg"
			request = requests.get(data_tuple[0], allow_redirects=True)
			open(save_at, 'wb').write(request.content)



if __name__ == "__main__":
	scraper = TumblerScraper()
	# lets dependency inject some magic friends


	

