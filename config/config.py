import config.auth as cfg_auth

# Use these asserts for easier debugging of issues when
# someone clones the repo but doesn't update the auth.py-TEMPLATE to auth.py
# These are put in that file so passwords and tokens aren't on GitHub
assert cfg_auth.username
assert cfg_auth.password
assert cfg_auth.discord_token
assert cfg_auth.base_dir

PROD_DB = 'prod_swgoh.sqlite3'
DEV_DB = 'dev.sqlite3'
username = cfg_auth.username
password = cfg_auth.password
discord_token = cfg_auth.discord_token
base_dir = cfg_auth.base_dir
