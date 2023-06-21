#python3 decode_whisper_folder.py audio_folder model language output_folder

# python3 decode_whisper_folder.py audio/en tiny en output/en
# python3 decode_whisper_folder.py /vol/tensusers5/mbentum/dart_wav tiny nl output/dartwav
# python3 decode_whisper_folder.py /vol/tensusers5/mbentum/dart_wav large nl output/dartwav-large

import os
from os.path import isfile, join
import sys
print("Loading Whisper... ")
import whisper
from datetime import timedelta


MODEL=sys.argv[2]
print("Downloading & loading model... ",MODEL)
model = whisper.load_model(MODEL, download_root="/vol/tensusers5/ctejedor/whisper/models")


MY_DIR=sys.argv[1]
onlyfiles = [f for f in os.listdir(MY_DIR) if isfile(join(MY_DIR, f))]
OUTPUT_DIR=sys.argv[4]
if not os.path.exists(OUTPUT_DIR):
    print("Created directory",OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

for file in onlyfiles:
    
    file_segments=join(OUTPUT_DIR,os.(path.basename(file).rsplit('.', maxsplit=1)[0])+'.srt')
    print(file, file_segments)
    model.language=sys.argv[3]
    result = model.transcribe(join(MY_DIR,file),language=model.language)
    print("Language:", model.language, result["language"])
    print("Output:",result["text"])
    segments = result['segments']
    with open(file_segments, 'a', encoding='utf-8') as srtFile:
        for segment in segments:
            startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
            endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
            text = segment['text']
            segmentId = segment['id']+1
            segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] == ' ' else text}\n\n"
            srtFile.write(segment)
