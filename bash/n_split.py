#!/usr/bin/env python

import sys
import math

fsize = sys.stdin.read()
print max(1, int(math.ceil(float(fsize) / float(sys.argv[1]))))
