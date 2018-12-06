## PyPlayer - Local Video Player in Python

### Description

PyPlayer uses a Kivy GUI to allow users to select and play movies from a list of local movie files.  Movie information is collected through the Open Movie Data Base (OMDb) API and stored in a local ZODB database.

<img src="https://github.com/txpmr001/PyPlayer/blob/master/screenshot.jpg" alt="screenshot">

### Requirements

 1.  PyPlayer is written in [python](https://www.python.org/) 2.7. Instructions on how to download and install python can be found here: [python downloads](https://www.python.org/downloads/)
 2. The GUI is written in [Kivy](https://kivy.org/#home) 1.10.1. Instructions on how to download and install Kivy can be found here:  [Kivy User’s Guide »  Installation](https://kivy.org/doc/stable/installation/installation.html)
 3. Movie information is collected through the  [Open Movie Data Base (OMDb) API](http://www.omdbapi.com/). PyPlayer uses a python wrapper around the OMDb API which can be found here: [omdb.py](https://github.com/dgilland/omdb.py) The OMDb API requires a key which can be obtained here: [OMDb API Key](http://www.omdbapi.com/apikey.aspx)
 4. After retreiveing information from OMDb, PyPlayer stores the data in a [ZODB](http://www.zodb.org/en/latest/#) object database. Instructions on how to install and use ZODB can be found here: [ZODB Tutorial](http://www.zodb.org/en/latest/tutorial.html)

### Using PyPlayer

Download all PyPlayer files. Set *movie_dir* to point to the local file directory that contains movie files. Update list *movie_file_extentions* to reflect the movie file extentions in the *movie_dir*. Set *api_key* to be your OMDb API Key as explained in the requirements section.


> Written with [StackEdit](https://stackedit.io/).