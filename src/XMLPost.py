import xml.etree.cElementTree as tree
# import xml.etree.CDATA as CDATA

# https://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def prettyPrintET(etNode):
    reader = Sax2.Reader()
    docNode = reader.fromString(ET.tostring(etNode))
    tmpStream = StringIO()
    PrettyPrint(docNode, stream=tmpStream)
    return tmpStream.getvalue()

class XMLPost:
	def __init__(self, id, title, body, tags, photos, date, category):
		self._id = id
		self._title = title
		self._body = body
		self._tags = tags
		self._photos = photos
		self._date = date
		self._category = category

	def generate_xml(self):
		item = tree.Element("item")
		tree.SubElement(item, "link").text = "http://when-im-older.com/post" + self._id
		tree.SubElement(item, "title").text = str(self._title)
		tree.SubElement(item, "pubDate").text = str(self._date)
		tree.SubElement(item, "dc:creator").text = "Taylor Doucette"
		tree.SubElement(item, "content:encoded").text = self._wrap_in_cdata(self._gen_images() + self._body)
		tree.SubElement(item, "wp:status").text = "publish"
		tree.SubElement(item, "wp:post_date").text = str(self._date) 
		tree.SubElement(item, "wp:post_date_gmt").text = str(self._date)
		tree.SubElement(item, "wp:ping_status").text = "closed"
		tree.SubElement(item, "wp:comment_status").text = "closed"
		tree.SubElement(item, "wp:post_type").text = "post"
		tree.SubElement(item, "wp:post_password").text = ""
		tree.SubElement(item, "wp:menu_order").text = "0"
		tree.SubElement(item, "wp:post_parent").text = "0"
		tree.SubElement(item, "description").text = ""
		tree.SubElement(item, "wp:post_name").text = str(self._id)
		self._gen_tags(item)
		return item

	def _gen_tags(self, item):
		if self._category:
			tree.SubElement(item, "category", domain="category", nicename=self._category).text = \
					str(self._wrap_in_cdata(self._category))
		for tag in self._tags:
			tree.SubElement(item, "category", domain="tag").text = str(self._wrap_in_cdata(tag))
			tree.SubElement(item, "category", domain="tag", nicename=tag).text = str(self._wrap_in_cdata(tag))

	def _wrap_in_cdata(self, original_data):
		# prefix = r"<![CDATA["
		# suffix = r"]]>"
		# print(prefix + original_data + suffix)
		# return prefix + original_data + suffix
		return "CDATA_START" + str(original_data) + "CDATA_END"

	def _gen_images(self):
		result = ""
		for photo in self._photos:
			result += "IMG_TAG_START" + str(photo) + "IMG_TAG_ENDBREAK_TAG"
		return result

if __name__ == "__main__":
	post = XMLPost("1", "fake_title", "fake_body_of_text fiasdjoifjaswoijfsdoa", ["cool", "post", "bro"], 
		["https://cnet4.cbsistatic.com/img/SPn24bmx9mm7jKE-3iZgRWjurJw=/2018/04/18/b0d2e71b-f600-41b4-9075-af845f1e6531/p-incredible-hero-avengers-58e3c823.jpg",
		 "https://www.google.com/url?sa=i&rct=j&q=&esrc=s&source=images&cd=&cad=rja&uact=8&ved=2ahUKEwjhqembi4PhAhWWup4KHen1BPsQjRx6BAgBEAU&url=https%3A%2F%2Fwww.polygon.com%2Fspider-man-ps4-guide%2F2018%2F9%2F10%2F17841942%2Fselfie&psig=AOvVaw0seJ_wIIY7Yko4kXH-mCXt&ust=1552702885153545",
		 "https://www.google.com/url?sa=i&rct=j&q=&esrc=s&source=images&cd=&ved=2ahUKEwicjf6ji4PhAhWVvJ4KHSwIB4YQjRx6BAgBEAU&url=https%3A%2F%2Fwww.imdb.com%2Ftitle%2Ftt4154664%2F&psig=AOvVaw1XbDkWMBuVRe4_Ilj2kOFH&ust=1552702923373070"], "1995-12-01 10:13:00")
	result = post.generate_xml()
	indent(result)
	final_result = tree.ElementTree(result)
	tree.dump(final_result)
	final_result.write("output.xml", encoding="utf-8")