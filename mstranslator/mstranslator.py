from microsofttranslator import Translator
from mstranslator.language import Language


class MSTranslator():

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.translator = Translator(client_id, client_secret)

    def detect(self, text):
        code = self.translator.detect_language(text)
        lang = Language(code)
        return lang

    def translate(self, text, target_lang="ja"):
        translated_text = self.translator.translate(text, target_lang)
        return translated_text
