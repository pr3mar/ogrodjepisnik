import os
import subprocess
import openai
import re
import argparse

from dotenv import load_dotenv

load_dotenv()

# Settings
CHUNK_LENGTH = 1500  # seconds
OPENAI_MODEL = "whisper-1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def split_audio(input_file, chunk_length):
    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", input_file],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration = float(result.stdout)
    chunk_files = []
    i = 0
    for start in range(0, int(duration), chunk_length):
        out_file = f"{os.path.splitext(input_file)[0]}_chunk_{i:03d}.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file, "-ss", str(start),
            "-t", str(chunk_length), "-c", "copy", out_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        chunk_files.append((out_file, start))
        i += 1
    return chunk_files


def transcribe_to_srt(audio_path, model=OPENAI_MODEL):
    with open(audio_path, "rb") as audio_file:
        result = openai.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="srt"
        )
    return result


def translate_to_srt(audio_path, model=OPENAI_MODEL):
    with open(audio_path, "rb") as audio_file:
        result = openai.audio.translations.create(
            model=model,
            file=audio_file,
            response_format="srt"
        )
    return result


def offset_srt(srt_text, offset):
    def time_add(s, offset):
        h, m, rest = s.split(":")
        s, ms = rest.split(",")
        total = int(h)*3600 + int(m)*60 + int(s) + offset
        ms = int(ms)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    new_lines = []
    for line in srt_text.splitlines():
        match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", line)
        if match:
            start, end = match.groups()
            start_off = time_add(start, offset)
            end_off = time_add(end, offset)
            new_lines.append(f"{start_off} --> {end_off}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def merge_srts(srt_chunks):
    merged = []
    idx = 1
    for srt in srt_chunks:
        entries = re.split(r"\n\s*\n", srt.strip())
        for entry in entries:
            lines = entry.strip().splitlines()
            if len(lines) >= 2:
                lines[0] = str(idx)
                merged.append("\n".join(lines))
                idx += 1
    return "\n\n".join(merged)


def process_mp3_file(mp3_path, api_key, suffix):
    openai.api_key = api_key
    base = os.path.splitext(mp3_path)[0]
    srt_original = base + "_si.srt"
    srt_english = base + "_en.srt"

    print(f"\n{suffix} Processing: {mp3_path}")

    # 1. Split audio
    chunks = split_audio(mp3_path, CHUNK_LENGTH)
    srt_chunks_original = []
    srt_chunks_english = []
    for chunk_file, start in chunks:
        print(f"  Transcribing {os.path.basename(chunk_file)} (original)...")
        srt_orig = transcribe_to_srt(chunk_file)
        print(f"  Translating {os.path.basename(chunk_file)} (English)...")
        srt_eng = translate_to_srt(chunk_file)
        srt_chunks_original.append(offset_srt(srt_orig, start))
        srt_chunks_english.append(offset_srt(srt_eng, start))
        os.remove(chunk_file)
    # 2. Merge and write SRTs
    merged_original = merge_srts(srt_chunks_original)
    merged_english = merge_srts(srt_chunks_english)
    with open(srt_original, "w", encoding="utf-8") as f:
        f.write(merged_original)
    with open(srt_english, "w", encoding="utf-8") as f:
        f.write(merged_english)
    print(f"  Done! SRTs: {os.path.basename(srt_original)}, {os.path.basename(srt_english)}")


def main():

    parser = argparse.ArgumentParser(description="Process MP3 files and generate SRT subtitles using OpenAI Whisper.")
    parser.add_argument("data_path", help="Directory containing MP3 files to process")
    args = parser.parse_args()

    api_key = OPENAI_API_KEY
    if not api_key:
        print("OPENAI_API_KEY not found in environment. Please set it in your .env file.")
        return

    data_path = args.data_path
    if not os.path.isdir(data_path):
        print(f"Provided data_path '{data_path}' is not a valid directory.")
        return

    mp3_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.lower().endswith(".mp3")]
    if not mp3_files:
        print("No MP3 files found in the directory.")
        return
    for i, mp3_path in enumerate(mp3_files):
        base = os.path.splitext(mp3_path)[0]
        srt_original = base + "_si.srt"
        srt_english = base + "_en.srt"
        if os.path.exists(srt_original) and os.path.exists(srt_english):
            print(f"Skipping {mp3_path} (SRTs already exist)")
            continue
        process_mp3_file(mp3_path, api_key, f"{i + 1}/{len(mp3_files)}")


if __name__ == "__main__":
    main()
