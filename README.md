
# Poem Reader

A simple Poem Reader GUI application written in Python using PyGObject.

In the default application, two poems are present:
- Divina Commedia (Italian)
- Divine Comedy (English, translated by Longfellow)

The included poems are in the public domain.

## Bookmarks

In the header bar, a bookmark can be saved for the current poem. Only one bookmark per poem can be saved.

## Add poems

In order to add new poems, check https://github.com/stebenve86/poems_for_poem_reader repository. Create a folder (using the same name of the folders in that repository) in the *poems* folder and download all the files (text files and configuration json file).
Then, go to the "utilities" folder and run the **add_poem.py** script providing the **poems_delta.json** file path as argument:
```
USAGE: ./add_poem.py JSON_DELTA_FILE_PATH
```
