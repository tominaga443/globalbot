from microsofttranslator import Translator
from mstranslator.language_code import MSLanguageCode


class MSTranslator():

    def __init__(self, client_id, client_secret, target_lang="ja"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.target_lang = target_lang
        self.translator = Translator(client_id, client_secret)

    def detect(self, text):
        src_lang = self.translator.detect_language(text)
        return MSLanguageCode.name(src_lang)

    def translate(self, text):
        translated_text = self.translator.translate(text, self.target_lang)
        return translated_text
