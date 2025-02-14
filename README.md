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



- ### How does that work?
  - Basic server: as explicitly said in the name, that's the server
  - Basic client: simple test of ws connection. Used as a prototype to check written messages exchange.
  - Orca client: this client uses speech to text to recognize what is said by the user and once done, sends the message. On the other hand, when the client receives a message, it is spoken by Cheetah module in the language configured by the user.
  - Translate Agent: used to detect language of the message received by the client, translates it into the language selected by the user. 
