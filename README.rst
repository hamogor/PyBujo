# PyBujo

PyBujo uses pick and curses to provide a barebones interactive way of creating, managing and visualizing notes
 
PyBujo is a simple and effective means of notetaking from the command line. I really disliked how much bulk and crazy functionality most notetaking cli's were packaged with so I built a very simple and extensible one for you.

``pip install bujo``

  
+---------------------+---------------------------------+
| Command Line        |                                 |
+---------------------+---------------------------------+
| Command             | Output                          |
+---------------------+---------------------------------+
| bujo *name of bujo* | Opens Action Menu for that bujo |
+---------------------+---------------------------------+
| bujo                | Opens Select Bujo Menu          |
+---------------------+---------------------------------+

+-------------+-------------------------------------+
| Select Menu |                                     |
+-------------+-------------------------------------+
| Key         | Output                              |
+-------------+-------------------------------------+
| a           | Add a new Bujo                      |
+-------------+-------------------------------------+
| r           | Remove currently selected bujo      |
+-------------+-------------------------------------+
| e           | Edit currently selected bujo        |
+-------------+-------------------------------------+
| q           | Quit Bujo                           |
+-------------+-------------------------------------+
| h           | Display link for this documentation |
+-------------+-------------------------------------+

+-------------+------------------------------------------------+
| Action Menu |                                                |
+-------------+------------------------------------------------+
| Key         | Output                                         |
+-------------+------------------------------------------------+
| a           | Adds a new note                                |
+-------------+------------------------------------------------+
| r           | Remove currently selected note                 |
+-------------+------------------------------------------------+
| e           | Edit currently selected note                   |
+-------------+------------------------------------------------+
| q           | Quit Bujo                                      |
+-------------+------------------------------------------------+
| h           | Display link for this documentation            |
+-------------+------------------------------------------------+
| m           | Move currently selected note to different bujo |
+-------------+------------------------------------------------+
| b           | Go back to Select Menu                         |
+-------------+------------------------------------------------+
