#!/usr/bin/env python3

#Copyright Ηλιάδης Ηλίας, 2018
#
# contact http://gnu.kekbay.gr/gladerad/  -- mailto:iliadis@kekbay.gr
#
# This file is part of sampleapp.
#
# This is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3.0 of the License, or (at your option) any
# later version.
#
# It is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with the source code.  If not, see <http://www.gnu.org/licenses/>.

"""
    Simple Gui to create Skeleton app from a glade file.
    ...
    29/03/2018
"""

NAME = 'GladerRAD'
NAMEASONE = NAME.replace(' ', '_')
CONFIGDOMAIN = 'MainWindow'
#FIXME: correct the version
__version__ = '0.0.14'
VERSIONSTR = '{} v. {}'.format(NAME, __version__)

#RETURN ERROR CODES
ERROR_IMPORT_GTK_FAIL = -1
ERROR_IMPORT_LIBRARIES_FAIL = -2
ERROR_INVALID_GLADE_FILE = -3
ERROR_GLADE_FILE_READ = -4

def import_Gtk_failed(err):
    """ Fail with a friendlier message when imports fail. """
    msglines = (
        '{namever} requires some third-party libraries.',
        'Please install requirements using \'pip\' or your package manager.',
        'The import error was:',
        '    {err}\n'
    )
    print('\n'.join(msglines).format(namever=VERSIONSTR, err=err))
    sys.exit(ERROR_IMPORT_GTK_FAIL)

try:
    from gi import require_version as gi_require_version
    gi_require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError as eximp:
    import_Gtk_failed(eximp)

#If Gtk is imported then we can show a Gtk.MessageDialog
# for other imports.
def import_fail(err):
    """ Fail with a Gtk.MessageDialog message when imports fail. """
    msglines = (
        '{namever} requires some third-party libraries.',
        'Please install requirements using \'pip\' or your package manager.',
        'The import error was:',
        '    {err}\n'
    )
    themessage = '\n'.join(msglines).format(namever=VERSIONSTR, err=err)
    print(themessage)
    dialog = Gtk.MessageDialog(
        None,
        0,
        Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK,
        NAME)
    dialog.format_secondary_text(themessage)
    dialog.run()
    dialog.destroy()
    sys.exit(ERROR_IMPORT_LIBRARIES_FAIL)

try:
    import os
    import sys
    import stat
    from datetime import datetime
    from keyword import iskeyword
    from gi.repository import Gdk, GdkPixbuf, GLib, GObject, Pango
    gi_require_version('GtkSource', '3.0')
    from gi.repository import GtkSource
    from bs4 import BeautifulSoup as BS
    #Remove next line and all references to it,
    #if you do not want a config file
    from configparser import ConfigParser
    #Remove next lines and all references to locale,
    #if you do not want localization
    import locale
    from locale import gettext as _
except ImportError as eximp:
    import_fail(eximp)

#Remove if do not want config file (remove also all references to it).
class LocalConfig():
    """A very simplified configuration editor for multi usage.

    Read and write only one section from a conf file in user's home directory.
    Can be called from multiple "places"
    using the same filename, but different section names.

    """
    def __init__(self):
        """Init the python's configparser.

        Read existing keys for "my" section only, if any.
        Modify only "my" section.
        Readings are done using python's configparser idioms.
        Methods:
        - get
        - set
        - get_bool
        - save

        """
        self.ok = False
        self.parser = None
        self.configfile = os.path.join(os.path.expanduser('~'), '.config', NAMEASONE + '.conf')
        self.parser = ConfigParser()
        self.parser.add_section(CONFIGDOMAIN)
        try:
            os.makedirs(os.path.dirname(self.configfile), exist_ok=True)
            dummyparsersections = self.get_all_sections()
            if dummyparsersections.has_section(CONFIGDOMAIN):
                for akey, avalue in dummyparsersections.items(CONFIGDOMAIN):
                    self.parser.set(CONFIGDOMAIN, akey, avalue)
            else:
                self.parser[CONFIGDOMAIN] = {}
            self.ok = True
        except Exception as ex:
            print("ex", ex, repr(ex))

    def get(self, thekey, thedefault):
        """Get a value for a key based on type of the provided default value.

        Return a default value if key does not exists.

        """
        if self.parser.has_option(CONFIGDOMAIN, thekey):
            if type(thedefault) == int:
                return self.parser.getint(CONFIGDOMAIN, thekey)
            elif type(thedefault) == bool:
                return self.parser.getboolean(CONFIGDOMAIN, thekey)
            else:
                return self.parser.get(CONFIGDOMAIN, thekey)
        else:
            return thedefault

    def get_bool(self, thekey, thedefault):
        """Set the value for a key.

        Always convert to str.

        """
        b = self.get(thekey, thedefault)
        if type(b) == bool:
            return b
        if type(b) == str:
            if b.isalpha:
                return (b == 'False')
            else:
                return ( 0 == int(b))

    def set(self, thekey, thevalue):
        """Set the value for a key.

        Always convert to str.

        """
        self.parser[CONFIGDOMAIN][thekey] = str(thevalue)

    def save(self):
        """Save "my" section to the disk.

        1. Read all sections.
        2. Replace "my" section.
        3. Write all to disk. May re-arragne sections.
        """
        try:
            dummyparser = self.get_all_sections()
            dummyparser.remove_section(CONFIGDOMAIN)
            dummyparser.add_section(CONFIGDOMAIN)
            for akey, avalue in self.parser.items(CONFIGDOMAIN):
                dummyparser.set(CONFIGDOMAIN, akey, avalue)
            with open(self.configfile, 'w') as f:
                dummyparser.write(f)
        except Exception as ex:
            print('write exception ', ex,'\nwhile writing settings file: ', self.configfile)

    def get_all_sections(self):
        """Return a ConfigParser object from existing file or an empty one. """
        try:
            if os.path.exists(self.configfile):
                dummyparser = ConfigParser()
                dummyparser.read(self.configfile)
                return dummyparser
            else:
                return ConfigParser()
        except Exception as ex:
            pass
        return ConfigParser()

#init the settings
settings = LocalConfig()

READFROMFILE = """#Load the ui from a file
        #glade file will be either in the start directory
        gladefile = os.path.join(self.BASE_DIR, '{gladefile}')
        if not os.path.exists(gladefile):
            #or in a subdirectory named glades
            gladefile = os.path.join(self.BASE_DIR, 'glades', '{gladefile}')
        try:
            with open(gladefile, "r") as f:
                self.gladestring = f.read()
        except Exception as ex:
            print(str(ex))
            print('\\nError loading Glade file!\\n{gladefile}'.format(ex))
            sys.exit(ERROR_GLADE_FILE_READ)\n"""

READFROMSTRING = """#Load the ui from given string
        self.gladestring = THEGLADESTR\n"""

#class GladerRADApp(Gtk.Window):
class GladerRADApp(Gtk.Window):
    """ Main window with all components. """

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        Gtk.Window.__init__(self)
        debugging = os.path.exists(os.path.join(self.BASE_DIR, 'debug'))
        self.we_can_exit_now = False
        self.return_parameter = None

        self.set_glade_from_file = False
        #...
        GObject.type_register(GtkSource.View)

        #do some initilizations
        #and get the glade filename
        self.starting_initialisations()
        self.builder = Gtk.Builder()
        try:
            self.builder.add_from_string(self.gladestring)
        except Exception as ex:
            print('\nError building main window!\nwindowMain'.format(ex))
            sys.exit(ERROR_INVALID_GLADE_FILE)

        # Get gui objects
        self.box1 = self.builder.get_object('box1')
        self.box2 = self.builder.get_object('box2')
        self.boxControls = self.builder.get_object('boxControls')
        self.boxFileOpen = self.builder.get_object('boxFileOpen')
        self.boxFooter = self.builder.get_object('boxFooter')
        self.boxInButtonRegenerate = self.builder.get_object('boxInButtonRegenerate')
        self.boxMain = self.builder.get_object('boxMain')
        self.boxOptions = self.builder.get_object('boxOptions')
        self.boxOutputControls = self.builder.get_object('boxOutputControls')
        self.boxTheme = self.builder.get_object('boxTheme')
        self.buttonAbout = self.builder.get_object('buttonAbout')
        self.buttonExit = self.builder.get_object('buttonExit')
        self.buttonFileOpen = self.builder.get_object('buttonFileOpen')
        self.buttonRegenerate = self.builder.get_object('buttonRegenerate')
        self.buttonSave = self.builder.get_object('buttonSave')
        self.checkbuttonInsertGlade = self.builder.get_object('checkbuttonInsertGlade')
        self.checkbuttonMakeExecutable = self.builder.get_object('checkbuttonMakeExecutable')
        self.comboTheme = self.builder.get_object('comboTheme')
        self.entryConfigSectionName = self.builder.get_object('entryConfigSectionName')
        self.entryNAME = self.builder.get_object('entryNAME')
        self.filterGlade = self.builder.get_object('filterGlade')
        self.fontbutton1 = self.builder.get_object('fontbutton1')
        self.image1 = self.builder.get_object('image1')
        self.label1 = self.builder.get_object('label1')
        self.label2 = self.builder.get_object('label2')
        self.label3 = self.builder.get_object('label3')
        self.labelFileOpen = self.builder.get_object('labelFileOpen')
        self.labelForInputPath = self.builder.get_object('labelForInputPath')
        self.labelOutput = self.builder.get_object('labelOutput')
        self.labelTheme = self.builder.get_object('labelTheme')
        self.labelVersion = self.builder.get_object('labelVersion')
        self.listTheme = self.builder.get_object('listTheme')
        self.paned1 = self.builder.get_object('paned1')
        self.scrollOutput = self.builder.get_object('scrollOutput')
        self.scrolledwindowForWarnings = self.builder.get_object('scrolledwindowForWarnings')
        self.srcviewOutput = self.builder.get_object('srcviewOutput')
        self.textviewForWarnings = self.builder.get_object('textviewForWarnings')
        self.viewportForWarnings = self.builder.get_object('viewportForWarnings')

        # Connect all signals.
        self.builder.connect_signals(self)

        #Reparent our main container from glader file,
        #this way we have all Gtk.Window functionality using "self"
        thechild = self.builder.get_object('winMain').get_child()
        thechild.get_parent().remove(thechild)
        self.add(thechild)

        # Connect all signals.
        self.buttonAbout.connect('clicked', self.on_buttonAbout_clicked)
        self.connect('destroy', self.on_winMain_destroy)
        self.connect('size-allocate', self.on_winMain_size_allocate)
        self.connect('window-state-event', self.on_winMain_window_state_event)
        self.paned1.connect('size-allocate', self.on_paned1_size_allocate)

        # Main window properties
        self.can_focus = 'False'
        self.default_height = '600'
        self.default_width = '750'
        self.destroy_with_parent = 'True'
        self.window_position = 'center'

        self.extra_initialisations()

#********* Auto created defs  ****************************************************************
    def on_buttonAbout_clicked(self, widget, *args):
        """ Handler for buttonAbout.clicked. """
        self.show_About()

    def on_buttonExit_clicked(self, widget, *args):
        """ Handler for buttonExit.clicked. """
        self.exit_requested()

    def on_buttonFileOpen_selection_changed(self, widget, *args):
        """ Handler for buttonFileOpen.selection-changed. """
        filename = widget.get_filename()
        if filename:
            self.gladesource = filename
            thepath = os.path.dirname(filename)
            settings.set('glade_last_path', thepath)
            self.labelForInputPath.set_label(thepath)
            # Automatically generate code for selected files.
            self.regenerate_and_show_code()

    def on_buttonRegenerate_clicked(self, widget, *args):
        """ Handler for buttonRegenerate.clicked. """
        self.regenerate_and_show_code()

    def on_buttonSave_clicked(self, widget, *args):
        """ Handler for buttonSave.clicked. """
        self.save_generated()

    def on_checkbuttonInsertGlade_toggled(self, widget, *args):
        """ Handler for checkbuttonInsertGlade.toggled. """
        settings.set('checkbuttonInsertGlade', self.checkbuttonInsertGlade.get_active())
        self.regenerate_and_show_code()

    def on_checkbuttonMakeExecutable_toggled(self, widget, *args):
        """ Handler for checkbuttonMakeExecutable.toggled. """
        settings.set('checkbuttonMakeExecutable', self.checkbuttonMakeExecutable.get_active())

    def on_comboTheme_changed(self, widget, *args):
        """ Handler for comboTheme.changed. """
        # Selected TreeIter.
        selitr = self.comboTheme.get_active_iter()
        if selitr is None:
            return None
        # Value for column 0 (the theme name)
        themename = self.listTheme.get_value(selitr, 0)
        self.set_theme(themename)

    def on_entryConfigSectionName_changed(self, widget, *args):
        """ Handler for entryConfigSectionName.changed. """
        self.regenerate_and_show_code()

    def on_entryNAME_changed(self, widget, *args):
        """ Handler for entryNAME.changed. """
        self.regenerate_and_show_code()

    def on_fontbutton1_font_set(self, widget, *args):
        """ Handler for fontbutton1.font-set. """
        font = widget.get_font_name()
        settings.set('font', font)
        self.srcviewOutput.modify_font(Pango.FontDescription(font))

    def on_paned1_size_allocate(self, widget, allocation, *args):
        """ Handler for paned1.size-allocate. """
        settings.set('paned1',self.paned1.get_position())

    def on_winMain_destroy(self, widget, *args):
        """ Handler for winMain.destroy. """
        self.exit_requested()
        return False

    def on_winMain_size_allocate(self, widget, allocation, *args):
        """ Handler for winMain.size-allocate. """
        self.set_window_size_in_settings()

    def on_winMain_window_state_event(self, widget, event, *args):
        """ Handler for winMain.window-state-event. """
        settings.set('maximized', False)
        if (int(event.new_window_state) & Gdk.WindowState.ICONIFIED) != Gdk.WindowState.ICONIFIED:
            if (int(event.new_window_state) & Gdk.WindowState.MAXIMIZED) == Gdk.WindowState.MAXIMIZED:
                settings.set('maximized', True)
        self.set_window_size_in_settings()

#********* Auto created defs END ************************************************************

    def show_About(self):
        aboutdialog = Gtk.AboutDialog()
        #show the localized name
        aboutdialog.set_program_name( _(NAME) )
        aboutdialog.set_version(VERSIONSTR)
        info_dir = os.path.join(self.BASE_DIR, 'info')
        if os.path.exists(os.path.join(info_dir, 'AUTHORS')):
            with open(os.path.join(self.BASE_DIR, 'info', 'AUTHORS'), mode='rt', encoding='utf-8') as f:
                aboutdialog.set_authors(f.readlines())
        if os.path.exists(os.path.join(info_dir, 'COPYRIGHT')):
            with open(os.path.join(self.BASE_DIR, 'info', 'COPYRIGHT'), mode='rt', encoding='utf-8') as f:
                aboutdialog.set_copyright(f.read())
        if os.path.exists(os.path.join(info_dir, 'COMMENTS')):
            with open(os.path.join(self.BASE_DIR, 'info', 'COMMENTS'), mode='rt', encoding='utf-8') as f:
                aboutdialog.set_comments(f.read())
        if os.path.exists(os.path.join(info_dir, 'TRANSLATORS')):
            with open(os.path.join(self.BASE_DIR, 'info', 'TRANSLATORS'), mode='rt', encoding='utf-8') as f:
                aboutdialog.set_translator_credits(f.read())
        aboutdialog.set_transient_for(self)
        aboutdialog.set_logo(self.get_icon())
        aboutdialog.run()
        aboutdialog.destroy()

    def starting_initialisations(self):
        """Do some initializations before loading the glade file.

        - Find a logo.
        - Set the version.
        - Find the glade file.

        Return the glade filename.
        """
        self.appVersion = __version__
        #Try to load the app icon
        self.set_logo()
        #TODO: remove from production version
        #If we have a file named debug, extract version from the directory name
        #else use the __version__  from this file
        if os.path.exists(os.path.join(self.BASE_DIR, 'debug')):
            forversion = os.path.basename(self.BASE_DIR)
            if len(forversion) > 2 and (forversion.count('.') == 3):
                self.appVersion = forversion[2:]
            #in case we have some buttons for debugging purposes
            #in order to show them only in debug mode
            self.show_test_buttons = True
        self.appVersionSTR = '{} v. {}'.format(_(NAME), self.appVersion)
        #bind the locale to a domain so that "locale" will search in these ".mo" files
        self.bind_locale()
        #Load the ui from a file
        #glade file will be either in the start directory
        gladefile = os.path.join(self.BASE_DIR, 'main.glade')
        if not os.path.exists(gladefile):
            #or in a subdirectory named glades
            gladefile = os.path.join(self.BASE_DIR, 'glades', 'main.glade')
        try:
            with open(gladefile, "r") as f:
                self.gladestring = f.read()
        except Exception as ex:
            print(str(ex))
            print('Error loading {gladefile}.\n{ex}'.format(gladefile= gladefile, ex=ex))
            sys.exit(ERROR_GLADE_FILE_READ)


    def extra_initialisations(self):
        """Do some extra initializations.

        Display the version if a labelVersion is found.
        Set defaults (try to load them from a configuration file):
            - Window size and state (width, height and if maximized)
            - Theme
            - Font
            - Last used path
        """
        #Show version
        self.labelVersion.set_label(self.appVersionSTR)
        #Set size and state
        width = settings.get('width', 350)
        height = settings.get('height', 350)
        self.set_title(_(NAME))
        self.resize(width, height)
        if settings.get_bool('maximized', False):
            self.maximize()
        self.buttonFileOpen.set_current_folder(settings.get('glade_last_path', "."))
        self.load_and_show_themes()
        # Build actual view for the code.
        self.srcviewOutput.set_buffer(self.bufferOutput)
        font = settings.get('font', 'Monospace Regular 8')
        self.fontbutton1.set_font_name(font)
        self.textviewForWarnings.get_buffer().set_text(_('Warnings:'))
        self.checkbuttonInsertGlade.set_active(settings.get_bool('checkbuttonInsertGlade', False))
        self.paned1.set_position(settings.get('paned1', 50))

    def load_and_show_themes(self):
        # Set theme.
        self.themeManager = GtkSource.StyleSchemeManager()
        # Map from theme id to StyleScheme.
        self.themes = {
            tid: self.themeManager.get_scheme(tid)
            for tid in self.themeManager.get_scheme_ids()}
        # Holds the currently selected theme info.
        self.theme = None
        celltheme = Gtk.CellRendererText()
        self.comboTheme.pack_start(celltheme, True)
        self.comboTheme.add_attribute(celltheme, 'text', 0)
        self.bufferOutput = GtkSource.Buffer()
        self.langManager = GtkSource.LanguageManager()
        self.bufferLang = self.langManager.get_language('python3')
        self.bufferOutput.set_language(self.bufferLang)
        self.bufferOutput.set_highlight_syntax(True)
        self.bufferOutput.set_highlight_matching_brackets(True)
        if not self.set_theme_config():
            # Use first preferred theme if available.
            themeprefs = (
                'oblivion', 'tomorrownighteighties', 'twilight', 'kate')
            for themeid in themeprefs:
                theme = self.themes.get(themeid, None)
                if theme:
                    self.set_theme(theme)
                    break
        self.build_theme_list()

    def set_logo(self):
        """Set logo image for the app.

        Try the current directory
        then a subdirectory named "icons".
        Set "self.appIcon" if a valid icon found.
        """
        logo = 'logo.png'
        thefile = os.path.join(self.BASE_DIR, logo)
        if not os.path.exists(thefile):
            #or in a subdirectory named icons
            thefile = os.path.join(self.BASE_DIR, 'icons', logo)
        try:
            self.appIcon = GdkPixbuf.Pixbuf.new_from_file(thefile)
            self.set_icon(self.appIcon)
        except Exception as e:
            pass

    def bind_locale(self):
        """Bind the domain for localization.

        Bind the locale dir with a subdirectory in the current path.
        Set the domain to  the domain with the NAMEASONE constant.
        """
        #next line will bind the locale to our own directory
        #and is not needed if we want our translation to be system wide
        locale.bindtextdomain(NAMEASONE, os.path.join(self.BASE_DIR, 'locale'))
        #this will bind the locale with some name
        #in order to load the corresponding .mo file for the language
        locale.textdomain(NAMEASONE)

    def exit_requested(self, *args):
        """Set the param in order to exit from "run" method.

        """
        self.we_can_exit_now = True

    def run(self):
        """Start the main loop.

        WARNING:
            The "destroy" event of the main window
            MUST be binded to set "we_can_exit_now" to True,
            else program will never exit.
        Save settings on exit.
        Return "return_parameter" on exit.

        """
        #now we can show the main window.
        self.show_all()
        #"enable" next line to have some interactive view of potentiallities of GUI
        #self.set_interactive_debugging (True)
        #loop eternaly
        while True:
            #if we want to exit...
            if self.we_can_exit_now:
                #break the loop
                break
            #else... give others a change...
            while Gtk.events_pending():
                Gtk.main_iteration()
        #we can now return to "caller"
        #print(settings)
        settings.save()
        #self.return_parameter = 0 #set return_parameter if needed, last change... to change... it!!!
        #return_parameter should be checked and defined usually before this
        return self.return_parameter

    def set_window_size_in_settings(self):
        """Save the window size into settings if not maximized.

        """
        if not settings.get_bool('maximized', False):
            width, height = self.get_size()
            settings.set('width', width)
            settings.set('height', height)

# Helper functions -------------------------------------------------------------------------

# Theme manager START ---------------------------------------------------------------------
    def build_theme_list(self):
        """ Build the content for self.listTheme based on self.themes.
            Sorts the names first.
        """
        selected = -1
        themeids = sorted(
            self.themes,
            key=lambda k: self.themes[k].get_name()
        )
        themenames = sorted((self.themes[k].get_name() for k in themeids))
        selthemename = self.theme.get_name()
        for i, themename in enumerate(themenames):
            newrow = self.listTheme.append((themename, ))
            self.listTheme.set_value(newrow, 0, themename)
            if themename == selthemename:
                selected = i
        # Set the currently selected theme.
        if selected > -1:
            self.comboTheme.set_active(selected)

    def get_theme_by_name(self, name):
        """ Retrieves a StyleScheme from self.themes by it's proper name.
            Like: Kate, or Oblivion.
            Returns None if the theme can't be found.
        """
        for themeid, stylescheme in self.themes.items():
            themename = stylescheme.get_name()
            if name == themename:
                return stylescheme
        return None

    def set_theme(self, scheme_identifier):
        """ Sets the current highlight theme by id, name, or StyleScheme.
            or by prefetched StyleScheme.
            Return True if the theme was set, otherwise False.
        """
        if isinstance(scheme_identifier, str):
            # Id or name?
            theme = self.themes.get(scheme_identifier, None)
            if theme is None:
                # Name.
                theme = self.get_theme_by_name(scheme_identifier)
        elif isinstance(scheme_identifier, GtkSource.StyleScheme):
            # StyleScheme (prefetched)
            theme = scheme_identifier
        else:
            # Unknown type for set_theme().
            errfmt = 'Expected name, id, or StyleScheme. Got: {}'
            raise ValueError(errfmt.format(type(scheme_identifier)))

        if theme is not None:
            self.theme = theme
            self.bufferOutput.set_style_scheme(theme)
            #print("theme", scheme_identifier)
            settings.set('theme_id', scheme_identifier)
            return True
        else:
            print("no theme")
        return False

    def set_theme_config(self):
        """ Try loading a theme from config.
            Return True if a theme was set, otherwise False.
        """
        themeid = settings.get('theme_id', None)
        if themeid:
            return self.set_theme(themeid)

# Theme manager END ---------------------------------------------------------------------

    def regenerate_and_show_code(self):
        if not hasattr(self, 'gladesource'):
            return
        indent = '' * 4
        set_glade_from_string = self.checkbuttonInsertGlade.get_active()

        GFG = GenerateFromGlade(self.gladesource)

        thefull = ''
        thetextfromskeleton = ''
        gladestrinit = ""
        warnings = []
        if set_glade_from_string:
            readgladefilecode = READFROMSTRING
            with open(self.gladesource, "r") as f:
                gladestr = f.read()
            gladestrinit = """#Set the Glade str
THEGLADESTR = \"\"\"{gladestr}\"\"\"\n""".format(gladestr=gladestr)
        else:
            readgladefilecode = READFROMFILE.format(gladefile=os.path.basename(self.gladesource))
        possiblename = self.entryNAME.get_text().strip()
        if len(possiblename):
            appname = possiblename
            appnameinit = "NAME = '{}'".format(appname)
        else:
            appname = 'From GladerRAD'
            appnameinit = "#FIXME: Give a meaningful descriptive name\nNAME = '{}'".format(appname)
            warnings.append(_('Generated app name, maybe not a good choise!'))
        possibleclass = self.entryConfigSectionName.get_text().strip()
        if len(possibleclass) and (' ' not in possibleclass):
            AppClass = possibleclass
            AppClassinit = "CONFIGDOMAIN = '{}'".format(AppClass)
        else:
            AppClass = os.path.splitext(os.path.basename(self.gladesource))[0]
            AppClassinit = "#FIXME: Give a meaningfull CamelCase name\nCONFIGDOMAIN = '{}'".format(AppClass)
            warnings.append(_('Generated class name, maybe not a good choise!'))
        try:
            with open('skeleton.nonpy.py', 'r') as f:
                thetextfromskeleton = f.read()
            thefull = thetextfromskeleton.format(indent1=indent, indent2=indent*2,
            date = datetime.today().strftime('%m-%d-%Y'),
            guiobjects = ''.join(sorted(GFG.generatedobjects)),
            selfsignals = ''.join(sorted(GFG.generatedconnects)),
            theproperties = indent*2 + '# Properties for self generated from Glade file\n' + '\n'.join(sorted(GFG.generatedproperties)),
            thedefs = ''.join(sorted(GFG.generateddefs)),
            extrasettingsforpaned = '\n'.join(sorted(GFG.forpaned)),
            mainwindow = GFG.windowid,
            gladefile = os.path.basename(self.gladesource),
            readgladefilecode = readgladefilecode,
            gladestrinit = gladestrinit,
            appname = appname,
            appnameinit = appnameinit,
            AppClass = AppClass,
            AppClassinit = AppClassinit
            )
        except Exception as e:
            print(str(e), repr(e))
            print(e.args)

        self.bufferOutput.set_text(thefull)
        for warning in warnings:
            GFG.warnings.insert(0, warning)
        self.textviewForWarnings.get_buffer().set_text(_('Warnings:') + '\n' + '\n'.join(GFG.warnings))

    def save_generated(self):
        """ Write the generated code to a file. """
        # Get generated code content.
        content = self.bufferOutput.get_text(
            self.bufferOutput.get_start_iter(),
            self.bufferOutput.get_end_iter(),
            True)

        if not content:
            self.MessageBox(_('There is nothing to save.'))
            return None

        # Create Dialog.
        dlg = Gtk.FileChooserDialog(
            _(NAME),
            self,
            Gtk.FileChooserAction.SAVE,
            (
                '_Cancel', Gtk.ResponseType.CANCEL,
                '_Save', Gtk.ResponseType.OK)
        )
        dlg.set_default_response(Gtk.ResponseType.OK)

        # Show hidden files
        dlg.set_show_hidden(True)
        # Set a save path
        dlg.set_current_folder(settings.get('last_save_path', os.path.dirname(self.gladesource)))
        # Set a default filename
        if len(self.entryNAME.get_text()):
            proposedname = self.entryNAME.get_text().replace(' ','') + '.py'
        else:
            proposedname = os.path.splitext(os.path.basename(self.gladesource))[0] + '.py'
        dlg.set_current_name(proposedname)

        # Show Dialog, get response
        response = dlg.run()
        respfile = dlg.get_filename()
        dlg.destroy()
        if response == Gtk.ResponseType.OK:
            if os.path.exists(respfile):
                message = (_('File') + ':\n{respfile}\n '.format(respfile=respfile) + _('already exists.\nOverwrite?'))
                ok_to_save = self.MessageBox(message=message, buttons='OK, CANCEL', boxtype = 'WARNING')
                if not ok_to_save:
                    return None
            self.last_save_path = os.path.dirname(respfile)
            settings.set('last_save_path', self.last_save_path)
            try:
                with open(respfile, 'w') as f:
                    f.write(content)
            except EnvironmentError as ex:
                message = _('There was an error writing to') + (':\n    {}\n\n{}').format(respfile, ex)
                self.MessageBox(message=message, boxtype = 'ERROR')
                return None

            msglines = [_('File was saved') + (': {}').format(respfile)]
            if self.checkbuttonMakeExecutable.get_active():
                try:
                    self.make_executable(respfile)
                    msglines.append(_('Mode +rwx (774) was set to make it executable.'))
                except (PermissionError, EnvironmentError) as experm:
                    message = _('Unable to make it executable') + (':\n  {}').format(experm)
                    msglines.append(message)

            self.MessageBox('\n'.join(msglines))
            return None

        else:
            return None

    def make_executable(self, filename):
        """ Make a file executable, by setting mode 774. """
        # chmod 774
        mode774 = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH
        os.chmod(filename, mode774)

    def MessageBox(self, message, buttons='', boxtype = 'INFO', *args):
        """Simple MessageBox.

        Keyword arguments:
        buttons -- comma or space delimeted string containing one or more of:
            YES, OK, CANCEL, NO
            defaults to: OK
        boxtype -- a string declaring the type of dialog. One of:
            ERROR, WARNING, QUESTION
            defaults to: INFO

        """
        Buttons = tuple()

        if 'YES' in buttons:
            Buttons += (_('_Yes'), Gtk.ResponseType.OK)
        elif 'OK' in buttons:
            Buttons += (_('_OK'), Gtk.ResponseType.OK)
        if 'NO' in buttons:
            Buttons += (_('_No'), Gtk.ResponseType.CANCEL)
        elif 'CANCEL' in buttons:
            Buttons += (_('_Cancel'), Gtk.ResponseType.CANCEL)
        if len(Buttons) == 0:
            Buttons += (_('OK'), Gtk.ResponseType.OK)
        if boxtype == 'ERROR':
            MessageType = Gtk.MessageType.ERROR
        elif boxtype == 'WARNING':
            MessageType = Gtk.MessageType.WARNING
        elif boxtype == 'QUESTION':
            MessageType = Gtk.MessageType.QUESTION
        else:
            MessageType = Gtk.MessageType.INFO
        title = boxtype
        dialog = Gtk.MessageDialog(self, 0, MessageType, Buttons, _(title))
        dialog.format_secondary_text(message)
        dialog.set_title(_(NAME))
        dialog.vbox.set_spacing (3)
        for a in dialog.vbox:
            for b in a:
                if type(b) == Gtk.ButtonBox:
                    b.set_halign(Gtk.Align.CENTER)
        response = dialog.run()
        dialog.destroy()
        return True if response == Gtk.ResponseType.OK else False

class GenerateFromGlade:
    def __init__(self, gladefile=None):
        self.generatedobjects = []
        self.generatedconnects = []
        self.generatedproperties = []
        self.generateddefs = []
        self.extraconnections = []
        self.forpaned = []
        self.windowid = ''
        self.warnings = []
        self.gladefile = gladefile
        self.generate_basic()

    def generate_basic(self):
        spacing = ' ' * 4
        self.windowid = None
        #signals = {}
        objects = {}
        showAboutcode = """self.show_About"""
        Exitcode = """self.exit_requested"""
        try:
            #signals from glade will be connected to self.signalname
            #signals from main window will be connected sto self.nameofwindow.signal
            with open(self.gladefile, 'r') as f:
                thetext = f.read()
            soup = BS(thetext, 'xml')
            #find main window
            for thewindow in soup.find_all('object', "GtkWindow"):
                self.windowid = thewindow.attrs['id']
            #find all obects and append to objects dict
            for anobject in soup.find_all('object'):
                if not anobject.attrs['id'].isidentifier():
                    self.warnings.append("{w} is not a valid identifier. FIT IT!".format(w=anobject.attrs['id']))
                if iskeyword(anobject.attrs['id']):
                    self.warnings.append("{w} as identifier will mesh with keywords. FIT IT!".format(w=anobject.attrs['id']))
                objects[anobject.attrs['id']] = {'class' : anobject.attrs['class'], 'signals':{}, 'properties':{}}
            #find all signals and append them to objects
            for asignal in soup.find_all("signal"):
                objects[asignal.parent['id']]['signals'][asignal['name']] = {'handler':asignal['handler'],'fromglade':True}
            #create some default signals if they do not exist
            for o in objects:
                #clicked for  buttons and
                if objects[o]['class'] == "GtkButton" and 'clicked' not in objects[o]['signals']:
                    objects[o]['signals']['clicked'] = {}
                    objects[o]['signals']['clicked']['handler'] = 'on_{o}_clicked'.format(o=o)
                    objects[o]['signals']['clicked']['fromglade'] = False
                    self.warnings.append("Created signal 'clicked' for object '{o}'.".format(o=o))
                #size-allocate for paned
                if objects[o]['class'] == "GtkPaned" and ('size-allocate' not in objects[o]['signals']):
                    objects[o]['signals']['size-allocate'] = {}
                    objects[o]['signals']['size-allocate']['handler'] = 'on_{o}_size_allocate'.format(o=o)
                    objects[o]['signals']['size-allocate']['fromglade'] = False
                    self.warnings.append("Created signal 'size-allocate' for object '{o}'.".format(o=o))
                #'destroy', 'window-state-event', 'size-allocate' for main window
                if o == self.windowid:
                    #if there are not some default signals for main window, generate as on_signalname
                    #TODO: check, maybe later, if some defs with the same name exist and are connected to different object
                    for signal in ['destroy', 'window-state-event', 'size-allocate']:
                        if signal not in objects[o]['signals']:
                            objects[o]['signals'][signal] ={}
                            objects[o]['signals'][signal]['handler'] = 'on_{o}_{signal}'.format(o=o, signal=signal.replace('-', '_'))
                            objects[o]['signals'][signal]['fromglade'] = False
                            self.warnings.append("Created signal '{signal}' for object main window.".format(signal=signal))

            #Create properties for main window which will be repareted
            #Only normal properties, not packing properties
            for aproperty in soup.find_all("property"):
                #print("aproperty",aproperty)
                #packing as parent does not have id. Check first != 'packing'
                if aproperty.parent.name != 'packing' and aproperty.parent['id'] == self.windowid:
                    if 'translatable' in aproperty.attrs:
                        translatable = aproperty['translatable']
                    else:
                        translatable = ''
                    thevalue = '\n'.join(aproperty.children)
                    #print('aproperty.name', aproperty.name)
                    #print("aproperty['name']",aproperty['name'])
                    objects[aproperty.parent['id']]['properties'][aproperty['name']]={'value':thevalue, 'translatable':translatable}

            #generate the codes
            for o in objects:
                if o == self.windowid:
                    #bind the main window properties to self
                    for aproperty in objects[o]['properties']:
                        #print('aproperty',aproperty)
                        thepropsline = spacing * 2 + "self." + aproperty + " = '" + objects[o]['properties'][aproperty]['value'] + "'"
                        self.generatedproperties.append(thepropsline)
                #create a local name for objects (except main window)
                else:
                    theline = spacing * 2 + "self.{lala} = self.builder.get_object('{lala}')\n".format(lala = o,)
                    self.generatedobjects.append(theline)
                #if object has signals create the def lines
                if objects[o]['signals']:
                    #create defs for the signals
                    for signal in objects[o]['signals']:
                        theline = self.create_the_def(objects[o]['class'], signal, objects[o]['signals'][signal]['handler'], o)
                        #print('signal',signal, 'object',o)
                        add_pass = True
                        #all signals of main window should be connected to self
                        if o == self.windowid:
                            #print('signal',signal,objects[o]['signals'][signal])
                            self.generatedconnects.append(spacing * 2 + "self.connect('" + signal + "', self." +  objects[o]['signals'][signal]['handler'] + ')\n')
                            #Also append code for specific signals
                            if signal == 'destroy':
                                theline += spacing * 2 + "self.exit_requested()\n" + spacing * 2 + "return False\n\n"
                                add_pass = False
                            elif signal == 'window-state-event':
                                theline += spacing * 2  + """settings.set('maximized', False)
        if (int(event.new_window_state) & Gdk.WindowState.ICONIFIED) != Gdk.WindowState.ICONIFIED:
            if (int(event.new_window_state) & Gdk.WindowState.MAXIMIZED) == Gdk.WindowState.MAXIMIZED:
                settings.set('maximized', True)
        self.set_window_size_in_settings()\n\n"""
                                add_pass = False
                            elif signal == 'size-allocate':
                                theline += spacing * 2 + 'self.set_window_size_in_settings()\n\n'
                                add_pass = False

                        #for the rest of the objects
                        #append code for specific signals
                        else:
                            if signal == 'clicked':
                                if o == 'buttonAbout':
                                    theline += spacing * 2 + '{thecode}()\n\n'.format(thecode=showAboutcode)
                                    add_pass = False
                                if o == 'buttonExit':
                                    theline += spacing * 2 + '{thecode}()\n\n'.format(thecode=Exitcode)
                                    add_pass = False
                            if objects[o]['class'] == "GtkPaned" and signal == 'size-allocate':
                                theline += spacing * 2 + "settings.set('{widget}',self.{widget}.get_position())\n\n".format(widget=o)
                                textforloading = spacing * 2 + "self.{widget}.set_position(settings.get('{widget}', 50))".format(widget=o)
                                self.forpaned.append(textforloading)
                                add_pass = False
                            if len(theline):
                                if add_pass:
                                    theline += spacing * 2 + 'pass\n\n'
                        self.generateddefs.append(theline)
                        #print(objects[o]['signals'])
                        #if object is not the main window
                        #and the signal was not present in glade
                        #we must connect it
                        if o != self.windowid and (not objects[o]['signals'][signal]['fromglade']):
                            self.generatedconnects.append(spacing * 2 + "self.{o}.connect('{signal}', self.{handler})\n".format(o=o, signal=signal, handler = objects[o]['signals'][signal]['handler']))

        except Exception as e:
            raise e
            #print('Exception', str(e))
            #print(e.args)

    def create_the_def(self, widgettype, signalname, signalhandler, widgetname):
        spacing = ' ' * 4
        defaultargs = ('self', 'widget', '*args')
        content = spacing + 'def {signalhandler}('
        if widgettype.startswith('Gtk'):
            # Actual classes do not start with 'Gtk'.
            gtkname = widgettype[3:]
        else:
            gtkname = widgettype
        # Find the widget class in Gtk.
        widget = getattr(Gtk, gtkname, None)
        eventfunc = 'do_{}'.format(signalname.replace('-', '_'))
        widgetevent = getattr(widget, eventfunc, None)
        # Get argument info.
        if hasattr(widgetevent, 'get_arguments'):
            # Return default and known args.
            knownargs = (ai.get_name() for ai in widgetevent.get_arguments())
            formattedargs = ['self', 'widget']
            if knownargs:
                formattedargs.extend(knownargs)
            formattedargs.append('*args')
            content += ', '.join(formattedargs)
        else:
            content += ', '.join(defaultargs)
        content += '):\n' + spacing * 2 + '""" Handler for {widgetname}.{signalname}. """\n'

        return content.format(signalhandler=signalhandler,signalname=signalname,widgetname=widgetname)

if __name__ == '__main__':
    """ Main entry point for the program. """
    app_to_use = GladerRADApp()
    response = app_to_use.run()
    #print('response:', response)
    sys.exit(response)
