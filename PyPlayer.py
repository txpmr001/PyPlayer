#!/usr/bin/env python
'''Play local movie files.

PyPlayer uses a Kivy GUI to allow users to select and play movies from a list of local
movie files.  Movie information is collected from the Open Movie Data Base (OMDB) and stored
in a local ZODB object database.

Todo:
    * Add auto / manual delete of db entries for files that no longer exist.
'''

#------------------------------ Modules, Classes, & Definitions

import sys, os, re
from requests import get as requests_get, exceptions as requests_exceptions
from omdb import get as omdb_get, set_default as omdb_set_default

from ZODB import FileStorage, DB
from persistent import mapping
from transaction import commit

# Import kivy gui elements.
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

class Movie_File(object):
    '''Define the Movie_File object.'''

    def __init__(self, filename):
        '''Initialize a Movie_File object.

        Arg:
            filename (str): A complete local movie filename (name & extention).

        Example:
            Movie_File('The Incredibles.mp4')
        '''
        self.filename = filename
        self.file_name = filename.split('.')[0]
        self.file_ext = filename.split('.')[1]

        self.title = self.file_name
        self.db_idx = None
        self.display = None

        self.paren_info = None
        self.year = None

        pos = self.title.find('(')
        if pos >= 0:
            self.paren_info = self.title[pos+1 : self.title.find(')')]  # Save paren info.
            # Parse paren info.
            for item in self.paren_info.split():
                # Look for year.
                match = re.search(r'\d{4}', item)
                if match:
                    self.year = match.group()
                    continue
            self.title = self.title[:pos].strip()   # Remove paren info from title.
        self.fix_titles()
        self.db_idx = self.title
        if self.year:
            self.db_idx += ' (' + self.year + ')'   # Add year to DB idx.
        self.display = self.db_idx                  # Create display item for play list.

    def __repr__(self):
        return "Movie_File({})".format(repr(self.filename))

    def __str__(self):
        return self.filename

    def fix_titles(self):
        '''Fix titles as needed due to os file naming restrictions.'''
        if self.title == '50-50':
            self.title = '50/50'
        return

    def get_movie(self):
        '''Get movie info from the OMDB database.'''
        kwargs = {'title': self.title, 'fullplot': True, 'tomatoes': True}
        if self.year:
            # A movie with a year.
            kwargs['year'] = self.year      # Add year argument.

        movie = omdb_get(**kwargs)
        if movie:
            print movie['title'], '  -   from omdb, len(movie) =', len(movie)
            self.get_poster(movie)
        else:
            print '\n', 'omdb get fail:', self.filename, 'kwargs =', kwargs
        return movie

    def get_poster(self, movie):
        '''Download a movie poster file.

        Arg:
            movie (json): Info from the OMDB database.
        '''
        url = movie['poster']
        if url == 'N/A':
            movie['poster_file'] = None
            return
        try:
            request = requests_get(url)
        except requests_exceptions.RequestException as request_error:
            print 'requests get error: url =', url
            print request_error
            movie['poster_file'] = None
            return
        if request.status_code <> 200:
            print 'requests get error: request.status_code =', request.status_code, ', url =', url
            movie['poster_file'] = None
            return
        poster_folder = 'posters'
        if not os.path.exists(poster_folder):
            os.mkdir(poster_folder)
        poster_file = r'posters\\' + self.file_name + '.jpg'
        with open(poster_file, 'wb') as f:
            f.write(request.content)
        movie['poster_file'] = poster_file
        return

# Use kivy to define GUI elements and layout.
Builder.load_string('''
#: import utils kivy.utils

<ListItemButton>:
    size: (100, '30dp')
    text_size: self.size
    halign: 'left'
    valign: 'middle'
    selected_color: 0.0, 0.0, 0.0, 1
    deselected_color: 0.5, 0.5, 0.5, 1
    color: utils.get_color_from_hex('#70ffff')  # light cyan

<PlayButton>:
    source: 'play-button.png'
    pos_hint: {'center_x': .5, 'center_y': .5}

<AppWindow>:
    titles: titles
    plot: plot
    cast: cast
	poster: poster
    rows: 1
    padding: 20
    spacing: 20
    MovieListView:
        id: titles
        font_size: 18
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        FloatLayout:
            size_hint_y: 0.5
            PlayButton
        Label:
            text: 'Plot:'
            font_size: 20
            size_hint_y: 0.2
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        ScrollView:
            canvas.before:
                Color:
                    rgba: .1, .1, .1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: plot
                color: utils.get_color_from_hex('#70ffff')  # light cyan
                size_hint_y: None
                text_size: self.width, None
                height: self.texture_size[1]
                font_size: 18
        Label:
            text: 'Cast:'
            font_size: 20
            size_hint_y: 0.2
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        ScrollView:
            canvas.before:
                Color:
                    rgba: .1, .1, .1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: cast
                color: utils.get_color_from_hex('#70ffff')  # light cyan
                size_hint_y: None
                text_size: self.width, None
                height: self.texture_size[1]
                font_size: 18
        FloatLayout:
            size_hint_y: 0.3
            Image:
                source: 'logo.jpg'
                pos_hint: {'center_x': .5, 'center_y': .5}
	Image:
		id: poster
''')

class PlayButton(ButtonBehavior, Image):
    '''The PlayButton is used to play the selected movie.'''

    def on_press(self):
        '''Open the selected movie file with os.startfile. (Equivalent to double-click.)'''
        idx = app.app_window.titles.current_idx
        filename = movie_files[idx].filename
        os.startfile(filename)

class MovieListView(ListView):
    '''MovieListView displays the titles of local movie files.'''

    def __init__(self, **kwargs):
        '''Initialize MovieListView object.'''
        super(MovieListView, self).__init__(**kwargs)
        self.set_adapter()
        self.current_idx = 0

    def set_adapter(self):
        '''Set ListAdapter properties and selection change binding.'''
        self.adapter = ListAdapter(
            data=playlist,
            selection_mode='single',
            allow_empty_selection=False,
            cls=ListItemButton
        )
        self.adapter.bind(on_selection_change=self.selection_change)

    def selection_change(self, adapter, *args):
        '''Update the display when a new movie is selected.'''
        views = self.adapter.cached_views
        for key in views:
            view = views[key]
            new_idx = view.index
            if view.is_selected and self.current_idx <> new_idx:
                self.current_idx = new_idx
                app.app_window.update_display()

class AppWindow(GridLayout):
    '''Define the main display window.'''

    # Bind variables to kivy GUI elements.
    titles = ObjectProperty()
    plot = ObjectProperty()
    cast = ObjectProperty()
    poster = ObjectProperty()

    def __init__(self):
        '''Initialize the main display window'''
        super(AppWindow, self).__init__()
        self.update_display()

    def update_display(self):
        '''Get plot, cast, and poster for the current movie.'''
        idx = self.titles.current_idx
        self.plot.text = movies[playlist_db_map[idx]]['plot']
        self.cast.text = re.sub(r',\s*', '\n', movies[playlist_db_map[idx]]['actors'])
        self.poster.source = movies[playlist_db_map[idx]]['poster_file']

class PlayerApp(App):
    '''Define the kivy application.'''

    def build(self):
        '''Give the kivy application a title and a main display window.'''
        self.title = 'pyPlayer'
        self.app_window = AppWindow()
        return self.app_window

#------------------------------ Main Program
'''The Big Picture:

Set configuration variables.
Create/open the ZODB database.
Create a list of movie files in the movie directory.
Create a movie file object for each movie file.
For each movie file object, using filename as the key, check the database for a corresponding entry.
If the movie is in the database:
    use the database info
else:
    get the movie info from omdb and save it in the database
Create the kivy playlist and run the kivy app.
Close the ZODB database and exit.
'''

movie_dir = '.'                                         # Set movie directory.
movie_file_extentions = ['ISO', 'MP4', 'AVI', 'WMV']    # Set movie file types.
api_key = 'e408d3ba'                                    # Set OMDB api key.

# Open local file storage, database, connection, and set the root.
storage = FileStorage.FileStorage('zodb.fs')
db = DB(storage)
connection = db.open()
root = connection.root()
movie_key = 'movies'
print
if not root.has_key(movie_key):
    root[movie_key] = mapping.PersistentMapping()       # Add a persistent dictionary for movies.
    print 'created empty dict, root key =', repr(movie_key)
movies = root['movies']                                 # Reference persistent movie dictionary.
omdb_set_default('apikey', api_key)                     # Set default OMDB api key.

# Go to movie directory, make & sort a list of movie files.
os.chdir(movie_dir)
filelist = [f for f in os.listdir('.') if f.split('.')[-1].upper() in movie_file_extentions]
filelist.sort()

# Create a movie file object for each movie file.
movie_files = []
for f in filelist:
    movie_file = Movie_File(f)
    movie_files.append(movie_file)
    if movie_file.db_idx not in movies:
        movie = movie_file.get_movie()
        if movie:
            movies[movie_file.db_idx] = movie   # Add movie to database.
            commit()

# Go
playlist = []             # Create a playlist of movie titles for the gui.
playlist_db_map = {}      # Create a mapping from playlist idx to db idx.
for idx, movie_file in enumerate(movie_files):
    playlist.append(movie_file.display)
    playlist_db_map[idx] = movie_file.db_idx

app = PlayerApp()
app.run()

# Close connection, database, storage, then exit.
connection.close()
db.close()
storage.close()
sys.exit(0)
