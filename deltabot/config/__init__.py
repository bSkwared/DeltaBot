import os.path

import config.local as local


# These configs must be provided by local.py
allycode = int
discord_token = str
healthcheck_url = str
accomplishments_channel_id = int
accomplishments_thread_id = int
officers_channel_id = int
relics_thread_id = int


# These configs may optionally be set by local.py
# Really all that would make sense to configure 
# would be BASE_DIR, if you want to store the
# the bigger files in another directory.
resource_dir_name = 'resources'
tmp_dir_name = 'tmp'
daily_data_dir_name = 'daily_data'
stats_db_name = 'stats.sqlite3'

__current_dir = os.path.split(os.path.realpath(__file__))[0]
base_dir = os.path.split(__current_dir)[0]


# Use these asserts for easier debugging of issues when
# someone clones the repo but doesn't update the local.py-TEMPLATE to local.py
# These are put in that file so passwords and tokens aren't on GitHub
required_locals = {k for k, v in locals().items() if not k.startswith('__') and isinstance(v, type)}
provided_locals = {k for k in local.__dict__.keys() if not k.startswith('__')}
assert provided_locals == required_locals, 'Please update config/local.py with ' \
                                           'your local specific configurations'

# This will update the local variables if values were provided
# in the local.py file. Any variable within this file can be overwritten
# by setting the same variable in local.py. This allows for more
# customized configurations that are not updated by git pulls
for k, v in local.__dict__.items():
    if k.startswith('__'):
        continue

    current_local = locals()[k]
    expected_type = (current_local if isinstance(current_local, type)
                     else type(current_local))
    assert type(v) == expected_type, f'Expected {k} from local.py to be ' \
                                     f'of type {expected_type}, got {type(v)}'

    locals()[k] = v


# These configs SHALL NOT be set by local.py
TMP_DIR = os.path.join(base_dir, tmp_dir_name)
RESOURCE_DIR = os.path.join(base_dir, resource_dir_name)
DAILY_DATA_DIR = os.path.join(base_dir, daily_data_dir_name)
STATS_DB = os.path.join(TMP_DIR, stats_db_name)
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(RESOURCE_DIR, exist_ok=True)
os.makedirs(DAILY_DATA_DIR, exist_ok=True)
