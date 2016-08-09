#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import cgi, cgitb
import os
import io, locale

def main():
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='shift_jis', errors='ignore')
  print('Content-type: application/octet-stream;\r\nContent-Disposition: attachment; filename="sample_search_console.csv"\r\n')

  with open('sample_search_console.csv', encoding='utf-8', errors='ignore') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
      print(', '.join(row))

if __name__ == '__main__':
  main()