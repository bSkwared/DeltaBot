import config
import json
import os
import stackprinter
import urllib.request

# Get json list of characters
contents = urllib.request.urlopen("http://api.swgoh.gg/units/").read()
units = json.loads(contents)
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#urllib.request.urlopen("https://game-assets.swgoh.gg/tex.charui_triplezero.png", headers=headers).read()
#1 / 0
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)


# Iterate json list and write images to base_dir/tmp
for unit in units['data']:
    try:
        #os.remove(os.path.join(CFG.base_dir, 'tmp', unit['name']))
        unit_path_name = ''.join(c if c.isalnum() else '_' for c in unit['name']) + '.' + unit['image'].split('.')[-1]
        urllib.request.urlretrieve(unit['image'], os.path.join(config.base_dir, 'tmp', unit_path_name))
    except:
        stackprinter.show()
        raise



