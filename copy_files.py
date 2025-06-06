import os
import shutil
import argparse


def copy_srt_files(source_dir, dest_dir):
    """
    Recursively copies all .srt files from source_dir to dest_dir.
    Creates destination directory if it doesn't exist.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination directory: {dest_dir}")

    file_count = 0
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(".srt"):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_dir)
                dest_path = os.path.join(dest_dir, rel_path)

                # Create subdirectories in destination if needed
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                shutil.copy2(src_path, dest_path)
                print(f"Copied: {rel_path}")
                file_count += 1

    print(f"\nDone! Copied {file_count} SRT files to {dest_dir}")


def main():
    parser = argparse.ArgumentParser(description="Recursively copy SRT files from source to destination directory")
    parser.add_argument("source_dir", help="Source directory containing SRT files")
    parser.add_argument("dest_dir", help="Destination directory for SRT files")
    args = parser.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"Error: Source directory '{args.source_dir}' does not exist")
        return

    copy_srt_files(args.source_dir, args.dest_dir)


if __name__ == "__main__":
    main()
