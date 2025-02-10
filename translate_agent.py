from locale import normalize

import ollama
import unicodedata


def print_decorator(n):
    """ Print fill-in # pretty cli """
    print("=" * n)


class TranslateAgent:
    def __init__(self):
        self._detected_language = ""
        self._language_listen = ""
        self._model = ""
        self._model_speak = ""


    def __list_model(self):
        """List the models available locally."""
        try:
            models = ollama.list()
            return [model['model'] for model in models['models']]
        except Exception as e:
            print(f"Error while fetching local models: {e}")
            return []

    def choose_model(self):
        """Allow the user to choose a model from those available."""
        models = self.__list_model()
        if not models:
            print("No model locally available.")
            return

        print("Models locally available:")
        for idx, model in enumerate(models):
            print(f"{idx + 1}. {model}")

        choice = int(input("Select a model: ")) - 1
        if 0 <= choice < len(models):
            self._model = models[choice]
        else:
            print("Invalid selection. First model in list will be used by default.")
            self._model = models[0]


    def translate(self, prompt):
        """Translate the given prompt using the chosen model."""
       # self.detected_language = self.__detect_language(prompt)
        messageToTranslate = f"Translate following text to {self._language_listen} : {prompt}. Only strict translation of the prompt is required, don't add anything more."
        res = ollama.generate(prompt=messageToTranslate, model=self._model, stream=False)
        #print("Response : ", res)
        return self.normalize_text(res['response'])

    def normalize_text(self, text):
        # Normalize the text by decomposing accented characters
        normalized_text = unicodedata.normalize('NFD', text)
        # Filter out the accent marks
        final_text = ''.join(
            c for c in normalized_text
            if unicodedata.category(c) != 'Mn'
        )
        return final_text

    def __detect_language(self, text):
        """Detect the language of the given text."""
        res = ollama.generate(prompt=f"Detect language of the following text : {text}, return only the language, nothing more", model=self._model, stream=False)
        #print("Language détected : ", res['response'])
        self._detected_language = res['response']

    def select_language(self):
        """ Select language all received texts should be translated to"""
        languages = ["English", "French", "German", "Italian", "Portuguese", "Spanish"]
        print_decorator(50)
        for idx, model in enumerate(languages):
            print(f"{idx + 1}. {model}")

        choice = int(input("Select a language: ")) - 1
        print_decorator(50)
        if 0 <= choice < len(languages):
            self._language_listen = languages[choice]
        else:
            print("Invalid selection. First model in list will be used by default.")
            self._language_listen = languages[0]

    def select_model_speak(self):
        """ Select model to speak"""
        models = ["Male", "Female"]
        for idx, model in enumerate(models):
            print(f"{idx + 1}. {model}")

        choice = int(input("Select a model: ")) - 1
        print_decorator(50)
        if 0 <= choice < len(models):
            self._model_speak = models[choice]
        else:
            print("Invalid selection. First model in list will be used by default.")
            self._model_speak = models[0]

if __name__ == "__main__":
    agent = TranslateAgent()
    print(agent.translate("Bonjour, comment ça va?"))

#"Hal tatakalam al arabiyya?"