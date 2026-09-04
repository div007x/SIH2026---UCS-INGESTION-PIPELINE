import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

prefix = 'Original Network Traffic and Log data/'
url = 'https://cse-cic-ids2018.s3.amazonaws.com/?list-type=2&delimiter=/&prefix=' + urllib.parse.quote(prefix)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    root = ET.fromstring(resp.read())

print("Sub-prefixes in 'Original Network Traffic and Log data/':")
ns = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}
for cp in root.findall('s3:CommonPrefixes', ns):
    p = cp.find('s3:Prefix', ns).text
    print(" ", p)

