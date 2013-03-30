py\_flickr\_upload
================

Scripts for uploading photos to flickr


Overview
--------
There are two scripts here. flickr\_upload.py does pretty much what you think.
Give an input folder and it uploads photos to your photostream. If you want it
can split the photos into sets based on the folders they're in, and it can
reset the 'date taken' exif data to the creation date of the file. The latter
is useful for files retrieved from services like facebook, which remember the
upload date of the photo as the creation date, but don't store any exif data.


split\_into\_200.py takes an input and output folder and splits all images into
folders with 200 images each. This is useful if you're using the flickr html5
uploader, which only takes 200 photos at a time.



Dependencies
-----------

[flickr\_api](https://code.google.com/p/python-flickr-api/)
[jhead](http://www.sentex.net/~mwandel/jhead/): Only if you want to modify the exif data

Usage
-----

`python flickr_upload.py ~/Pictures/Photo\ Library/Masters`

or 

`python split_into_200.py ~/Pictures/Photo\ Library/Masters ~/Desktop/output`


