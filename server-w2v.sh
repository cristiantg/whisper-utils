#!/bin/bash

# Usage:
# nohup time ./server-w2v.sh /vol/tensusers4/ctejedor/shared/stcart/8dgames-s2/audio 3 &

# Codes for <lang_code>:
# English: 1 (Whisper)
# Spanish: 2 (Implemented)
# Dutch_XL: 3 (Implemented)
# Irish: 4 (Implemented)
# Flemish: 5 (Not implemented but works with 3 as well) # Dutch_light: 6 (Not implemented)

# Check if the folder path is provided as an argument
if [ $# -ne 2 ]; then
  echo "Usage: $0 <folder_path> <lang_code>"
  exit 1
fi

# Extract the folder path from the argument
folder_path="$1"
lang_code="$2"

# Check if the provided folder path is valid
if [ ! -d "$folder_path" ]; then
  echo "Error: $folder_path is not a valid folder path."
  exit 1
fi

# Use find command to locate all files in the folder and its subdirectories
# and store their paths in an array variable
files=()
while IFS= read -r -d $'\0' file; do
  files+=("$file")
done < <(find "$folder_path" -type f -print0)

# Iterate over the filenames using a for loop
for file in "${files[@]}"; do
  #echo "Changing extension of $file to .txt"
  echo $file
  # Change the file extension to .txt
  new_file="${file%.*}.txt"
  #echo "New file name: $new_file"
  #echo $new_file
  # Add your desired logic here for processing each file
  echo
  curl -v -X POST -F "file=@$file" https://signon-wav2vec2-dev.cls.ru.nl/$lang_code > $new_file
done
