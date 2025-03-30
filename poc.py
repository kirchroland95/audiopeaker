import librosa
import json

def load_audio(file_path):
    """Load audio file and return as waveform and sample rate."""
    y, sr = librosa.load(file_path, sr=None)
    return y, sr

def compute_loudness(y):
    """Compute loudness of the audio signal over time."""
    S = librosa.feature.rms(y=y)
    return S

def detect_shouting(loudness, threshold=0.1):
    """Detect segments where the loudness exceeds a threshold, indicating shouting."""
    shouting_segments = []
    for idx, value in enumerate(loudness[0]):
        if value > threshold:
            shouting_segments.append(idx)
    return shouting_segments

def segment_to_time(segments, sr, frame_length=512):
    """Convert segment indices to timestamps in seconds."""
    times = librosa.frames_to_time(segments, sr=sr, hop_length=frame_length)
    return times

def merge_consecutive_timestamps(timestamps, gap_threshold=5, min_duration=3):
    """Merge consecutive timestamps that are less than 'gap_threshold' seconds apart into a single range, excluding ranges shorter than 'min_duration' seconds."""
    merged_ranges = []
    start_time = None
    end_time = None

    for i, timestamp in enumerate(timestamps):
        if i == 0:
            start_time = timestamp
            end_time = timestamp
        else:
            prev_minutes, prev_seconds = map(int, timestamps[i-1].split(":"))
            curr_minutes, curr_seconds = map(int, timestamp.split(":"))

            prev_total_seconds = prev_minutes * 60 + prev_seconds
            curr_total_seconds = curr_minutes * 60 + curr_seconds

            # Check if the difference between consecutive timestamps is less than the gap threshold
            if curr_total_seconds - prev_total_seconds <= gap_threshold:
                end_time = timestamp  # Extend the current range
            else:
                # Only add the range if it's longer than min_duration seconds
                start_total_seconds = int(start_time.split(":" )[0]) * 60 + int(start_time.split(":" )[1])
                end_total_seconds = int(end_time.split(":" )[0]) * 60 + int(end_time.split(":" )[1])
                if end_total_seconds - start_total_seconds >= min_duration:
                    merged_ranges.append(f"{start_time}-{end_time}")
                start_time = timestamp
                end_time = timestamp

    # Append the last range only if it's longer than min_duration seconds
    if start_time and end_time:
        start_total_seconds = int(start_time.split(":" )[0]) * 60 + int(start_time.split(":" )[1])
        end_total_seconds = int(end_time.split(":" )[0]) * 60 + int(end_time.split(":" )[1])
        if end_total_seconds - start_total_seconds >= min_duration:
            merged_ranges.append(f"{start_time}-{end_time}")

    return merged_ranges

def analyze_audio(file_path, loudness_threshold=0.1, min_duration=0):
    """Main function to analyze the audio and detect shouting segments based on loudness."""
    y, sr = load_audio(file_path)
    loudness = compute_loudness(y)
    shouting_segments = detect_shouting(loudness, threshold=loudness_threshold)
    shouting_times = segment_to_time(shouting_segments, sr)
    shouting_times_minutes_seconds = [f"{int(time // 60)}:{int(time % 60):02d}" for time in shouting_times]
    shouting_times_minutes_seconds.sort(key=lambda t: int(t.split(":" )[0]) * 60 + int(t.split(":" )[1]))
    shouting_ranges = merge_consecutive_timestamps(shouting_times_minutes_seconds, gap_threshold=5, min_duration=min_duration)
    result = {
        "shouting_ranges": shouting_ranges
    }

    return result

def save_to_json(data, output_file='audio_analysis.json'):
    """Save the result to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

# Example usage
audio_file = 'audiofile.mp3'
#result = analyze_audio(audio_file, 0.25)
result = analyze_audio(audio_file, 0.25, min_duration=4)
save_to_json(result)

print("Shouting Ranges:", result['shouting_ranges'])
