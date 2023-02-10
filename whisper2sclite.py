# Prepares a hyp.txt file for SCLITE from a folder of files with the orthographical transcription in of the ASR decoding (in one line).

import os
from os.path import isfile, join

INPUT_DIR='/vol/tensusers5/ctejedor/whisper/output/beeldverhaal'
OUTPUT_SCLITE_FILE='/vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_jasmin/Beeldverhaal/whisper/hyp.txt'
INPUT_EXTENSION=['txt']

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