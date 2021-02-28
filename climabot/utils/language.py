import os, gettext, locale, sys, pathlib

class Language:

    def __init__(self):
        self.__localeDir = str(pathlib.Path.cwd()) + '/' + sys.argv[0] + '/climabot/locales'
        self.__lang = ''
        self.__listeners = []

    def install(self):
        gettext.install('climabot', localedir=self.__localeDir)
        self.setLanguage(self.__getSystemLanguage())

    def __getSupportedLanguages(self):
        dirs = [ x.lower() for x in os.listdir(self.__localeDir) if os.path.isdir(os.path.join(self.__localeDir, x)) ]
        return dirs

    def __notifyListeners(self, lang):
        for listener in self.__listeners:
            listener.setLanguage(lang)

    def __getSystemLanguage(self):
        return os.getenv('LANG')[:5]

    def setLanguage(self, lang):
        languages = [ x.lower() for x in self.__getSupportedLanguages() ]
        if lang.lower() in languages:
            self.__lang = lang[:2] + '_' + lang[-2:].upper()
            t = gettext.translation('climabot', localedir=self.__localeDir, languages=[self.__lang])
            t.install()
            locale.setlocale(locale.LC_ALL, (self.__lang, locale.getpreferredencoding()))
            self.__notifyListeners(self.__lang)
            return True
        return False

    def getLanguage(self):
        if len(self.__lang) == 0:
            return self.__getSystemLanguage().lower()
        return self.__lang.lower()

    def isSupportedLanguage(self, lang):
        return lang.lower() in self.__getSupportedLanguages()

    def addListener(self, listener):
        self.__listeners.append(listener)

botlanguage = Language()
