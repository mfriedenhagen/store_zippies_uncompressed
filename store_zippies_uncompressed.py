from __future__ import with_statement
import os
import sys
import zipfile

THUMBNAIL_NAMES = [
    "Thumbnails/thumbnail.jpg", # xmind
    "Thumbnails/thumbnail.png"  # open office
]
EXTENSIONS = [".xmind",]
EXTENSIONS.extend((".odp", ".odt", ".ods", ".odg",)) # OO-Documents
EXTENSIONS.extend((".otp", ".ott", ".ots", ".otg",)) # OO-Templates

def replaceOriginalWithUncompressedWithoutThumb(name, thumbnailNames = THUMBNAIL_NAMES):
    infile_stats = os.stat(name)
    infile = zipfile.ZipFile(name, "r")
    tmpname = name + ".tmp"
    hasThumbnail = False
    try:
        hasThumbnail = len([f for f in infile.infolist() if f.orig_filename in thumbnailNames]) > 0
        if hasThumbnail:
            outfile = zipfile.ZipFile(tmpname, "w", compression=zipfile.ZIP_STORED)
            try:
                for f in infile.infolist():
                    if f.orig_filename not in thumbnailNames:
                        outfile.writestr(f.orig_filename, infile.read(f.orig_filename))
                    else:
                        hasThumbnail = True
            finally:
                outfile.close()
        else:
            print("Without thumbnail %s" % name)
    finally:
        infile.close()
    if hasThumbnail:
        print("With thumbnail %s" % name)
        # Do not use rename but "cat" to avoid changing ctime and permissions
        with open(name, "w") as outfile:
            with open(tmpname, "r") as infile:
                outfile.write(infile.read())
        # Reset atime and mtime
        os.utime(name, (infile_stats.st_atime, infile_stats.st_mtime))
        os.unlink(tmpname)

def addXmind(arg, dirname, fnames):
    for fname in fnames:
        root, extension = os.path.splitext(fname)
        if extension in EXTENSIONS:
            arg.append(os.path.join(dirname, fname))
xminds = []
os.path.walk(sys.argv[1], addXmind, xminds)
for xmind in xminds:
    replaceOriginalWithUncompressedWithoutThumb(xmind)

