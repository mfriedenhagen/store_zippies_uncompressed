import os
import sys
import zipfile

def replaceOriginalWithUncompressedWithoutThumb(name):
    infile = zipfile.ZipFile(name, "r")
    tmpname = name + ".tmp"
    try:
        outfile = zipfile.ZipFile(tmpname, "w", compression=zipfile.ZIP_STORED)
        try:
            for f in infile.infolist():
                if f.orig_filename != "Thumbnails/thumbnail.jpg":
                    outfile.writestr(f.orig_filename, infile.read(f.orig_filename))
        finally:
            outfile.close()
    finally:
        infile.close()
    os.rename(tmpname, name)

def addXmind(arg, dirname, fnames):
    for fname in fnames:
        if fname.endswith(".xmind"):
            arg.append(os.path.join(dirname, fname))
xminds = []
os.path.walk(sys.argv[1], addXmind, xminds)
for xmind in xminds:
    print xmind
    replaceOriginalWithUncompressedWithoutThumb(xmind)

