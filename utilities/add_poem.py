#!/usr/bin/env python3

"""
Copyright 2015 Stefano Benvenuti <ste.benve86@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import os
import json
import shutil


# helper function for reading a file content
def read_file(filename):
	f = None
	try:
		f = open(filename)
		content = json.load(f)
	except Exception as e:
		print("File \"%s\" cannot be opened or read: %s", filename, e)
		sys.exit(1)
	finally:
		if f is not None:
			f.close()
	return content


if len(sys.argv) is not 2:
	print("""
USAGE: ./add_poem.py JSON_DELTA_FILE_PATH
	""")
	sys.exit(1)

conf_file = os.path.join("..","poems","poems.json")
# reads old configuration file and new content
content = read_file(conf_file)
new_content = read_file(sys.argv[1])
# merge the values
content.update(new_content)
# write file
shutil.copyfile(conf_file, conf_file + ".bak")
f = None
try:
	f = open(conf_file,'w')
	json.dump(content, f)
except Exception as e:
	print("File \"%s\" cannot be opened or written: %s", filename, e)
	sys.exit(1)
finally:
	if f is not None:
		f.close()

