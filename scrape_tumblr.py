import json 
import pytumblr

''' Parse credentials from options.json file in same dir

Arguments:
filename -- the name of the json file to read from
	Both an absolute path and a local path are acceptable

Returns [consumer_key, consumer_secret] from the json filename arg

'''
def get_credentials(filename):
	with open(filename, "r") as file:
		file_options = json.load(file)
	return [file_options['consumer_key'], file_options['consumer_secret']]


''' Parse blog url from options.json file in same dir

Arguments:
filename -- the name of the json file to read from
	Both an absolute path and a local path are acceptable

Returns blog_url from the json filename arg

'''
def get_blog_url(filename):
	with open(filename, "r") as file:
		file_options = json.load(file)
	return file_options['blog']


if __name__ == "__main__":
	consumer_key, consumer_secret = get_credentials("options.json")
	blog_name = get_blog_url("options.json")
	