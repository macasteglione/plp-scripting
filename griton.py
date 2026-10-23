#!/usr/bin/python
import sys

for line in sys.stdin:
  sys.stdout.write(line.upper().strip()+'!\n')
  sys.stdout.flush()
 

