#!/usr/bin/env python

import signal
import sys
import os
import argparse
import ConfigParser
import subprocess
import flickr_api


class PhotoUploader(object):

    def __init__(self, recreate_exif=False, upload_to_set=False, user=None, tags=''):
        self.upload_to_set = upload_to_set
        self.recreate_exif = recreate_exif
        self.user = user
        self.tags = tags
        self.photos = {}

        if self.upload_to_set:
            self.photosets = {}
            photosets = user.getPhotosets() 
            for photoset in photosets:
                self.photosets[photoset.title] = photoset


    def is_valid(self, file_path):
        return os.path.splitext(file_path)[1].lower() in [".jpg", ".png"]

    def upload_photo(self, file_path):
        dir_path, name = os.path.split(file_path)
        name = os.path.splitext(name)[0]

        if not self.is_valid(file_path):
            print "Ignoring '%s'" % file_path
            return

        if self.recreate_exif:
            subprocess.check_call(["jhead", "-de", file_path],
                                  stdout=subprocess.PIPE)
            subprocess.check_call(["jhead", "-mkexif", file_path],
                                  stdout=subprocess.PIPE)

        if self.upload_to_set:
            photoset_title = os.path.basename(dir_path.rstrip("/"))
            # flickr_api seems to use unicode
            try:
                photoset_title = unicode(photoset_title)
            except UnicodeDecodeError:
                photoset_title = photoset_title.decode('iso8859-1')

            if self.exist_in_photoset(name, photoset_title):
                return

        flickr_photo = flickr_api.upload(photo_file=file_path,
                                         title=name,
                                         tags=self.tags,
                                         is_public=0)

        if self.upload_to_set:
            self.add_to_photoset(flickr_photo, photoset_title)


    def add_to_photoset(self, photo, photoset_title):
        assert self.upload_to_set

        if photoset_title not in self.photosets:
            photoset = flickr_api.Photoset.create(title=photoset_title,
                                                  primary_photo=photo)
            self.photosets[photoset_title] = photoset
        else:
            self.photosets[photoset_title].addPhoto(photo=photo)

    def exist_in_photoset(self, name, photoset_title):
        assert self.upload_to_set

        if photoset_title not in self.photos:
            photoset = self.photosets.get(photoset_title, None)
            if not photoset:
                return False

            self.photos[photoset_title] = photoset.getPhotos()

        for photo in self.photos[photoset_title]:
            if name == photo.title:
                return True
        
        return False


def main():

    args = parse_args()

    print "Logging in..."

    auth_file = "flickr.auth"
    key_file = "keys.conf"

    config = ConfigParser.RawConfigParser()
    config.read(key_file)

    flickr_api.set_keys(config.get("auth", "api_key"),
                        config.get("auth", "api_secret"))

    if not os.path.isfile(auth_file):
        a = flickr_api.auth.AuthHandler()
        url = a.get_authorization_url("write")
        print ("Allow access to flickr through this url, then copy and "
               "paste the oauth_verifier here")
        print url

        sys.stdout.write("\noauth_verifier: ")
        oauth_verifier = raw_input()
        a.set_verifier(oauth_verifier)
        flickr_api.set_auth_handler(a)

        a.save(auth_file)

    else:
        try:
            flickr_api.set_auth_handler(auth_file)
        except Exception as e:
            os.remove(auth_file)
            print "Need to reauthorize, run the script again"


    user = flickr_api.test.login()

    uploader = PhotoUploader(recreate_exif=args.recreate_exif,
                             upload_to_set=args.put_in_sets,
                             user=user,
                             tags=args.tags)
    print "Counting..."
    paths_to_upload = []

    for root, dirnames, fns in os.walk(args.input_folder):
        if '.picasaoriginals' in dirnames:
            dirnames.remove('.picasaoriginals')
        for fn in fns:
            if not uploader.is_valid(fn):
                continue

            file_path = os.path.join(root, fn)
            paths_to_upload.append(file_path)

    for i, file_path in enumerate(sorted(paths_to_upload)):
        if stop:
            sys.exit(130)
        name = os.path.basename(file_path)

        restart_line()
        sys.stdout.write("%d/%d: '%s'" % (i+1, len(paths_to_upload), name))

        uploader.upload_photo(file_path)

    print ""

def restart_line():
    sys.stdout.write('\r')
    sys.stdout.flush()

def directory(dir_path):
    if os.path.isdir(dir_path):
        return os.path.abspath(dir_path)
    else:
        raise argparse.ArgumentTypeError("Not a directory")


def parse_args():

    parser = argparse.ArgumentParser(description="Upload some flickr photos")

    parser.add_argument("input_folder", type=directory,
                        help="Folder containing photos and other folders")
    parser.add_argument("-s", "--put-in-sets", action="store_true",
                        help=("Uses the folder name containing the photos to "
                              "place them in sets"))
    parser.add_argument("-e", "--recreate-exif", action="store_true",
                        help=("Replaces the exif data of the date taken with "
                              "the creation date of the file"))
    parser.add_argument("-t", "--tags", nargs='?', default='',
                        help=("A space-seperated list of tags "
                              "to apply to the photo"))

    return parser.parse_args()

def signal_handler(signal, frame):
    global stop
    stop = True

if __name__ == "__main__":
    global stop
    stop = False
    signal.signal(signal.SIGINT, signal_handler)
    main()
