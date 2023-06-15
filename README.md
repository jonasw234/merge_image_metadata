# Merge Image Metadata
Currently only tested and working on Windows 10.

Merge metadata between images.  
Useful for cases when metadata was already added and then you receive the high-res version afterwards.

Assumes that you want to merge the `Keyword`, `Subject`, and `HierarchicalSubject` fields as used by Adobe Bridge.

Currently merges metadata between two consecutive images only (i.e. will not correctly detect triplicates).

# Usage
```
Usage: merge_image_metadata.py [-v] FOLDER

Options:
    -v  Enable verbose (debug) output
```

# Installation
[exiftool](https://exiftool.org/) needs to be available in the PATH at runtime.

For the development version:

```
git clone https://github.com/jonasw234/merge_image_metadata
cd merge_image_metadata
python3 setup.py install
pip3 install -r dev-requirements.in
```

For normal usage do the same but don’t include the last line or use `[pipx](https://pypi.org/project/pipx/)` and install with

`pipx install git+https://github.com/jonasw234/merge_image_metadata`
