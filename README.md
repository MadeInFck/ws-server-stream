# Snippets and code example for a websocket client/server using PicoVoice services locally

- ### Uses PicoVoice services in Python to maintain data locally:
  - Orca and PvSpeaker to synthesize voice from speech. Only English model available at this time, male or female voice
  - Cheetah to recognize speech to text. English, French, Spanish, Italian, Portuguese and German models provided by PicoVoice
- ### Uses Ollama as the translator agent

- ### Implementation to come
  - PicoLLM (work in progress) to infer using small open weight models

- ### CLI parameters selection:
  - Model for ollama, from the list of models installed locally
  - Model for Orca
  - Model for Cheetah
  - Device to listen from a list of devices available on your computer
  - Device to speak from a list of devices available on your computer
