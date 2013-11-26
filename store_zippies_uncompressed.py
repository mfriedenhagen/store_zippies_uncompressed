"""
This python script will modify all zip style files like OpenOffice, XMind or iWork files,
remove the preview png, jpg or pdf parts and store the remaining files uncompressed (STORED)
thereby making them better suited for following changes in a SCM, e.g. Mercurial :-).

There are two modes supported right now:
- given an argument of `-` the script will read filenames from stdin
- given an argument other than `-` this is taken as a directory name

All files ending in EXTENSIONS are taken as a "zippy" file, from which THUMBNAIL_NAMES
will be removed and the remaining files will be stored in a new, uncompressed zip, which
will *replace* the original zip files while maintaining permissions and ctime, mtime and 
atime.

An optional argument `-d` will set the log level to DEBUG and spits out more information
during the process.

To use this with mercurial add something like::
    [hooks]
    pre-commit.store-zippies = hg status --modified --added --no-status | python store_zippies_uncompressed.py -
to your hgrc file located in the repository or your HOME (mercurial.ini on Windows).

This software is licensed under the Apache Software License (https://www.ohloh.net/licenses/apache).

Copyright Mirko Friedenhagen 2010.

For more information see: http://bitbucket.org/mfriedenhagen/store_zippies_uncompressed/
"""

import logging
import os
import sys
import zipfile

THUMBNAIL_NAMES = [
    "Thumbnails/thumbnail.jpg",                        # xmind
    "Thumbnails/thumbnail.png",                        # open office
    "QuickLook/Thumbnail.jpg", "QuickLook/Preview.pdf" # iWork
]
EXTENSIONS = [
    ".xmind",
    ".odp", ".odt", ".ods", ".odg", # OO-Documents
    ".otp", ".ott", ".ots", ".otg", # OO-Templates
    ".pages",                       # iWork
]

LOG = logging.getLogger()

def replaceOriginalWithTmp(source, target):
    """ Do not use rename but "cat" to avoid changing ctime and permissions.
        Use binary mode for opening files as otherwise this will fail 
        really bad under windows.        
    """
    LOG.debug("cat %s > %s" % (source, target))    
    outfile = open(target, "wb")
    try:
        infile = open(source, "rb")
        try:
            outfile.write(infile.read())
        finally:
            infile.close()
    finally:
        outfile.close()
    # Only unlink source if no exceptions happen during copy action!
    os.unlink(source)

def createUncompressedCopyWithoutThumbnail(tmpname, infile):
    """ Create a new, uncompressed ZIP and do store everything
        of infile except the thumbnails.
    """
    outfile = zipfile.ZipFile(tmpname, "w", compression=zipfile.ZIP_STORED)
    try:
        for f in infile.infolist():
            LOG.debug("Processing %s of %s" % (f.orig_filename, infile))
            if f.orig_filename not in THUMBNAIL_NAMES:
                LOG.debug("Storing %s" % f.orig_filename)
                outfile.writestr(f.orig_filename, infile.read(f.orig_filename))
            else:
                LOG.debug("Skipping %s" % f.orig_filename)
    finally:
        outfile.close()

def containsThumbnail(infile):
    """ Does any of the files in infile match one of THUMBNAIL_NAMES? """
    return len([f for f in infile.infolist() if f.orig_filename in THUMBNAIL_NAMES]) > 0
        
def replaceOriginalWithUncompressedWithoutThumb(name):
    infile_stats = os.stat(name)
    tmpname = name + ".tmp"
    hasThumbnail = False
    infile = zipfile.ZipFile(name, "r")
    try:
        hasThumbnail = containsThumbnail(infile)
        if hasThumbnail:
            LOG.info("Converting file with thumbnail %s" % name)
            createUncompressedCopyWithoutThumbnail(tmpname, infile)
        else:
            LOG.debug("Without thumbnail %s" % name)
    finally:
        infile.close()
    # Do this *after* we close infile, as weird things might happen under Windows otherwise.
    if hasThumbnail:
        replaceOriginalWithTmp(tmpname, name)
    # Reset atime and mtime, might now work under windows
    os.utime(name, (infile_stats.st_atime, infile_stats.st_mtime))

def addZippies(arg, dirname, fnames):
    """ Functor for collecting all these files with a ZIPped format. """
    for fname in fnames:
        if isZippy(fname):
            arg.append(os.path.join(dirname, fname))

def isZippy(fname):
    """ Returns True if fname is a zippy. """
    root, extension = os.path.splitext(fname)
    return extension in EXTENSIONS

def readFromStream(stream):
    """ Read lines from stream. """
    zippies = []
    for line in stream:
        fname = line.rstrip()
        if isZippy(fname):
            zippies.append(fname)
        else:
            LOG.debug("%s is not a zippy" % fname)
    return zippies

def replaceAllOriginalWithUncompressedWithoutThumb(zippies):
    """ Replaces uncompressed zippies with compressed. """
    for zippy in zippies:
        replaceOriginalWithUncompressedWithoutThumb(zippy)

def walkDirectory(directory):
    """ Walks the directory and returns zippies. """
    zippies = []
    os.path.walk(directory, addZippies, zippies)
    return zippies

def main(argv, stdin):
    """ Main. """
    logging.basicConfig()
    LOG.setLevel(logging.INFO)
    if "-d" in argv:
        LOG.setLevel(logging.DEBUG)
        argv.remove("-d")
    if argv[1] == "-":
        zippies = readFromStream(stdin)
    else:
        zippies = walkDirectory(argv[1])
    replaceAllOriginalWithUncompressedWithoutThumb(zippies)

if __name__ == "__main__":
    main(sys.argv, sys.stdin)

