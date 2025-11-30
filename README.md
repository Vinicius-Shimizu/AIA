# AIA
AIA is an Ollama-based assistant that aims to help with tasks like opening apps or creating files. It uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) to implement the STT feature.

<details>
<summary>Table of contents</summary>

- [Features](#features)
- [Setup](#setup)
- [Building the Custom Ollama Model](#building-the-custom-ollama-model)
- [Running the Server](#running-the-server)
- [Usage](#usage)

</details>

## Features

 - Support to speech-to-text for voice-commands
 - Chat interface for both commands and conversation

## Setup
First make sure you have [Ollama](https://ollama.com/) installed.
Then run:
```bash
cd backend
npm install
pip install -r requirements.txt
cd ..
cd frontend
npm install
```

You may want to create a python virtual environment.
AIA's default language is portuguese. If you want another language modify this part of `stt_engine.py`:

```Python
    segments, _ = self.model.transcribe(
        speech_audio,
        language=<insert language>,
        temperature=0,
        beam_size=10,
        best_of=5,
        vad_filter=False,
        initial_prompt=<insert "O nome do assistente é AIA." in target language>
    )
```
Remember to also
## Building the Custom Ollama Model
You can modify the `Modelfile` to include the model you chose (the default is gemma3) and your own model configuration.
    
    From <insert your model>

    SYSTEM """
    <insert your configurations>
    """

After that, just run:
```bash
ollama create aia -f Modelfile
```

## Running the server
To start the server run:
```bash
node backend/server.js
```
When you see `[STT Status] Ready`, then the server has succesfully started.

## Usage
You can use AIA both as a chatbot assistant and a voice-command assistant.

### Chatbot version 
Run:
```bash
cd frontend
npm run dev
```
Then go to `localhost:5173`

### Voice command assistant
With the server running, you must first say the wake-up word `AIA`. 
After `[AIA] I am listening` appears, you may say your voice command. 