import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
import sounddevice as sd
import numpy as np
import queue
import threading
import json
import sys
import time
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps
import requests
import asyncio

class STTEngine:
    def __init__(self, event_queue, loop):
        self.SAMPLE_RATE = 16000
        self.N_CHANNELS = 1
        self.WAKE_WORD = "aia"

        self.audio_queue = queue.Queue()
        self.buffer = np.zeros((0, 1), dtype=np.float32)
        self.state = "WAIT_WAKEWORD"
        self.stop_event = threading.Event()
        self.event_queue = event_queue
        self.loop = loop

        self.model = WhisperModel("large-v3", device="cuda", compute_type="float16")

        self.vad_options = VadOptions(
            threshold=0.45,
            min_speech_duration_ms=200,
            min_silence_duration_ms=10,
            speech_pad_ms=300
        )

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy())

    def recorder(self):
        self.stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.N_CHANNELS,
            dtype="float32",
            callback=self.audio_callback,
            blocksize=int(self.SAMPLE_RATE * 0.2)
        )
        with self.stream: 
            while not self.stop_event.is_set():
                sd.sleep(100)

    def emitEvent(self, status, message):
        future = asyncio.run_coroutine_threadsafe(
            self.event_queue.put({
                "status": status,
                "message": message
            }),
            self.loop
        )

    def transcriber(self):
        silence_frames = 0
        silence_limit = int(0.8 * self.SAMPLE_RATE)

        command_silence_frames = 0
        command_silence_limit = 8 * self.SAMPLE_RATE

        while not self.stop_event.is_set():
            try:
                block = self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            self.buffer = np.concatenate([self.buffer, block], axis=0)

            audio_data = self.buffer[:, 0]
            speech_regions = get_speech_timestamps(audio_data, self.vad_options, self.SAMPLE_RATE)

            if not speech_regions:
                # No speech detected
                silence_frames += len(block)
                if self.state == "LISTEN_COMMAND":
                    command_silence_frames += len(block)
                    
                    if command_silence_frames >= command_silence_limit: # Speech timeout control
                        self.state = "WAIT_WAKEWORD"
                        command_silence_frames = 0

                if silence_frames >= silence_limit:
                    self.buffer = np.zeros((0, 1), dtype=np.float32)
                    silence_frames = 0
                continue

            silence_frames = 0
            command_silence_frames = 0
            last_segment = speech_regions[-1]

            if last_segment["end"] < len(audio_data) - int(0.6 * self.SAMPLE_RATE):
                start = speech_regions[0]["start"]
                end = last_segment["end"]
                speech_audio = audio_data[start:end]

                segments, _ = self.model.transcribe(
                    speech_audio,
                    language="pt",
                    temperature=0,
                    beam_size=10,
                    best_of=5,
                    vad_filter=False,
                    initial_prompt="O nome do assistente é AIA."
                )

                text = " ".join([s.text for s in segments]).strip()
                if self.state == "WAIT_WAKEWORD":
                    if text.lower().strip(".") == self.WAKE_WORD:
                        self.state = "LISTEN_COMMAND"
                        self.emitEvent(status="listening", message="Estou ouvindo")
                else:
                    self.emitEvent(status="transcripted", message=text)

                self.buffer = np.zeros((0, 1), dtype=np.float32)
            
    def start(self):
        self.stop_event.clear()

        self.recorder_thread = threading.Thread(target=self.recorder, daemon=True)
        self.transcriber_thread = threading.Thread(target=self.transcriber, daemon=True)

        self.recorder_thread.start()
        self.transcriber_thread.start()

    def stop(self):
        self.stop_event.set()
        if hasattr(self, "stream"):
            self.stream.close()
        self.recorder_thread.join()
        self.transcriber_thread.join()

if __name__ == "__main__":
    stt = STTEngine()
    stt.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stt.stop()