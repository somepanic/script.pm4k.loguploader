"""Stand-ins for Kodi's modules and the add-on's dependencies, so lib/loguploader.py imports outside Kodi."""

import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


_ADDON_INFO = {
    'id': 'script.pm4k.loguploader',
    'name': 'PM4K Logfile Uploader',
    'version': '0',
    'path': '',
    'profile': '',
}


class _Addon:
    def getAddonInfo(self, key):
        return _ADDON_INFO[key]

    def getLocalizedString(self, string_id):
        return str(string_id)


def _module(name, **attributes):
    module = types.ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module


_module('xbmc', log=lambda *args, **kwargs: None, LOGINFO=1, getCondVisibility=lambda condition: False)
_module('xbmcgui', WindowXMLDialog=object, Dialog=object, DLG_YESNO_YES_BTN=11)
_module('xbmcaddon', Addon=_Addon)
_module('xbmcvfs', translatePath=lambda path: path, exists=lambda path: True)
_module('pyqrcode')
_module('requests')
