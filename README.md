GladerRAD
=========

Generator of working skeleton code from a glade file. The generated signal handler stubs
can then be filled in to provide functionality. Arguments for signal handlers
are automatically decided through introspection using Gtk.

The generated python script can be run from command line.

The glade file still needs to be present in the finished application
directory unless you opt to insert it in the python file.

The whole idea, starting point and a bunch of code came from
Christopher's Welborn [Glader](https://github.com/welbornprod/glader).

Assumptions:
-------------

* Only indentation with 4 spaces is provided (and correctly handled...).
* The "skeleton.nonpy.py" file must be present.
* The final python file will use its real path and not the path from any shortcut (link).
* Only one main Window in the Glade file should be present.
* Properties and signals of the main window will be "imported".
* Its "destroy", "window-state-event" and "size-allocate" signals will be connected to
some predefined functions.

* Buttons without "clicked" signal will be connected to a "default" def.
* Buttons with names "buttonExit" and "buttonAbout" will be handled slightly different.
* Program will generate code to use settings from a .conf file
* -Settings file will be set to ~/.config/Nameofheapp.conf.
* -Setting will be read and written to a single predefined section.
* -Code for saving and loading window size, width and height will be generated.
* -Code for maximized state of window will be generated.
* -If any GtkPaned objects exist, code for save-load gutter position
will be generated, using as default the "50" (pixels).
* Code will include basic imports to support localization
(both inside code as well as for texts in the glade file).


Dependencies:
-------------

GladerRAD has several GTK-related dependencies. If you are already creating GTK
apps then you may have some of these installed already.

###System packages:

Installed with your package manager, like [apt](https://wiki.debian.org/apt-get).

* **gir1.2-gtk-3.0** - *Provides helpers and access to GIRepository.*
* **python3-gi** - *Provides python bindings for gobject-introspection.*
* **python3-bs4** - *Provides python bindings for gobject-introspection.*
* **libgtksourceview-3.0-dev** - *Provides the `GtkSourceView` widget.*

There may be others, I will fill in the missing dependencies as they are found.
Message me or file an issue if you run into errors.


Generated script:
-----------------

GladerRAD creates a python3 script with a class derived from Gtk.Window
with a dummy name MyWindow.
In the init section of this class performs the following:
- performs some pre-initialization:
-- connects the path of the file to self.BASE_DIR
-- initializes the Gtk.Window class with self
-- creates two parameters:
--- self.we_can_exit_now = False
--- self.return_parameter = None
-- finds a logo if exists
-- connects a domain for localization using [locale](https://docs.python.org/3.2/library/locale.html) python module
-- finds the Glade file to load
-- creates two 
Then it:
- reads the glade file
-- raises an exception if the file cannot be loaded and stops.
- creates self objects named after all Glade file objects
- re-parents the top container of the main window to self
- connects all signals to handlers using Gtk.Builder's `get_object` method
- connects signals and properties of top window to self
- performs some post-initialization as:
-- using a saved configuration file:
--- reads previous state and size of the main window
--- sets the text of a label named labelVersion (if exists) to version
--- connects the found logo (if exists) to self

methods of the class include:
- all handlers of signals found in the Glade file plus some generated handlers: 
-- handler for `clicked` event for every Gtk.Button found
-- handler for `size-allocate` event for every Gtk.Paned found
-- handlers for `destroy`, `window-state-event` and `size-allocate` events of self
 (for the top window found in Glade file)
-- handlers will be connected if not found in the Glade file
- `starting_initialisations`, `extra_initialisations`, `set_logo`, `bind_locale`,
`get_glade_filename` (all used for initialization)
- `run` 
- `show_About`

pre-generated code in some of the methods includes:
- code to start and destroy the window using the `run` method.
This method also saves the settings and returns a single parameter
- code to save the current state and size of the top window.
- code to exit if a Gtk.Button named _buttonExit_ found.
- code to show a simple About box, using the `show_About` method as well as
code for the handler of `clicked` event for a a Gtk.Button named _buttonAbout_
(if such object exists in Glade file)
- code to save the current position of the gutter for Gtk.Paned object found
(in the handler for `size-allocate` event of these objects).

Another class named `LocalConfig` will also be included and used to load previous
saved settings and keep tracking of these settings and save these settings
upon normal exit.

Settings will be saved in a file in a subfolder named .config in user's 'HOME' dir.
The name of the file and the section that file will use depend on the `NAME`
and `CONFIGDOMAIN` "locally" global constants, which should be changed 
in order to have better usage.

Generated code will not handle situations where special initialization is required.
Example of this is the `GtkSourceView` widget which needs to be registered 
before it is loaded from the Glade file. You have to do it by yourself.

Also an `if __name__ == '__main__':` will show the window if the script is run 
from command line.

How it works:
-------------

GladerRAD reads the the glade file and performs the following steps:
- finds the main window based on: _it is an object of class Gtk.Window_
-- this means will not be useful if more than one Gtk.Window is present
-- or if they are not used as the top level window.
- finds all objects and checks their names for compatibility using:
-- `isidentifier` python's str method
-- `iskeyword` python's method, from iskeyword "internal" module
- finds all signals attaching their `signal name` and `handler name` to objects
- checks if Gtk.Button objects (if exist) have the `clicked` signal
and adds them (if not present).
- checks if Gtk.Paned objects (if exist) have the `clicked` signal
and adds them (if not present).
- checks if top window has signals for `destroy`, `window-state-event`
and `size-allocate` and adds them (if not present).
- saves the values for any property of the top window found but not in `packing`

All generated code from the above actions is then "inserted"
in the string loaded from the `skeleton.nonpy.py` file as a whole.

How to use it:
--------------

Create a Glade file including a top level window, possibly including
- a Gtk.Button named _buttonAbout_ 
- a Gtk.Button named _buttonExit_
and save it.

Run the GladerRad and open the Glade file.
Save the generated code to a file. The Glade file should be in the same folder
or in a subfolder named _glades_. 
Run the saved python file either by double clicking or by opening a terminal.

If you make any changes to the Glade file that not include:
- new objects
- change of names of existing objects
- new signal handlers for any existing object
- changes in the names of any existing handlers
- changes in the properties or the name of the top level window
which means, you only rearranged the objects or you only changed their properties
(excluding properties of the top level window
you can run the generated (or even modified after) python file.

Otherwise, use again the GladerRad again to generate a new python script,
save it with under another name and use a tool, like [Meld](http://meldmerge.org/),
to compare and find the differences that you must make.


Compatibility:
--------------

GladerRAD is designed for
[PyGTK3](http://python-gtk-3-tutorial.readthedocs.org/en/latest/install.html),
and [Python 3](https://www.python.org/downloads/).

File an issue if there is something you would like to see.

Contributions:
--------------

Contributions are welcome. That's what this repo is for.
File an issue, or send me a pull request if you would like to see a
feature added to GladerRAD.
