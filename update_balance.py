import datetime
import json
import os

from Clear import ClearFormat
from GuiaBolso import GuiaBolsoFormat
from Rico import RicoFormat
from pprint import pprint

date = datetime.datetime.today().strftime('%Y-%m-%d')
dir = 'output/' + date + '/'
files = os.listdir(dir)

for file in files:
    json_content = open(dir + file, "r").read()
    f = json.loads(json_content)

    file_split = file.split('.')
    format = file_split[0]

    if format == 'rico':
        # RicoFormat.format_json(f)
        print('Rico')
    elif format == 'clear':
        ClearFormat.format_json(f)
        print('Clear')
    elif format == 'smartt_bot':
        # ClearFormat.format_json(f)
        print('smartt_bot')
    elif format == 'guiabolso':
        # GuiaBolsoFormat.format_json(f)
        print('guiabolso')
