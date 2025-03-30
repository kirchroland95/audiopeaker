from audio_utils import (
    save_to_json,
    analyze_audio
)
import tkinter as tk
from tkinter import filedialog, messagebox

# Placeholder functions
def browse_file(entry):
    """Open a file dialog to select an audio file."""
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg"), ("All Files", "*.*")]
    )
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def start_analysis(file_path_entry, tolerance_entry, duration_entry, gap_entry, results_text):
    """Analyze the audio file using the provided inputs and display the results."""
    try:
        # Get the file path from the browse field
        file_path = file_path_entry.get()
        if not file_path:
            raise ValueError("No file selected. Please choose an audio file.")

        # Prepare arguments for analyze_audio
        kwargs = {"file_path": file_path}

        # Convert tolerance to a decimal (percentage to fraction)
        if tolerance_entry.get():
            tolerance_percentage = float(tolerance_entry.get())
            if not (0 <= tolerance_percentage <= 100):
                raise ValueError("Tolerance must be between 0 and 100.")
            kwargs["loudness_threshold"] = tolerance_percentage / 100  # Convert to fraction

        if duration_entry.get():
            kwargs["min_duration"] = int(duration_entry.get())
        if gap_entry.get():
            kwargs["gap_threshold"] = int(gap_entry.get())

        # Call the analyze_audio function with the prepared arguments
        result = analyze_audio(**kwargs)

        # Display the results in the results_text widget
        results_text.config(state=tk.NORMAL)
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, f"Shouting Ranges:\n{result['shouting_ranges']}")
        results_text.config(state=tk.DISABLED)

    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def save_results(results_text):
    """Save the results to a JSON file on the disk."""
    try:
        # Get the results from the results_text widget
        results = results_text.get(1.0, tk.END).strip()
        if not results:
            raise ValueError("No results to save. Please run the analysis first.")

        # Extract the shouting ranges from the results text
        if "Shouting Ranges:" in results:
            shouting_ranges = eval(results.split("Shouting Ranges:\n")[1].strip())
        else:
            raise ValueError("Invalid results format. Unable to extract shouting ranges.")

        # Open a file dialog to choose the save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return  # User canceled the save dialog

        # Save the results to the chosen file
        save_to_json({"shouting_ranges": shouting_ranges}, output_file=file_path)
        messagebox.showinfo("Success", f"Results saved successfully to {file_path}")

    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving: {e}")

# Helper function to add placeholder text to Entry widgets
def add_placeholder(entry, placeholder_text):
    """Add placeholder text to an Entry widget."""
    entry.insert(0, placeholder_text)
    entry.bind("<FocusIn>", lambda event: clear_placeholder(entry, placeholder_text))
    entry.bind("<FocusOut>", lambda event: restore_placeholder(entry, placeholder_text))

def clear_placeholder(entry, placeholder_text):
    """Clear placeholder text when the user focuses on the Entry widget."""
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.config(fg="black")  # Set text color to black

def restore_placeholder(entry, placeholder_text):
    """Restore placeholder text if the Entry widget is empty."""
    if not entry.get():
        entry.insert(0, placeholder_text)
        entry.config(fg="gray")  # Set placeholder text color to gray

def show_help():
    """Display a help message with information about the input fields."""
    help_text = (
        "About AudioPeaker:\n\n"
        "This program analyzes audio files to detect shouting segments based on loudness.\n\n"
        "Input Field Guide:\n\n"
        "1. Tolerance (%):\n"
        "   - Sets the loudness threshold as a percentage.\n"
        "   - Higher values ignore quieter parts.\n\n"
        "2. Duration (seconds):\n"
        "   - Specifies the minimum length of a shouting segment.\n"
        "   - Example With 3 seconds:\n"
        "       1:02-1:04 is ignored\n"
        "       1:07-1:18 is not ignored\n\n"
        "3. Gap (seconds):\n"
        "   - Specifies the maximum allowed silence between segments.\n"
        "   - Example:\n"
        "       With 2 seconds: 1:02-1:04, 1:07-1:18\n"
        "       With 5 seconds: 1:02-1:18\n\n"
        "4. START Button:\n"
        "   - Initiates the analysis of the selected audio file.\n"
        "   - Displays the shouting ranges in the results area.\n\n"
        "5. Save Results Button:\n"
        "   - Saves the analysis results to a JSON file.\n\n"

    )
    messagebox.showinfo("Help", help_text)

def run_gui():
    # Create the main window
    root = tk.Tk()
    root.title("AudioPeaker") 
    root.geometry("500x600")  # Window size

    # Add Help button in the top-right corner
    help_button = tk.Button(root, text="Help", command=show_help)
    help_button.pack(anchor="ne", padx=10, pady=10)

    # Program title
    title_label = tk.Label(root, text="Audio Analysis Program", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

    # Instruction label
    instruction_label = tk.Label(root, text="Choose an audio file to analyze:", font=("Arial", 12))
    instruction_label.pack(pady=5)

    # Browse button and file path entry
    file_frame = tk.Frame(root)
    file_frame.pack(pady=5)
    file_path_entry = tk.Entry(file_frame, width=40)
    file_path_entry.pack(side=tk.LEFT, padx=5)
    browse_button = tk.Button(file_frame, text="Browse", command=lambda: browse_file(file_path_entry))
    browse_button.pack(side=tk.LEFT)

    # Input fields for tolerance, duration, and gap
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    # Tolerance field
    tolerance_label = tk.Label(input_frame, text="Tolerance (%):")
    tolerance_label.grid(row=0, column=0, padx=5, pady=5)
    tolerance_entry = tk.Entry(input_frame, width=10, fg="gray")
    tolerance_entry.grid(row=0, column=1, padx=5, pady=5)
    add_placeholder(tolerance_entry, "10")

    # Duration field
    duration_label = tk.Label(input_frame, text="Duration (seconds):")
    duration_label.grid(row=1, column=0, padx=5, pady=5)
    duration_entry = tk.Entry(input_frame, width=10, fg="gray")
    duration_entry.grid(row=1, column=1, padx=5, pady=5)
    add_placeholder(duration_entry, "3")

    # Gap field
    gap_label = tk.Label(input_frame, text="Gap (seconds):")
    gap_label.grid(row=2, column=0, padx=5, pady=5)
    gap_entry = tk.Entry(input_frame, width=10, fg="gray")
    gap_entry.grid(row=2, column=1, padx=5, pady=5)
    add_placeholder(gap_entry, "5")

    # START button
    start_button = tk.Button(
    root,
    text="START",
    font=("Arial", 12, "bold"),
    command=lambda: start_analysis(file_path_entry, tolerance_entry, duration_entry, gap_entry, results_text)
)
    start_button.pack(pady=20)

    # Results display
    results_label = tk.Label(root, text="Results:", font=("Arial", 12))
    results_label.pack(pady=5)
    results_text = tk.Text(root, height=8, width=50, state=tk.DISABLED)
    results_text.pack(pady=5)

    # Save button
    save_button = tk.Button(root, text="Save Results", command=lambda: save_results(results_text))
    save_button.pack(pady=10)

    # Run the application
    root.mainloop()