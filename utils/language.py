import os
import gettext
import locale

class Language:

    def __init__(self):
        self.__localeDir = 'locales'
        self.__lang = ''
        self.__listeners = []

    def install(self):
        gettext.install('climabot', localedir='locales')

    def __getSupportedLanguages(self):
        dirs = [ x.lower() for x in os.listdir(self.__localeDir) if os.path.isdir(os.path.join(self.__localeDir, x)) ]
        return dirs

    def __notifyListeners(self, lang):
        for listener in self.__listeners:
            listener.setLanguage(lang)

    def setLanguage(self, lang):
        languages = [ x.lower() for x in self.__getSupportedLanguages() ]
        if lang.lower() in languages:
            lang = lang[:2] + '_' + lang[-2:].upper()
            t = gettext.translation('climabot', localedir=self.__localeDir, languages=[lang])
            t.install()
            locale.setlocale(locale.LC_ALL, (lang, locale.getpreferredencoding()))
            self.__notifyListeners(lang)
            return True
        return False

    def getLanguage(self):
        if len(self.__lang) == 0:
            return os.getenv('LANG')[:4].lower()
        return self.__lang.lower()

    def isSupportedLanguage(self, lang):
        return lang.lower() in self.__getSupportedLanguages()

    def addListener(self, listener):
        self.__listeners.append(listener)

    def removeListener(self, listener):
        self.__listeners.remove(listener)

botlanguage = Language()
