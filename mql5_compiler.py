import sublime, sublime_plugin
import os
import subprocess
import re

PLATFORM = sublime.platform()
METALANG = 'mql564.exe'
EXTENSION = '.mq5'
WINE = 'wine'

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PLUGIN_FOLDER = '%s/' % os.path.basename(BASE_PATH)
METALANG_PATH = os.path.join  (sublime.packages_path(), PLUGIN_FOLDER , METALANG)

def which(file):

    manual_path = os.path.join("/usr/bin", file)
    if os.path.exists(manual_path):
        return manual_path

    manual_path = os.path.join("/usr/local/bin", file)
    if os.path.exists(manual_path):
        return manual_path

    for dir in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(dir, file)
        if os.path.exists(path):
            return path

    print "PATH = {0}".format(os.environ['PATH'])
    return None


class Mql5CompilerCommand(sublime_plugin.TextCommand):

    def init(self):
        view = self.view

        self.dirname   = os.path.realpath(os.path.dirname(view.file_name()))
        self.filename  = os.path.basename(view.file_name())
        self.extension = os.path.splitext(self.filename)[1]

        if PLATFORM != 'windows':
            self.wine_path = which(WINE)

    def isError(self):

        iserror = False

        if not os.path.exists(METALANG_PATH):
            print METALANG_PATH # Debug
            print "Mqlcompiler | error: metalang.exe not found"
            iserror = True

        if not self.view.file_name() :
            # check if console..
            print "Mqlcompiler | error: Buffer has to be saved first"
            iserror = True

        if self.extension != EXTENSION:
            print "Mqlcompiler | error: wrong file extension: ({0})". \
            format(self.extension)
            iserror = True

        if self.view.is_dirty():
            print "Mqlcompiler | error: Save File before compiling"
            iserror = True

        if PLATFORM != 'windows':
            if not self.wine_path :
                print "Mqlcompiler | error: wine is not installed"
                iserror = True

        return iserror

    def runMetalang(self):

        command = [METALANG_PATH]

        if self.compile == "False":
            command.append("/s")
        
        command.append(self.filename)

        startupinfo = None

        # hide pop-up window on windows
        if PLATFORM == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # executing exe files with wine on mac / linux
        if PLATFORM != 'windows':
            command.insert(0,self.wine_path)

        # execution:
        proc = subprocess.Popen(command, 
        cwd= self.dirname,
        stdout=subprocess.PIPE,
        shell=False,
        startupinfo=startupinfo)
        
        return proc.stdout.read()

    def newLogWindow(self, output):
        view = self.view

        new_view = view.window().new_file()
        new_view.set_scratch(True)
        new_edit = new_view.begin_edit()
        new_view.insert(new_edit, 0, output)
        new_view.end_edit(new_edit)
        sublime.status_message('Metalang')

        pass

    def run(self , edit , compile):
        
        # compile or just check syntax
        self.compile = compile

        self.init()
        if self.isError():
            return

        stdout = self.runMetalang()

        self.newLogWindow(stdout)