# Version 1
This application records audio from your microphone in real-time, transcribes it using PyAudio and Torchaudio (Wav2Vec2), and displays the transcribed text in a simple Tkinter GUI. This document outlines known issues and limitations in ML-Prototype version 1
## Known Issues & Limitations

1. Path Handling:
The OUTPUT_FILENAME is set to live_audio.wav. This can get wonky on non-Windows machines or if the Version_1 folder doesn’t exist. Also, the backslash might get read as an escape character.
### Workaround
Will be amended when saving to disk is no longer necessary.

2. Chunk-based "Real-time" rendering:
* We only process audio in 5-second slices ((RATE / CHUNK) * 5 = 5 seconds). The transcription shows up after each slice, so there’s a noticeable delay before any text appears.
### Improvement Opportunity: 
Use a smaller chunk size or a continuous streaming approach for more responsive real-time feedback.

3. Repeated overwriting of audio file:
* Every 5-second slice overwrites live_audio.wav, so you only ever have the most recent chunk saved.

4. No Error Handling:
* We pretty much assume everything works perfectly. If your mic isn’t recognized or PyAudio flips out, the app might crash or just freeze.
### Future
Will Add Whole Section For It

6. Word Count Reset:
Once we hit 50 words total, we clear everything and start fresh. Prototype quirk.

7. Optimization:
* There is none.
### Future
Maybe "stats for nerds" output?

8. No Noise Handling:
* The code doesn't try to remove background noise, so transcriptions might be junk in a noisy room.

9. Lacking Debugging info:
* Along with error handling, this will be a separate unit.

10. Decoder currently sucks:
* Output is mostly garbage phonemes atm.