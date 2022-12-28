import os, sys

FILE_DIR  = os.path.split(__file__)[0]
FILE_NAME = os.path.basename(__file__)
FILE_NAME_NOEXT = os.path.splitext(FILE_NAME)[0]
FILE_NAME_SLTCF = FILE_NAME_NOEXT + ".sublime-settings"

sys.path.insert(1, os.path.join(FILE_DIR, R"3rdparty/bogo-python"))
from bogo.core import get_vni_definition, process_sequence
import sublime, sublime_plugin

HOVER  = False
STATUS = False
TELEX  = True

def plugin_loaded():
    global TELEX
    global HOVER

    settings = sublime.load_settings(FILE_NAME_SLTCF)
    TELEX = settings.get("telex", TELEX)
    HOVER = settings.get("hover", HOVER)

    msg_ready = FILE_NAME_NOEXT + " -> READY"
    sublime.status_message(msg_ready)
    print(msg_ready)

    return

class SaveOnModifiedListener(sublime_plugin.EventListener):
  def on_modified_async(self, view):
    view.run_command("startime")

class ControlimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global STATUS
    STATUS = not STATUS
    self.view.set_status('VN IME', " VN IME: " + "ON" if STATUS else "OFF")

class StartimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global STATUS
    if not STATUS: return False
    cur_pos = self.view.sel()[0]
    cur_region = self.view.word(cur_pos)
    cur_word = self.view.substr(cur_region)
    new_word = self.process(cur_word)
    if not new_word: return False
    self.view.end_edit(edit)
    self.view.run_command("bridge_replace_text", {"text": new_word})
    return True

  def process(self, word):
    global TELEX
    if TELEX:
      new_word = process_sequence(word)
    else:
      new_word = process_sequence(word, rules=get_vni_definition())
    if new_word != word:
      return new_word
    return False

class BridgeReplaceTextCommand(sublime_plugin.TextCommand):
  '''
  SLT did not use the Edit object in the run(...) method
  Thus, if we replace text inside this method is not working
  So on, we write a bridge class to do text replacement during typing to bypass this issue
  ValueError("Edit objects may not be used after the TextCommand's run method has returned")
  '''
  def run(self, edit, text):
    cur_pos = self.view.sel()[0]
    cur_region = self.view.word(cur_pos)
    self.view.replace(edit, cur_region, text)

class HoverTextEventListener(sublime_plugin.EventListener):
  def on_hover(self, view, point, hover_zone):
    global HOVER
    if not HOVER: return

    word = view.substr(view.word(point))
    if not word: return

    try:
      content = "this is a popup"
      view.show_popup(
        "<b>" + word + "</b><br>" + content,
        location=point,
        max_width=800,
        max_height=400,
      )
    except KeyError:
      pass
