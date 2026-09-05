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
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            root = ET.fromstring(resp.read())
        contents = root.findall('s3:Contents', ns)
        all_keys = [c.find('s3:Key', ns).text for c in contents]
        sizes = {c.find('s3:Key', ns).text: c.find('s3:Size', ns).text for c in contents}
        pcaps = [k for k in all_keys if k.lower().endswith('.pcap') or k.lower().endswith('.pcapng')]
        print('')
        print('=== ' + day + ' ===')
        print('  Total objects: ' + str(len(all_keys)))
        print('  PCAP files: ' + str(len(pcaps)))
        for p in pcaps:
            print('    ' + p + '  (' + str(int(sizes[p])) + ' bytes)')
        if not pcaps:
            exts = []
            for k in all_keys:
                ext = k.rsplit('.', 1)[-1] if '.' in k else '(no ext)'
                if ext not in exts:
                    exts.append(ext)
            print('  Extensions present: ' + str(exts))
            for k in all_keys[:3]:
                print('    sample key: ' + k)
    except Exception as e:
        print('  ERROR for ' + day + ': ' + str(e))
