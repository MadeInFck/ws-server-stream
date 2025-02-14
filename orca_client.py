#!/usr/bin/env python3
import asyncio
import websockets
import json
import threading
import pvorca
import pvspeaker
import pvcheetah
import pvrecorder
from translate_agent import TranslateAgent
from dotenv import load_dotenv
import os

language_model_mapping = {
    "English": "./models/cheetah_params.pv",
    "French": "./models/cheetah_params_fr.pv",
    "German": "./models/cheetah_params_de.pv",
    "Italian": "./models/cheetah_params_it.pv",
    "Portuguese": "./models/cheetah_params_pt.pv",
    "Spanish": "./models/cheetah_params_es.pv",
}

speak_model_mapping = {
    "Male": "./models/orca_params_male.pv",
    "Female": "./models/orca_params_female.pv"
}

# Get env variables
load_dotenv()
port = os.getenv("WS_PORT")
ip = os.getenv("WS_IP")
access_key = os.getenv("PV_ACCESS_KEY")

async def handle_messages(websocket, loop):
    """
    Continuously listens for messages received from the server and prints them immediately.
    """
    async for message in websocket:
        try:
            if recorder.is_recording:
                recorder.stop()
            speaker.start()
            data = json.loads(message)
        except json.JSONDecodeError:
            print("Received message is not a valid JSON.")
            continue

        if data.get("type") == "speech":
            #print(f"\nText received: {data.get('text')}")
            text = data.get("text")
            message_translated = agent.translate(text)
            print("Message translated:", message_translated, " depuis ", text)
            pcm, alignments = orca.synthesize(text=message_translated)
            # print("PCM:", pcm, "ALIGN:", alignments)
            #speaker.write(pcm)
            speaker.flush(pcm)
            # Reprint the prompt to ensure the user can continue inputting
            # print("Enter your message: ", end="", flush=True)
            recorder.start()
            speaker.stop()



async def send_status(websocket, status):
    """
    Sends a message of type "status" to indicate the client's status.
    """
    message = json.dumps({"type": "status", "status": status, "from": str(websocket.remote_address)})
    await websocket.send(message)


async def send_text(websocket, text):
    """
    Sends a message of type "speech" containing the typed text.
    """
    message = json.dumps({
        "type": "speech",
        "text": text,
        "from": str(websocket.remote_address)
    })
    await websocket.send(message)


async def send_inactive_delay(websocket):
    """
    Waits a short delay then sets the client's status to "inactive".
    """
    await asyncio.sleep(0.1)
    await send_status(websocket, "inactive")

def capture_audio_thread(websocket, loop):
    """
    Captures audio in real-time and transcribes it using pvcheetah.
    """
    try:
        recorder.start()
        print('Listening... (press Ctrl+C to stop)')

        try:
            transcript = ""
            while True:
                partial_transcript, is_endpoint = cheetah.process(recorder.read())
                #print(partial_transcript, end='', flush=True)
                transcript += partial_transcript
                if is_endpoint:
                    final_transcript = cheetah.flush()
                    #print(transcript + final_transcript)
                    asyncio.run_coroutine_threadsafe(send_status(websocket, "active"), loop)
                    asyncio.run_coroutine_threadsafe(send_text(websocket, transcript + final_transcript), loop)
                    asyncio.run_coroutine_threadsafe(send_inactive_delay(websocket), loop)
                    transcript = ""


        except Exception as error:
            print("Error while capturing audio : ", error)
    except KeyboardInterrupt:
        pass
    finally:
        print("Transcription stopped.")
        recorder.stop()

def input_thread(websocket, loop):
    """
    Function executed in a separate thread for user input.
    For each inputted message, the corresponding coroutines are scheduled in the loop.
    """
    while True:
        try:
            text = input("Enter your message: ").strip()
        except EOFError:
            break

        if text == "":
            continue  # Ignore empty inputs

        # Schedule sending messages in the asynchronous loop via run_coroutine_threadsafe
        asyncio.run_coroutine_threadsafe(send_status(websocket, "active"), loop)
        asyncio.run_coroutine_threadsafe(send_text(websocket, text), loop)
        asyncio.run_coroutine_threadsafe(send_inactive_delay(websocket), loop)


async def start_client():
    """
    Connects to the server and starts tasks for displaying received messages
    and handling user input via a thread.
    """
    websocket_url = f"ws://{ip}:{port}"  # Verify that the URL and port are correct
    async with websockets.connect(websocket_url) as websocket:
        print(f"WebSocket connection established at ws://{ip}:{port}.")
        # Get the current asynchronous loop
        loop = asyncio.get_running_loop()
        # Start the thread for user input
        thread = threading.Thread(target=capture_audio_thread, args=(websocket, loop), daemon=True)
        thread.start()
        # Remain in the message receiving loop
        await handle_messages(websocket, loop)

def print_decorator(n):
    """ Print fill-in # pretty cli """
    print("="*n)

def select_device_audio_capture():
    print_decorator(50)
    print("Available devices to capture audio : ")
    devices = pvrecorder.PvRecorder.get_available_devices()
    for idx, device in enumerate(devices):
        print(f"{idx + 1}. {device}")

    choice = int(input("Select a device to capture audio: ")) - 1
    print_decorator(50)
    if 0 <= choice < len(devices):
        return choice
    else:
        print("Invalid selection. First model in list will be used by default.")
        return 0

def select_device_audio_speak():
    print_decorator(50)
    print("Available devices to speak audio : ")
    devices = pvspeaker.PvSpeaker.get_available_devices()
    for idx, device in enumerate(devices):
        print(f"{idx + 1}. {device}")

    choice = int(input("Select a device to speak audio: ")) - 1
    print_decorator(50)
    if 0 <= choice < len(devices):
        return choice
    else:
        print("Invalid selection. First model in list will be used by default.")
        return 0


def run():
    """ Init of agent and Ollama"""
    # Select LLM model to run for translation
    agent = TranslateAgent()
    agent.choose_model()
    # Select language to play messages received
    print_decorator(50)
    agent.select_language()
    print_decorator(50)
    agent.select_model_speak()
    """ Init of PicoVoice services """

    # Initialize PV Recorder
    device_listen = select_device_audio_capture()
    recorder = pvrecorder.PvRecorder(frame_length=512, device_index=device_listen, buffered_frames_count=50)
    device_speak = select_device_audio_speak()
    print_decorator(50)
    print(f"→ PV Recorder v{recorder.version} started.")


    # Initialize PV Cheetah
    cheetah = pvcheetah.create(access_key=access_key, model_path=language_model_mapping[agent._language_listen], endpoint_duration_sec=2, enable_automatic_punctuation=True)
    print(f"→ PV Cheetah v{cheetah.version} started with language {agent._language_listen}.")

    # Initialize PV Orca
    orca = pvorca.create(access_key=access_key, model_path=speak_model_mapping[agent._model_speak])
    print(f"→ PV Orca v{orca.version} started with {agent._model_speak} voice.")

    # Initialize PV Speaker
    speaker = pvspeaker.PvSpeaker(
        sample_rate=22050,
        bits_per_sample=16,
        buffer_size_secs=20,
        device_index=device_speak)
    print(f"→ PV Speaker v{speaker.version} started.")

    print ("PV Speaker selected : ", speaker.selected_device)
    print("PV Recoder selected : ", recorder.selected_device)
    print_decorator(50)

    # Run client asynchronously
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print("Client stopped by user.")
    finally:
        try:
            speaker.stop()
            print("PV Speaker stopped.")
            speaker.delete()
            print("PV Speaker resources released.")
            orca.delete()
            print("PV Orca resources released.")
            cheetah.delete()
            print("PV Cheetah resources released.")
            recorder.stop()
            print("PV Recorder stopped.")
            recorder.delete()
            print("PV Recorder released.")
        except Exception as e:
            print(f"Error while shutting down : {e}")


if __name__ == "__main__":
    run()