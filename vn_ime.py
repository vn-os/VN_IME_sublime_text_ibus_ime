import os
FILE_NAME = os.path.basename(__file__)
FILE_NAME_NOEXT = os.path.splitext(FILE_NAME)[0]
FILE_NAME_SLTCF = FILE_NAME_NOEXT + ".sublime-settings"

from .bogo.core import get_vni_definition, process_sequence
import sublime, sublime_plugin

STATUS = False
TELEX  = False

class SaveOnModifiedListener(sublime_plugin.EventListener):
  def on_modified_async(self, view):
    view.run_command("startime")

class ControlimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    global STATUS
    global TELEX
    #
    settings = sublime.load_settings(FILE_NAME_SLTCF)
    if settings.get("telex"):
      TELEX = True
    else:
      TELEX = False
    #
    if STATUS:
      STATUS = False
      self.view.set_status('VN IME'," VN IME: OFF")
    else:
      STATUS = True
      self.view.set_status('VN IME'," VN IME: ON")

class StartimeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if not STATUS: return False
    cur_pos = self.view.sel()[0]
    cur_region = self.view.word(cur_pos)
    cur_word = self.view.substr(cur_region)
    new_word = self.process(cur_word)
    if not new_word: return False
    self.view.end_edit(edit)
    self.view.run_command("bridge_replace_text", {"text": new_word})
    print(cur_word, "=>", new_word)
    return True

  def process(self, word):
    if TELEX:
      final_word = process_sequence(word)
    else:
      final_word = process_sequence(word, rules=get_vni_definition())
    if final_word != word:
      return final_word
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
