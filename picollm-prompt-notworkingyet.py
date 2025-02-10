import picollm

# Init PicoLLM AccessKey/Model Path
access_key = 'l4dpMwLCGSZkaCBGnNqrW0bO/sE/8Qv/F9V9gHbvbHbdM7s2dPNsDg=='
model_path = '/Users/mickaelfonck/Documents/Programmation/pico-cookbook/recipes/llm-voice-assistant/llama-3-8b-540.pllm'

#List all devices (GPU/CPU) available
print("Devices:",picollm.available_devices())

# Load model
llm = picollm.create(access_key=access_key, model_path=model_path)

print("Version: ", llm.version)
print("Model: ", llm.model)

# # Exemple de texte à traiter
prompt = "Quel est le sens de la vie?"

# Obtenir une réponse du modèle
try:
    print("Début prompt")
    response = llm.generate(prompt="Bonjour")
    print("Réponse du modèle:", response)
except Exception as e:
    print(f"Une erreur s'est produite lors de la génération de la réponse: {e}")



