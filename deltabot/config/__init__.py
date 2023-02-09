import config.auth as cfg_auth

# Use these asserts for easier debugging of issues when
# someone clones the repo but doesn't update the auth.py-TEMPLATE to auth.py
# These are put in that file so passwords and tokens aren't on GitHub
assert cfg_auth.allycode
assert cfg_auth.username
assert cfg_auth.password
assert cfg_auth.discord_token
assert cfg_auth.base_dir
assert cfg_auth.healthcheck_url
assert cfg_auth.accomplishments_channel_id
assert cfg_auth.accomplishments_thread_id

PROD_DB = 'prod_swgoh.sqlite3'
DEV_DB = 'dev.sqlite3'
allycode = cfg_auth.allycode
username = cfg_auth.username
password = cfg_auth.password
discord_token = cfg_auth.discord_token
base_dir = cfg_auth.base_dir
healthcheck_url = cfg_auth.healthcheck_url
accomplishments_channel_id = cfg_auth.accomplishments_channel_id
accomplishments_thread_id = cfg_auth.accomplishments_thread_id
