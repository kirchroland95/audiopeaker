import librosa
import json

def load_audio(file_path):
    """Load audio file and return as waveform and sample rate"""
    return librosa.load(file_path, sr=None)

def compute_loudness(y):
    """Compute loudness of the audio signal"""
    return librosa.feature.rms(y=y)

def detect_shouting(loudness, threshold=0.1):
    """Detect segments where the loudness exceeds a threshold"""
    return [idx for idx, value in enumerate(loudness[0]) if value > threshold]

def segment_to_time(segments, sr, frame_length=512):
    """Convert segment indices to timestamps in seconds"""
    return librosa.frames_to_time(segments, sr=sr, hop_length=frame_length)

def format_timestamps_to_mm_ss(timestamps):
    """Convert timestamps to MM:SS format"""
    return [f"{int(time // 60)}:{int(time % 60):02d}" for time in timestamps]

def time_to_seconds(timestamp):
    """Convert a timestamp in MM:SS format to total seconds"""
    minutes, seconds = map(int, timestamp.split(":"))
    return minutes * 60 + seconds

def add_range_if_valid(start, end, min_duration, merged_ranges):
    """Add a range to the merged ranges if it meets the minimum duration"""
    if time_to_seconds(end) - time_to_seconds(start) >= min_duration:
        merged_ranges.append(f"{start}-{end}")

def merge_consecutive_timestamps(timestamps, gap_threshold=5, min_duration=3):
    """Merge consecutive timestamps that are less than 'gap_threshold' seconds apart into a single range, excluding ranges shorter than 'min_duration' seconds"""
    merged_ranges = []
    start_time = None
    end_time = None

    for i, timestamp in enumerate(timestamps):
        if i == 0:
            start_time = timestamp
            end_time = timestamp
        else:
            if time_to_seconds(timestamp) - time_to_seconds(timestamps[i - 1]) <= gap_threshold:
                end_time = timestamp
            else:
                add_range_if_valid(start_time, end_time, min_duration, merged_ranges)
                start_time = timestamp
                end_time = timestamp

    # Append the last range only if it's longer than min_duration seconds
    if start_time and end_time:
        add_range_if_valid(start_time, end_time, min_duration, merged_ranges)

    return merged_ranges

def analyze_audio(file_path, loudness_threshold=0.1, min_duration=3, gap_threshold=5):
    """Main function to analyze the audio and detect shouting segments based on loudness."""
    y, sr = load_audio(file_path)
    loudness = compute_loudness(y)
    shouting_segments = detect_shouting(loudness, threshold=loudness_threshold)
    shouting_times = segment_to_time(shouting_segments, sr)
    shouting_times_mm_ss = format_timestamps_to_mm_ss(shouting_times)
    shouting_times_mm_ss.sort(key=lambda t: int(t.split(":" )[0]) * 60 + int(t.split(":" )[1]))
    shouting_ranges = merge_consecutive_timestamps(shouting_times_mm_ss, gap_threshold=gap_threshold, min_duration=min_duration)

    # Format the output as JSON
    result = {
        "shouting_ranges": shouting_ranges
    }

    return result

def save_to_json(data, output_file='audio_peaks.json'):
    """Save the result to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
