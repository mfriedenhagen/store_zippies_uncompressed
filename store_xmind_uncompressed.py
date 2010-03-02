import os
import sys
import zipfile

def replaceOriginalWithUncompressedWithoutThumb(name, thumbnailName = "Thumbnails/thumbnail.jpg"):
    infile = zipfile.ZipFile(name, "r")
    tmpname = name + ".tmp"
    try:
        hasThumbnail = len([f for f in infile.infolist() if f.orig_filename == thumbnailName]) > 0
        if hasThumbnail:
            outfile = zipfile.ZipFile(tmpname, "w", compression=zipfile.ZIP_STORED)
            try:
                for f in infile.infolist():
                    if f.orig_filename != thumbnailName:
                        outfile.writestr(f.orig_filename, infile.read(f.orig_filename))
                    else:
                        hasThumbnail = True
            finally:
                outfile.close()
            print("With thumbnail %s" % name)
            os.rename(tmpname, name)
        else:
            print("Without thumbnail %s" % name)
    finally:
        infile.close()

def addXmind(arg, dirname, fnames):
    for fname in fnames:
        if fname.endswith(".xmind"):
            arg.append(os.path.join(dirname, fname))
xminds = []
os.path.walk(sys.argv[1], addXmind, xminds)
for xmind in xminds:
    replaceOriginalWithUncompressedWithoutThumb(xmind)

