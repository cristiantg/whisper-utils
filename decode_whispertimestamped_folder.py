# This script decodes an entire folder of audio files using Whisper-timestamped.
# If the transcription is already on the output directory, the audio file it is not decoded.
# 
# Usage (on Ponyland):
#
# ssh mistmane
# nvidia-smi (see if at least one GPU is at 0% capacity, if not change to another Pony with GPUs)
# cd /vol/tensusers5/ctejedor/whisper && source venv/bin/activate
# python3 decode_whispertimestamped_folder.py input_folder whisper_model lang_code output_folder cache_model_folder prompts_folder[0 for none]
# 
# Note: each pair of audio-prompt files must have the same name (different extension) in each corresponding folder (by default .prompt for the prompts extension)
# Note: if the transcription is found in the output folder before the decoding, the file will be skipped.
# @since 2023/02/07

# Examples:
# nohup time python3 decode_whispertimestamped_folder.py audio/en tiny en output/en /vol/tensusers5/ctejedor/whisper/models 0 &
# python3 decode_whispertimestamped_folder.py audio/examples tiny nl output/nl /vol/tensusers5/ctejedor/whisper/models 0
# nohup time python3 decode_whispertimestamped_folder.py /vol/tensusers5/ctejedor/whisper/audio/dart-long large-v2 nl output/dart-long /vol/tensusers5/ctejedor/whisper/models 0 &
# nohup time python3 decode_whispertimestamped_folder.py /vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_egs_CGN/s5/astla_is/kaldi_nl_input large-v2 nl output/dart-whisper-prompts /vol/tensusers5/ctejedor/whisper/models /vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_egs_CGN/s5/astla_is/kaldi_nl_input_prompts &

# nohup time python3 decode_whispertimestamped_folder.py /vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_jasmin/Beeldverhaal/utterances large-v2 nl output/beeldverhaal /vol/tensusers5/ctejedor/whisper/models 0 &


import sys
MY_DIR=sys.argv[1]
MODEL=sys.argv[2]
MODEL_LANG=sys.argv[3]
OUTPUT_DIR=sys.argv[4]
STORE_MODEL=sys.argv[5]
PROMPTS_FOLDER=sys.argv[6]
check_initial_prompt=False if PROMPTS_FOLDER=='0' else True
PROMPT_EXTENSION='.prompt'


import os
from os.path import isfile, join

import json
print("Loading Whisper timestamped...",end='')
import whisper_timestamped as whisper
print('done')
from pathlib import Path
print("Downloading & loading model...",MODEL)
model = whisper.load_model(MODEL, download_root=STORE_MODEL)


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
        audio = whisper.load_audio(join(MY_DIR,file))
        result = ''
        if check_initial_prompt:
            with open(join(PROMPTS_FOLDER,filebase+PROMPT_EXTENSION)) as prompt_f:
                try:
                    result = whisper.transcribe(model, audio, language=MODEL_LANG, initial_prompt=prompt_f.read().strip())
                except:                    
                    try:
                        print("**-** Error --> ",str(counter), file, "trying again without prompt...")
                        result = whisper.transcribe(model, audio, language=MODEL_LANG)
                        print("**-** Fixed --> ",str(counter), file, " OK after trying without prompt...")
                    except:
                        print("**-** Error again --> ",str(counter), file, "skipping this file ...")
                        continue
        else:
            result = whisper.transcribe(model, audio, language=MODEL_LANG)

        with open(join(OUTPUT_DIR,filebase+'.json'), "w") as outfile:
            outfile.write(json.dumps(result, indent = 2, ensure_ascii = False))
        with open(join(OUTPUT_DIR,filebase+'.txt'), "w") as outfile:
            outfile.write(result["text"])

        counter+=1

print('Total files decoded', str(counter-1))
print('See all **-** for errors')