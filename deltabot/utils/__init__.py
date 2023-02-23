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


def get_retry(get_fn, url, retries=3):
    for _ in range(retries):
        r = get_fn(url)
        if r:
            return r

    logger.error(f'Unable to retrieve from {url}')
    return None


def get_raw_retry(url, retries=3):
    return get_retry(get_url_raw, url, retries)


def get_json_retry(url, retries=3):
    return get_retry(get_url_json, url, retries)


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


def safe_write_json(filename, content):
    safe_write(filename, json.dumps(content, indent=2))


def sanitize_unit_name(name):
    return ''.join(c if c.isalnum() else '_' for c in name)


def get_unit_img_path(name):
    return os.path.join(config.RESOURCE_DIR, f'{sanitize_unit_name(name)}.png')


# NOTE: if name is provided, the file image file will be 
# forced to update to the new image
def update_unit_images(name=None):
    units = get_json_retry("http://api.swgoh.gg/units/")
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

        if name != None and unit['name'] != name:
            continue

        img_type = unit['image'].split('.')[-1]
        assert img_type.lower() == 'png', f'Unexpected image format: {img_type}'

        final_path = get_unit_img_path(unit["name"])
        # If name is specified, force update the image
        if os.path.exists(final_path) and name == None:
            continue

        logger.info(f'Updating image for {unit["name"]} at {final_path}')
        img_data = get_raw_retry(unit['image'])

        if not img_data:
            logger.error(f'Unable to pull image data for {unit["name"]}')
            continue

        safe_write(final_path, img_data)

