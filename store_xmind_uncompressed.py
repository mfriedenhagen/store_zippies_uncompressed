import os
import sys
import zipfile

def replaceOriginalWithUncompressedWithoutThumb(name):
    infile = zipfile.ZipFile(name, "r")
    tmpname = name + ".tmp"
    hasThumbnail = False
    try:
        outfile = zipfile.ZipFile(tmpname, "w", compression=zipfile.ZIP_STORED)
        try:
            for f in infile.infolist():
                if f.orig_filename != "Thumbnails/thumbnail.jpg":
                    outfile.writestr(f.orig_filename, infile.read(f.orig_filename))
                else:
                    hasThumbnail = True
        finally:
            outfile.close()
    finally:
        infile.close()
    if hasThumbnail:
        print("With thumbnail %s" % name)
        os.rename(tmpname, name)
    else:
        print("Without thumbnail %s" % name)
        os.unlink(tmpname)

def addXmind(arg, dirname, fnames):
    for fname in fnames:
        if fname.endswith(".xmind"):
            arg.append(os.path.join(dirname, fname))
xminds = []
os.path.walk(sys.argv[1], addXmind, xminds)
for xmind in xminds:
    print xmind
    replaceOriginalWithUncompressedWithoutThumb(xmind)

