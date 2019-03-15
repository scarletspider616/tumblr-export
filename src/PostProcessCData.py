#!/usr/bin/python
import sys
def add_cdata(filename):
	new_lines = list()
	with open(filename, "r") as xml_file:
		for line in xml_file:
			line = line.replace(r"CDATA_START", r"<![CDATA[").replace(r"CDATA_END", r"]]>")
			line = line.replace(r"IMG_TAG_START", r'<img src="').replace(r"IMG_TAG_END", r'"/>')
			line = line.replace(r"BREAK_TAG", r"<br/>")
			new_lines.append(line)
	header_lines = list()
	with open("header.xml", "r") as header_file:
		for line in header_file:
			header_lines.append(line)
	with open(filename, "w") as new_file:
		for line in header_lines:
			new_file.write(line)
		for line in new_lines:
			new_file.write(line)



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: ./" + sys.argv[0] + " <filename.xml>")
		exit(-1)
	add_cdata(sys.argv[1])