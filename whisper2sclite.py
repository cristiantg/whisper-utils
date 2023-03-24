# Prepares a ref/hyp file for SCLITE from a folder of files with the text 
# transriptions (in one line).

import os
from os.path import isfile, join


import sys
if len(sys.argv) != 4:
    print(sys.argv[0] + "Please, specify 3 parameters: hyp-filepath ref-filepath")
    # python3 whisper2sclite.py output/dart-whisper-vad wer-vad/hyp-vad-prompts.txt txt
    sys.exit(2)
[INPUT_DIR, OUTPUT_SCLITE_FILE, EXTENSION] = sys.argv[1:4]
INPUT_EXTENSION=[EXTENSION]

import re

onlyfiles = [f for f in os.listdir(INPUT_DIR) if isfile(join(INPUT_DIR, f))]
ext_files = 0
with open(OUTPUT_SCLITE_FILE,'w') as sclite_f :
    for file in onlyfiles:
        for ext in INPUT_EXTENSION:
            if file.endswith(ext):
                file_id=file.split('.')[0].replace('-','_')
                #print(file_id)
                ext_files+=1
                with open(join(INPUT_DIR, file), 'r') as f:
                    prompt_lower = re.sub('[^a-zA-Z ]+', '',re.sub(' +', ' ',f.read().lower().replace('.',' ').strip()))
                    sclite_f.write(prompt_lower+' ('+file_id.replace('-','_')+'-1)\n')
print(str(ext_files),'files with the extension(s)',INPUT_EXTENSION)