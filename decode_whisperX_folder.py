# This script decodes an entire folder of audio files using Whisper-X.
# If the transcription is already on the output directory, the audio file it is not decoded.
# WhisperX provides timestamps with VAD, while Whisper-timestamped provides argmax of the timestamps
# 
# Usage (on Ponyland):
#
# #First Run the commands on step # 1. Setup (just for the first time)
# ssh mistmane
# nvidia-smi (see if at least one GPU is at 0% capacity, if not change to another Pony with GPUs)
# cd /vol/tensusers5/ctejedor/whisper && source venv/bin/activate
# python3 decode_whisperX_folder.py input_folder whisper_model lang_code[0 for autom. detection] output_folder cache_model_folder prompts_folder[0 for none]
# 
# Note: each pair of audio-prompt files must have the same name (different extension) in each corresponding folder (by default .prompt for the prompts extension)
# Note: if the transcription is found in the output folder before the decoding, the file will be skipped.
# @since 2023/02/07

# Examples:
# python3 decode_whisperX_folder.py audio/examples tiny 0 output/nl /vol/tensusers5/ctejedor/whisper/models 0
# nohup time python3 decode_whisperX_folder.py audio/en tiny en output/en /vol/tensusers5/ctejedor/whisper/models 0 &


import sys
MY_DIR=sys.argv[1]
MODEL=sys.argv[2]
MODEL_LANG=sys.argv[3]
OUTPUT_DIR=sys.argv[4]
STORE_MODEL=sys.argv[5]
PROMPTS_FOLDER=sys.argv[6]
PROMPT_EXTENSION='.prompt'
device = "cuda" 

NO_PARAM='0'
check_initial_prompt=False if PROMPTS_FOLDER==NO_PARAM else True
MODEL_LANG = None if MODEL_LANG == NO_PARAM else MODEL_LANG


import os
from os.path import isfile, join

import json
print("Loading Whisper X... ",end='')
import whisperx
import whisper 
print('done')
from pathlib import Path
print("Downloading & loading model...",MODEL)
model = whisper.load_model(MODEL, download_root=STORE_MODEL, device=device)


onlyfiles = [f for f in os.listdir(MY_DIR) if isfile(join(MY_DIR, f))]

if not os.path.exists(OUTPUT_DIR):
    print("Created directory",OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
counter=1
for file in onlyfiles:
    filebase = file.split('.')[0]
    #This condition is optional, is to not repeat the decoding for files we already have the transcription in OUTPUT_DIR
    if not Path(join(OUTPUT_DIR,filebase+'.txt')).is_file() or not Path(join(OUTPUT_DIR,filebase+'.json')).is_file():
        print(str(counter), file)
        audio_file = join(MY_DIR,file)
        result = ''
        if check_initial_prompt:
            with open(join(PROMPTS_FOLDER,filebase+PROMPT_EXTENSION)) as prompt_f:
                try:
                    result = model.transcribe(audio_file, language = MODEL_LANG, initial_prompt=prompt_f.read().strip())
                except:                    
                    try:
                        print("**-** Error --> ",str(counter), file, "trying again without prompt...")
                        result = model.transcribe(audio_file, language = MODEL_LANG)
                        print("**-** Fixed --> ",str(counter), file, " OK after trying without prompt...")
                    except:
                        print("**-** Error again --> ",str(counter), file, "skipping this file ...")
                        
        else:
            try:
                result = model.transcribe(audio_file, language = MODEL_LANG)
            except:
                print("**-** Error decoding --> ",str(counter), file, "skipping this file ...")


        try:
            # load alignment model and metadata
            model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
            with open(join(OUTPUT_DIR,filebase+'.json'), "w") as outfile:
                outfile.write(json.dumps(result, indent = 2, ensure_ascii = False))
            with open(join(OUTPUT_DIR,filebase+'.txt'), "w") as outfile:
                outfile.write(result["text"])
        except:
            print("**-** Error load alignment model and metadata --> ",str(counter), file, " not possible to write results ...")

        try:
            # align whisper output
            result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_file, device)
            #["segments"]) # after alignment
            #print(result_aligned["word_segments"]) # after alignment'
            with open(join(OUTPUT_DIR,filebase+'_timestamps.json'), "w") as outfile:
                outfile.write(json.dumps(result_aligned["word_segments"], indent = 2, ensure_ascii = False))
        except:
            print("**-** Error align whisper output --> ",str(counter), file, " not possible to write results ...")

        counter+=1

print('Total files decoded', str(counter-1))
print('See all **-** for errors')