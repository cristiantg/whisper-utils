@since February 2023

@author Cristian TG

@requires Python3 + Virtual environment


[Whisper](https://github.com/openai/whisper/) is a multilingual automatic speech recognition (ASR) system trained on 680,000 hours of multilingual and multitask supervised data collected from the web.
This repository contains the instructions to install and use Whisper on Ponyland with: 
[Whisper-timestamped](https://github.com/linto-ai/whisper-timestampe/d) (timestamps, VAD at sentence-level and confidence scores at word-level) or [WhisperX](https://github.com/m-bain/whisperX/) (timestamps, VAD at sentence&word-level, but without confidence scores yet).


# 1. Setup
Please, first check which folder on Ponyland has enough space (more than 20GB) and create a folder there. In my case, I use: */vol/tensusers5/ctejedor/*. Obviously, **you need to choose your own folder** :)

```
# Run the following commands once:
# Choose a Pony with GPUs: https://ponyland.science.ru.nl/doku.php?id=wiki:ponyland:about
ssh thunderlane
current=/vol/tensusers5/ctejedor/whisper
mkdir $current && cd $current
df -h . # Check free space > 50GB. Otherwise, change the path to other location
python3 -m venv venv
source venv/bin/activate

pip3 install --upgrade pip
pip3 install triton
pip3 install tiktoken -v
pip3 install git+https://github.com/openai/whisper.git
# check whether ffmpeg is installed or not and install it if necessary
pip3 install git+https://github.com/linto-ai/whisper-timestamped
pip3 install matplotlib
pip install onnxruntime
pip install git+https://github.com/m-bain/whisperx.git
cd $current
git clone https://github.com/cristiantg/whisper-utils.git .
```

# 2. Update
```
cd /vol/tensusers5/ctejedor/whisper && source venv/bin/activate && clear && pwd
pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git
pip install --upgrade --no-deps --force-reinstall git+https://github.com/linto-ai/whisper-timestamped
pip install git+https://github.com/m-bain/whisperx.git --upgrade
```


# 3. Execution

```
# You will decode all files in a specific input_folder. The results will be obtained on an output_folder.
# Let op: The models are downloaded and saved in cache_model_folder (from 1GB to 20GB)!
# With nohup  ... & you can run the command in the background

ssh mistmane
nvidia-smi # Optional, to check if at least one GPU is free, if not, change to another Pony
cd /vol/tensusers5/ctejedor/whisper && source venv/bin/activate && clear && pwd

# Example for WhisperX
nohup time python3 decode_whisperX_folder.py audio/en tiny en output/en /vol/tensusers5/ctejedor/whisper/models 0 &

# Example for Whisper-timestamped
nohup time python3 decode_whispertimestamped_folder.py ./kaldi_jasmin/Beeldverhaal/utterances large-v2 nl output/beeldverhaal /vol/tensusers5/ctejedor/whisper/models 0 &
```

- *input_folder*: folder with audio files.
- *whisper_model*: tiny, small, medium, large… (choose one).
- *lang_code*: 0 for auto detection. You can also explicitally set the code: en, nl, etc. (see Whisper models).
- *output_folder*: folder for the Whisper output (.txt and .json files will be generated here).
- *cache_model_folder*: folder in which the Whisper models will be downloaded and stored.
- *prompts_folder*: folder with the prompts of the audio files. By default, .prompt files with the same filename as in the audio_folder. Write 0 if you do not want to set this value.


```
# Examples Python

python3 decode_whispertimestamped_folder.py audio/en tiny 0 output/en models 0

python3 decode_whispertimestamped_folder.py audio/en tiny en output/en models 0

python3 decode_whispertimestamped_folder.py audio/en tiny en output/en models prompts/en

# Run in background:
nohup time python3 decode_whispertimestamped_folder.py audio/en tiny en output/en models 0 &
```
```
# Examples command line
whisper "audio/snf025_nikolateslawirelessvision_anonymous_gu.mp3" --model tiny --model_dir /vol/tensusers5/ctejedor/whisper/models/ --output_dir output --language English

whisper audio/p1/second.wav --model large --model_dir /vol/tensusers5/ctejedor/whisper/models/ --output_dir output/p1/ --language nl
```


# 4. Extra

```
# List of Ponies with free GPUs
source /vol/tensusers/mbentum/AUDIOSERVER/audioserver_env/bin/activate;
python /vol/tensusers/mbentum/AUDIOSERVER/repo/controller.py -show_available
```


# 5. Models & languages

```
# Q&A - Where can I see the list of models?
# https://huggingface.co/openai

tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large-v1,large-v2,large

language-
{af,am,ar,as,az,ba,be,bg,bn,bo,br,bs,ca,cs,cy,da,de,el,en,es,et,eu,fa,fi,fo,fr,gl,gu,ha,haw,he,hi,hr,ht,hu,hy,id,is,it,ja,jw,ka,kk,km,kn,ko,la,lb,ln,lo,lt,lv,mg,mi,mk,ml,mn,mr,ms,mt,my,ne,nl,nn,no,oc,pa,pl,ps,pt,ro,ru,sa,sd,si,sk,sl,sn,so,sq,sr,su,sv,sw,ta,te,tg,th,tk,tl,tr,tt,uk,ur,uz,vi,yi,yo,zh,Afrikaans,Albanian,Amharic,Arabic,Armenian,Assamese,Azerbaijani,Bashkir,Basque,Belarusian,Bengali,Bosnian,Breton,Bulgarian,Burmese,Castilian,Catalan,Chinese,Croatian,Czech,Danish,Dutch,English,Estonian,Faroese,Finnish,Flemish,French,Galician,Georgian,German,Greek,Gujarati,Haitian,Haitian Creole,Hausa,Hawaiian,Hebrew,Hindi,Hungarian,Icelandic,Indonesian,Italian,Japanese,Javanese,Kannada,Kazakh,Khmer,Korean,Lao,Latin,Latvian,Letzeburgesch,Lingala,Lithuanian,Luxembourgish,Macedonian,Malagasy,Malay,Malayalam,Maltese,Maori,Marathi,Moldavian,Moldovan,Mongolian,Myanmar,Nepali,Norwegian,Nynorsk,Occitan,Panjabi,Pashto,Persian,Polish,Portuguese,Punjabi,Pushto,Romanian,Russian,Sanskrit,Serbian,Shona,Sindhi,Sinhala,Sinhalese,Slovak,Slovenian,Somali,Spanish,Sundanese,Swahili,Swedish,Tagalog,Tajik,Tamil,Tatar,Telugu,Thai,Tibetan,Turkish,Turkmen,Ukrainian,Urdu,Uzbek,Valencian,Vietnamese,Welsh,Yiddish,Yoruba}]
```
