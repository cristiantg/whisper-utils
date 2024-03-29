# This script decodes an entire folder of audio files using Whisper-timestamped.
# If the transcription is already on the output directory, the audio file it is not decoded.
# WhisperX provides timestamps with VAD, while Whisper-timestamped provides argmax of the timestamps
# 
# Usage (on Ponyland):
# It is possible to run mutliple instances in different Ponies (not the same since teh GPU is exclusive)
# 
# #First Run the commands on step # 1. Setup (just for the first time)
# ssh mistmane
# nvidia-smi (see if at least one GPU is at 0% capacity, if not change to another Pony with GPUs)
# cd /vol/tensusers5/ctejedor/whisper && source venv/bin/activate
# python3 decode_whispertimestamped_folder.py input_folder whisper_model lang_code[0 for autom. detection] output_folder cache_model_folder prompts_folder[0 for none]
# 
# Note: each pair of audio-prompt files must have the same name (different extension) in each corresponding folder (by default .prompt for the prompts extension)
# Note: if the transcription is found in the output folder before the decoding, the file will be skipped.
# @since 2023/02/07

# Examples:
# python3 decode_whispertimestamped_folder.py audio/examples tiny 0 output/nl /vol/tensusers5/ctejedor/whisper/models 0
# nohup time python3 decode_whispertimestamped_folder.py audio/en tiny en output/en /vol/tensusers5/ctejedor/whisper/models 0 >> out.out &
# nohup time python3 decode_whispertimestamped_folder.py /vol/tensusers5/ctejedor/whisper/audio/dart-long large-v2 nl output/dart-long /vol/tensusers5/ctejedor/whisper/models 0 >> out.out &
# nohup time python3 decode_whispertimestamped_folder.py /vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_egs_CGN/s5/astla_is/kaldi_nl_input large nl output/dart-whisper-prompts-dis /vol/tensusers5/ctejedor/whisper/models /vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_egs_CGN/s5/astla_is/kaldi_nl_input_prompts >> out.out &

# nohup time python3 decode_whispertimestamped_folder.py /vol/tensusers4/ctejedor/lanewcristianmachine/opt/kaldi/egs/kaldi_jasmin/Beeldverhaal/utterances large-v2 nl output/beeldverhaal /vol/tensusers5/ctejedor/whisper/models 0 >> out.out &


# Improves the general output, change to False if needed:
do_VAD=True # No hallucinations
do_detect_disfluencies=True # [*] when a disfluence is found
do_precision=True # Better accuracy, higher latency
m_pres={}
if do_precision:
    m_pres={'beam_size':5, 'best_of':5, 'temperature':(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)}
print('\n+++ INTERNAL PARAMETERS +++\n','do_VAD',do_VAD,'do_detect_disfluencies',do_detect_disfluencies,'do_precision',do_precision)

import sys
MY_DIR=sys.argv[1]
MODEL=sys.argv[2]
MODEL_LANG=sys.argv[3]
OUTPUT_DIR=sys.argv[4]
STORE_MODEL=sys.argv[5]
PROMPTS_FOLDER=sys.argv[6]
PROMPT_EXTENSION='.prompt'


NO_PARAM='0'
check_initial_prompt=False if PROMPTS_FOLDER==NO_PARAM else True
MODEL_LANG = None if MODEL_LANG == NO_PARAM else MODEL_LANG


import os
from os.path import isfile, join

import json
print("Loading Whisper timestamped... ",end='')
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
    filebase = os.path.basename(file).rsplit('.', maxsplit=1)[0]
    #This condition is optional, is to not repeat the decoding for files we already have the transcription in OUTPUT_DIR
    if not Path(join(OUTPUT_DIR,filebase+'.txt')).is_file() or not Path(join(OUTPUT_DIR,filebase+'.json')).is_file():
        print(str(counter), file)
        audio = whisper.load_audio(join(MY_DIR,file))
        result = ''
        if check_initial_prompt:
            with open(join(PROMPTS_FOLDER,filebase+PROMPT_EXTENSION)) as prompt_f:
                try:
                    result = whisper.transcribe(model, audio, **m_pres, vad=do_VAD, detect_disfluencies=do_detect_disfluencies, language = MODEL_LANG, initial_prompt=prompt_f.read().strip())
                except:                    
                    try:
                        print("**-** Error --> ",str(counter), file, "trying again without prompt...")
                        result = whisper.transcribe(model, audio, **m_pres, vad=do_VAD, detect_disfluencies=do_detect_disfluencies, language = MODEL_LANG)
                        print("**-** Fixed --> ",str(counter), file, " OK after trying without prompt...")
                    except:
                        print("**-** Error again --> ",str(counter), file, "skipping this file ...")
                        
        else:
            try:
                result = whisper.transcribe(model, audio, **m_pres, vad=do_VAD, detect_disfluencies=do_detect_disfluencies, language = MODEL_LANG)
            except Exception as ex:
                print("**-** Error decoding --> ",str(counter), file, "skipping this file ...")
                print(ex)

        try:   
                with open(join(OUTPUT_DIR,filebase+'.json'), "w") as outfile:
                    outfile.write('' if type(result)==str else json.dumps(result, indent = 2, ensure_ascii = False))
                # This does not include disfluences and other info, better use the json output and process the file
                #with open(join(OUTPUT_DIR,filebase+'.txt'), "w") as outfile:
                #    outfile.write('' if type(result)==str else result["text"])
        except:
            print("**-** Error writing the model and metadata --> ",str(counter), file, " not possible to write results ...")
        counter+=1

print('Total files decoded', str(counter-1))
print('See all **-** for errors')