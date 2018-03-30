#!/usr/bin/env python3
"""
    ...
    Copyright , {date}
    Contact:
    Licence:
"""

{appnameinit}
NAMEASONE = NAME.replace(' ', '_')
{AppClassinit}
#FIXME: correct the version
__version__ = '0.0.1'
VERSIONSTR = '{{}} v. {{}}'.format(NAME, __version__)

#RETURN ERROR CODES
ERROR_IMPORT_GTK_FAIL = -1
ERROR_IMPORT_LIBRARIES_FAIL = -2
ERROR_INVALID_GLADE_FILE = -3
ERROR_GLADE_FILE_READ = -4
{gladestrinit}
def import_Gtk_failed(err):
    """ Fail with a friendlier message when imports fail. """
    msglines = (
        '{{namever}} requires some third-party libraries.',
        'Please install requirements using \'pip\' or your package manager.',
        'The import error was:',
        '    {{err}}\n'
    )
    print('\n'.join(msglines).format(namever=VERSIONSTR, err=err))
    sys.exit(ERROR_IMPORT_GTK_FAIL)

try:
    from gi import require_version as gi_require_version
    gi_require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError as eximp:
    import_Gtk_failed(eximp)

# If Gtk is imported then we can show a Gtk.MessageDialog
# for other import errors.
def import_fail(err):
    """ Fail with a Gtk.MessageDialog message when imports fail. """
    msglines = (
        '{{namever}} requires some third-party libraries.',
        'Please install requirements using \'pip\' or your package manager.',
        'The import error was:',
        '    {{err}}\n'
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
    import os, sys
    from gi.repository import Gdk, GdkPixbuf, GLib, GObject
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
                self.parser[CONFIGDOMAIN] = {{}}
            self.ok = True
        except Exception as ex:
            print("ex", ex, repr(ex))

    def get(self, thekey, thedefault):
        """Get a value for a key based on the type of the provided default value.

        Return a default value if key does not exists.

        """
        if self.parser.has_option(CONFIGDOMAIN, thekey):
            if type(thedefault) == str:
                return self.parser.get(CONFIGDOMAIN, thekey)
            elif type(thedefault) == bool:
                return self.parser.getboolean(CONFIGDOMAIN, thekey)
            else:
                return self.parser.getint(CONFIGDOMAIN, thekey)
        else:
            return thedefault

    def get_bool(self, thekey, thedefault):
        """Get a boolean value for a key.

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

class {AppClass}(Gtk.Window):
    """Main window with all components. """

    def __init__(self, parent=None, transient=False):
        self.BASE_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        Gtk.Window.__init__(self)

        self.we_can_exit_now = False
        self.return_parameter = None

        #do some initilizations
        #and get the glade filename
        self.starting_initialisations()
        self.builder = Gtk.Builder()
        try:
            self.builder.add_from_string(self.gladestring)
        except Exception as ex:
            print(str(ex))
            print('\nError building main window!\n{mainwindow}'.format(ex))
            sys.exit(ERROR_INVALID_GLADE_FILE)

        # Get gui objects
{guiobjects}
        # Connect signals existing in the Glade file
        self.builder.connect_signals(self)

        #Reparent our main container from glader file,
        #this way we have all Gtk.Window functionality using "self"
        thechild = self.builder.get_object('{mainwindow}').get_child()
        thechild.get_parent().remove(thechild)
        self.add(thechild)

        # Connect generated signals.
{selfsignals}

{theproperties}

        self.extra_initialisations()
#********* Auto created defs ********************************************************************
#********* Auto created signals ****************************************
{thedefs}

#********* Auto created signals  END************************************

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
        #bind the locale to a domain so that "locale" will search in these ".mo" files
        self.bind_locale()
        {readgladefilecode}
    def extra_initialisations(self):
        """Do some extra initializations.

        Display the version if a labelVersion is found.
        Set defaults (try to load them from a configuration file):
            - Window size and state (width, height and if maximized)

        """
        #Set size and state
        width = settings.get('width', 350)
        height = settings.get('height', 350)
        self.set_title(_(NAME))
        self.resize(width, height)
        if settings.get_bool('maximized', False):
            self.maximize()
        #Show version
        if hasattr(self, 'labelVersion'):
            self.labelVersion.set_label(VERSIONSTR)
        #If an icon found bind it
        if hasattr(self, 'appIcon'):
            self.set_icon(self.appIcon)
{extrasettingsforpaned}
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

    def set_window_size_in_settings(self):
        """Save the window size into settings if not maximized. """
        if not settings.get_bool('maximized', False):
            width, height = self.get_size()
            settings.set('width', width)
            settings.set('height', height)

    def show_About(self):
        """Show an About dialog.

        Searches a subdirectory named "info" for the content.
        """
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

    def exit_requested(self, *args):
        """Set the param in order to exit from "run" method. """
        self.we_can_exit_now = True

    def run(self):
        """Start the main loop.

        WARNING:
            The "destroy" event of the main window
            MUST set the "we_can_exit_now" to True,
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

#********* Auto created defs  END*********************************************************

if __name__ == '__main__':
    """ Main entry point for the program. """
    app_to_use = {AppClass}()
    response = app_to_use.run()
    #print('response:', response)
    sys.exit(response)
