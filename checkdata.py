#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Check the IANA list of TLDs and add new ones to data.go
#
# Authors: Kris Hunt <github.com/sourcekris>
# License: BSD 2-Clause see LICENSE
#

import requests
import tempfile
import re

dataGo        = "data.go"
outFile       = "data.go.new"
ianaURL       = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
pubSuffixList = "https://publicsuffix.org/list/public_suffix_list.dat"

# parseDataGo parses a golang file containing known TLDs.
def parseDataGo(dataFile):
  dataList = [x.strip() for x in open(dataFile).readlines() if "TldItem{" in x]

  knownTLDList = []
  for dataLine in dataList:
    try:
      knownTLDList.append(dataLine.split('"')[3])
    except IndexError:
      print "Line is misformed: " + dataLine

  return knownTLDList

# downloadIanaTlds returns a list of TLDs from IANA's list.
def downloadIanaTlds():
  s = requests.Session()
  r = s.get(ianaURL)

  ianaTLDs = [x.strip().lower() for x in r.content.splitlines() if x and not x[0] == '#']

  s.close()
  return ianaTLDs

# downloadPubSuffixes returns a file object to a temp file with public suffixes in it.
def downloadPubSuffixes():
  s = requests.Session()
  r = s.get(pubSuffixList)

  tmpFile = tempfile.TemporaryFile()
  tmpFile.write(r.content)
  s.close()
  return tmpFile

# checkPubSuffix checks if str is a TLD known in the public suffix list file.
def checkPubSuffix(fh, str):
  fh.seek(0)

  line = True

  while line:
    line = fh.readline()

    if re.match("^" + str + "\s", line):
      return str.strip()

    # Look for an IDN match (e.g. xn--90ais)
    if re.match("^// " + str + "\s", line):
      # Search for and return the next uncommented line.
      while True:
        nextline = fh.readline()
        if not re.match("^//", nextline):
          return nextline.translate(None, '\n\r')

  # str is not in the Public Suffix list.
  return False

# writeNewDataGo writes a new data.go formatted file to outFile.
def writeNewDataGo(newList):
  of = open(outFile, "w+")

  with open(dataGo) as f:
    line = True
    while line:
      line = f.readline()

      if re.match("^}", line):
        for n in newList:
          of.write("\t" + n + "\n")
        of.write("}\n")
        of.close()
        return

      else:
        of.write(line.rstrip() + "\n")

if __name__ == "__main__":
  print "[+] Parsing " + dataGo
  knownTlds = parseDataGo(dataGo)
  print "[+] Downloading and parsing IANA TLDs"
  ianaTlds  = downloadIanaTlds()
  print "[+] Downloading Public Suffixes"
  pubSuffixFile = downloadPubSuffixes()
  print "[+] Comparing data.go with IANA TLDs"

  newList = []

  for i in ianaTlds:
    punycode = ""
    if i.startswith("xn--"):
      punycode = checkPubSuffix(pubSuffixFile, i)

      if not punycode:
        print "[-] %s not in public suffix list" % i

    if punycode not in knownTlds and i not in knownTlds:
      if not punycode:
        newList.append('tldMap["' + i + '"] = TldItem{Tld: "' + i + '"}')
      else:
        newList.append('tldMap["' + punycode + '"] = TldItem{Tld: "' + punycode + '"}')
        newList.append('tldMap["' + i + '"] = TldItem{Tld: "' + punycode + '"}')

    # Add IDN encoded versions.
    if punycode and punycode in knownTlds:
      newList.append('tldMap["' + i + '"] = TldItem{Tld: "' + punycode + '"}')

  print "[+] Writing new data file to " + outFile
  writeNewDataGo(newList)


