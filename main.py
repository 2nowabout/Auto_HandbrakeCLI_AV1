import os
import subprocess
import threading


FFPROBE_PATH = r"D:\Programs\ffmpeg\bin\ffprobe.exe"  # Update this path accordingly
HANDBRAKE_PATH = "D:\Programs\HandBrake\HandBrakeCLI.exe"  # Update with the full path if HandBrakeCLI



# Create a lock for reencoding
encode_lock = threading.Lock()

# Function to get video width using ffprobe
def get_video_width(file_path):
    result = subprocess.run([FFPROBE_PATH, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width', '-of', 'csv=s=x:p=0', file_path], stdout=subprocess.PIPE, text=True)
    try:
        width = int(result.stdout.strip())
        return width
    except ValueError:
        return None
def is_empty_folder(folder_path):
    return not any(os.listdir(folder_path))

def delete_empty_folders(root_folder):
    for foldername, subfolders, filenames in os.walk(root_folder, topdown=False):
        folder_path = os.path.join(root_folder, foldername)
        if is_empty_folder(folder_path):
            print(f"Deleting empty folder: {folder_path}")
            os.rmdir(folder_path)

def reencode_to_av1(input_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')) and "av1" not in file.lower():
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}_av1.mp4")

                command = [
                    HANDBRAKE_PATH,
                    "--input", input_file_path,
                    "--output", output_file_path,
                    "--align-av",
                    "--encoder", "nvenc_av1_10bit",  # Use AV1 encoder
                    "--encoder-level", "slowest",
                    "--vfr",
                    "--aencoder", "copy"
                ]

                # Check if video width is lower than 720p
                video_width = get_video_width(input_file_path)
                if video_width is not None and video_width < 1280:  # Assuming 720p as the threshold
                    command.extend(["--quality", "21.0"])
                else:
                    command.extend(["--quality", "24.0"])

                with encode_lock:
                    subprocess.run(command)

                # Delete old file after successful reencoding
                os.remove(input_file_path)
                print(f"Old file deleted: {input_file_path}")
def main():
    folder_to_check = input("Enter the path of the folder to check: ")
    input_folder = folder_to_check

    if os.path.exists(folder_to_check):
        with encode_lock:
            delete_empty_folders(folder_to_check)
            print("Empty folders deleted successfully.")

        if os.path.exists(input_folder):
            reencode_to_av1(input_folder)
            print("Reencoding to AV1 completed successfully.")
        else:
            print("The specified video folder does not exist.")
    else:
        print("The specified folder to check does not exist.")

if __name__ == "__main__":
    main()