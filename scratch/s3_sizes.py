import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ns = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}
days_to_check = [
    'Wednesday-21-02-2018',
    'Thursday-22-02-2018',
    'Wednesday-28-02-2018',
    'Thursday-01-03-2018',
    'Friday-02-03-2018',
    'Wednesday-14-02-2018',
]

for day in days_to_check:
    prefix = 'Original Network Traffic and Log data/' + day + '/'
    url = ('https://cse-cic-ids2018.s3.amazonaws.com/?list-type=2&prefix='
           + urllib.parse.quote(prefix))
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        root = ET.fromstring(resp.read())
    contents = root.findall('s3:Contents', ns)
    print('=== ' + day + ' ===')
    for c in contents:
        k = c.find('s3:Key', ns).text
        sz = c.find('s3:Size', ns).text
        if int(sz) > 0:
            print('  ' + k.split('/')[-1] + '  ' + str(int(sz)) + ' bytes (' + str(round(int(sz)/1024/1024,1)) + ' MB)')
