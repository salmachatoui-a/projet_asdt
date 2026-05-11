from lingua import Language, LanguageDetectorBuilder

class LangDetect:
    def __init__(self):
        self.detector = LanguageDetectorBuilder.from_all_languages().build()

    def is_eng(self, text:str) -> bool:
        result = self.detector.detect_language_of(text)
        res = (result == Language.ENGLISH)
        if res:
            return True
        else:
            return False