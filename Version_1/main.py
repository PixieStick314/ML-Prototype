import pyaudio
import wave
import torchaudio
import threading
import tkinter as tk
from queue import Queue
import torch

# Audio Configuration
FORMAT = pyaudio.paInt16  # 16-bit audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # 16kHz sample rate
CHUNK = 1024  # Buffer size
OUTPUT_FILENAME = "blive_audio.wav"

# Load Wav2Vec2 Pretrained Model
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H  # Base model for English ASR
model = bundle.get_model()

# Global Variables
recording = False
audio_queue = Queue()
transcription_text = ""
word_count = 0

def record_audio():
    """Continuously records audio and sends it to the queue for transcription."""
    global recording
    audio = pyaudio.PyAudio()

    # Open audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    print("Listening... Speak now!")

    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

        # Process every 5 seconds of audio
        if len(frames) >= (RATE / CHUNK) * 5:
            audio_queue.put(frames)
            frames = []  # Reset buffer

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

def process_audio():
    """Processes audio from the queue and transcribes it using Wav2Vec2."""
    global transcription_text, word_count

    while recording or not audio_queue.empty():
        if not audio_queue.empty():
            frames = audio_queue.get()

            # Save recorded audio chunk
            with wave.open(OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            # Load and process audio
            waveform, sample_rate = torchaudio.load(OUTPUT_FILENAME)

            # Ensure sample rate matches model requirement
            if sample_rate != bundle.sample_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=bundle.sample_rate)
                waveform = resampler(waveform)

            # Perform speech-to-text
            with torch.no_grad():
                emission, _ = model(waveform)

            # Decode output (This is shit, replace soon)
            tokens = torch.argmax(emission, dim=-1).squeeze().tolist()
            labels = bundle.get_labels()
            transcript = ' '.join([labels[token] for token in tokens if token != 0])

            if transcript.strip():
                transcription_text += " " + transcript
                word_count += len(transcript.split())

                # Reset output every 50 words
                if word_count >= 50:
                    transcription_text = transcript
                    word_count = len(transcript.split())

                # Update GUI
                update_text(transcription_text)

def update_text(text):
    """Updates the transcription text in the GUI."""
    text_output.config(state=tk.NORMAL)
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, text)
    text_output.config(state=tk.DISABLED)

def start_recording():
    """Starts the recording and transcription process."""
    global recording
    if not recording:
        recording = True
        threading.Thread(target=record_audio, daemon=True).start()
        threading.Thread(target=process_audio, daemon=True).start()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)

def stop_recording():
    """Stops the recording process."""
    global recording
    recording = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# GUI Setup
root = tk.Tk()
root.title("Real-Time Speech Recognition")

# Start/Stop Buttons
start_button = tk.Button(root, text="Start Recording", command=start_recording, width=20, height=2)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, width=20, height=2)
stop_button.pack(pady=10)
stop_button.config(state=tk.DISABLED)

# Transcription Output Box
text_output = tk.Text(root, height=5, width=50, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 14))
text_output.pack(pady=10)

# Run the GUI
root.mainloop()