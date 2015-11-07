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

separator = "CANTO"
#separator = "LIBRO"
counter = 0
counting = False

if len(sys.argv) is not 2:
	print("""
USAGE: ./remove_empty_lines.py FILENAME_IN > FILENAME_OUT
	""")
	sys.exit(1)

with open(sys.argv[1]) as f:

	for line in f:

		# read a line
		line_s = line.strip()

		# empty line
		if line_s == "":
			if not counting:
				print()
			continue
 
		# a new canto, counter reset
		if line_s.startswith(separator) or line_s.startswith("["):
			print(line_s)
			counter = 0
			counting = False
			continue

		# updates counter, printed every 3 lines
		print(line_s)
		counting = True
