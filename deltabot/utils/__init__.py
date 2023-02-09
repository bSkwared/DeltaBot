import config
import json
import logging
import os
import requests
# Random utility functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(config.TMP_DIR, 'bot.log'))
handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
                                       '%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)


def get_retry(get_fn, url, retries=3):
    for _ in range(retries):
        r = get_fn(url)
        if r:
            return r

    logger.error(f'Unable to retrieve from {url}')
    return None

def get_url_json(url):
    try:
        return json.loads(get_url_raw(url))
    except Exception as e:
        logger.error(f'Unable to load json from {url}: {e}')
        return None
    
def get_url_raw(url, timeouts=(3.05, 10)):
    try:
        response = requests.get(url, timeout=timeouts)
        return response.content
    except requests.exceptions.ReadTimeout as e:
        logger.error(f'Timed out connecting to {url}: {e}')
    except Exception as e:
        logger.error(f'Unable to read {url}: {e}')

    return None


def safe_write(filename, content):
    open_perms = 'w' if isinstance(content, str) else 'wb'
    tmp_path = f'{filename}.tmp'
    try:
        with open(tmp_path, open_perms) as fp:
            fp.write(content)
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(tmp_path, filename)
    except:
        logger.error(f'Failed to update {filename} with type {type(content)}')

def sanitize_unit_name(name):
    return ''.join(c if c.isalnum() else '_' for c in name)

def update_unit_images():
    units = get_retry(get_url_json, "http://api.swgoh.gg/units/")
    if not isinstance(units, dict):
        logger.error(f'Expected list of units from swgoh.gg. Got {type(units)}: {units}')
        return
    if 'data' not in units:
        logger.error(f'Missing "data" field from dict {units}')
        return

    for unit in units['data']:
        if not ('name' in unit and 'image' in unit):
            logging.error(f'name and image missing from {unit}')
            continue

        img_type = unit['image'].split('.')[-1]
        unit_path_name = f'{sasnitize_unit_name(unit["name"])}.{img_type}'
        final_path = os.path.join(config.TMP_DIR, unit_path_name)
        if os.path.exists(final_path):
            continue
        logger.info(f'Updating image for {unit["name"]} to {final_path}')
        for _ in range(3):
            img_data = get_url_raw(unit['image'])
            if img_data:
                break

        if not img_data:
            raise Exception()

        safe_write(final_path, img_data)

