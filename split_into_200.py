import sys
import os
import shutil

input_folder_path = sys.argv[1]
output_folder_path = sys.argv[2]
if not os.path.isdir(input_folder_path):
    raise Exception("Input not a folder")
if not os.path.isdir(output_folder_path):
    os.makedirs(output_folder_path)

class OutputFolder(object):

    def __init__(self, path):
        self.fns = []
        self.path = path
        if not os.path.isdir(path):
            os.mkdir(path)


    def copy_to_folder(self, file_path):
        if self.is_full:
            raise Exception("Im full!")


        fn = os.path.basename(file_path)
        if os.path.splitext(fn)[1].lower() not in [".jpg", ".png"]:
            print "Ignoring %s" % file_path
            return

        output_fn = fn
        while output_fn in self.fns:
            output_fn = "_" + output_fn

        self.fns.append(output_fn)
        shutil.copyfile(file_path, os.path.join(self.path, output_fn))


    @property
    def is_full(self):
        return len(self.fns) >= 200


                        
num_output_folders = 0
current_output_folder = OutputFolder(os.path.join(output_folder_path,
                                                  str(num_output_folders)))

for root, dirs, files in os.walk(input_folder_path):
    if not files:
        continue

    for fn in files:
        if current_output_folder.is_full:
            num_output_folders += 1
            current_output_folder = OutputFolder(
                os.path.join(output_folder_path, str(num_output_folders))
            )


        current_output_folder.copy_to_folder(os.path.join(root, fn))


