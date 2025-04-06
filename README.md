# Snippets and code example for a websocket client/server using PicoVoice services locally

- ### Uses PicoVoice services in Python to maintain data locally:
  - Orca and PvSpeaker to synthesize voice from speech. English, French, Spanish and German models (Korean and Japanese not implemented as speech recognition is not available yet) available at this time, male or female voice
  - Cheetah to recognize speech to text in English, French, Spanish, German, Italian and Portuguese (Korean and Japanese not implemented yet)
- ### Uses Ollama as the translator agent

- ### Implementation to come
  - PicoLLM (work in progress) to infer using small open weight models
  - Real time streaming

- ### CLI parameters selection:
  - Model for ollama, from the list of models installed locally
  - Model gender for speech (male, female)
  - Model for Cheetah speech recognition (en, fr, pt, sp, ge, it)
  - Device to listen from a list of devices available on your computer
  - Device to speak from a list of devices available on your computer


- ### Some explanations about the files of the repo
  - Basic server: as explicitly said in the name, that's the server
  - Basic client: simple test of ws connection. Used as a prototype to check written messages exchange.
  - Translate Agent: used to detect language of the message received by the client, translates it into the language selected by the user. 
  - secure ws client/server: implements ssl for wss connection
  - wss and jwt client/server: implements ssl + jwt auth based for more secure connection
  - Orca client: this client uses speech to text (Cheetah) to recognize what is said by the user and once done, sends the message. On the other hand, when the client receives a message, it is spoken by Orca module in the language/gender configured by the user.
  - Orca secure client: ssl and jwt auth for same features from Orca client
