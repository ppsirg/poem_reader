#!/usr/bin/env python3

import sys

counter = 0
num = False

with open(sys.argv[1]) as f:

  for line in f:

    line_s = line.strip()

    if line_s == "":
      if not num:
        print()
        num = False
      continue
 
    if line_s.startswith("CANTO") or line_s.startswith("["):
      print(line_s)
      counter = 0
      num = False
      continue

    counter += 1
    print(line_s)
    if counter % 3 == 0:
      print ("\t\t\t\t\t\t\t(" + str(counter) + ")")
      num = True
