# Ogrodjepisnik
## A subtitler service for Ogrodje


### Introduction
This tool generates subtitles for mp3 files in a provided source folder.

It generates a subtitle in the source language (not necessarily Slovene) and its corresponding translation in English.

How it works:
1. the script takes the mp3 file, 
2. divides it into 1500s chunks (max allowed input for whisper), 
3. transcribes each chunk,
4. syncs the subtitles (adds X * chunk_length)
5. does the same for the original language (Slovene) and English 
6. persists to disk (_si.srt and _en.srt)

It also takes into account already existing subtitles, so if it fails you can just rerun it, and it will continue where it left off :)

### Current state
ALl of s2, s3, s4 episodes are completely transcribed, but there are some s1 episodes missing.

### Prerequisites
This tool assumes you have a .mp3 version of the episode you want to transcribe on your local disk.
You can download the episodes using various tools, e.g. [yt-dlp](https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation):

```shell

# Download s04 in mp3 format
yt-dlp -x --audio-format mp3 --embed-thumbnail -i "https://www.youtube.com/playlist?list=PLv1TY0ByPjuSFFbIdMWd0Ln-aZY3Mr4yH" 

# Download s04 in worst video format
yt-dlp -f worst "https://www.youtube.com/playlist?list=PLv1TY0ByPjuSFFbIdMWd0Ln-aZY3Mr4yH"

```

### Setup & Run

```shell
# Create a new Python environment using UV
uv sync

source .venv/bin/activate

python transcriber.py <your input folder>

# since your videos are probably together with your subtitles, you can easily extract them using:
python copy_files.py <your input folder> ./srts

# Note that the ./srts keeps the same structure as your input folder

```
### Contribution 
If you want to improve the script please open a PR and let's make it happen.

If you find a bug please open a new issue and I will try to address it ASAP, but it will be faster if you open a PR :)

I encourage you to open PRs to improve the current state of the subtitles :)

### Author(s)

[Marko Prelevikj](https://www.linkedin.com/in/mprelevic/)
