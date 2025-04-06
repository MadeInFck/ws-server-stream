import picollm

# Init PicoLLM AccessKey/Model Path
access_key = 'l4dpMwLCGSZkaCBGnNqrW0bO/sE/8Qv/F9V9gHbvbHbdM7s2dPNsDg=='
model_path = '/Users/mickaelfonck/Documents/Programmation/pico-cookbook/recipes/llm-voice-assistant/llama-3-8b-540.pllm'

# List all devices (GPU/CPU) available
print("Devices:",picollm.available_devices())

# Load model
llm = picollm.create(access_key=access_key, model_path=model_path)

print("Version: ", llm.version)
print("Model: ", llm.model)

# Example text to process
prompt = "Quel est le sens de la vie?"

# Get a response from the model
try:
    print("Début prompt")
    response = llm.generate(prompt="Bonjour")
    print("Réponse du modèle:", response)
except Exception as e:
    print("An error occurred while generating the response:", e)



