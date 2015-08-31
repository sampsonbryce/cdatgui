from application import CDATGUIApp
import utils


def script_run(file, canvas):
    import sys
    import os.path
    fname = os.path.basename(file)
    f, _ = os.path.splitext(fname)
    pngname = f + ".png"
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg in ("-i", "--interact"):
                canvas.interact()
                sys.exit()
            if arg in ("-h", "--help"):
                print "Usage: python %s (-i|--interact) (-h|--help)" % fname
                print "    -i | --interact: Starts vis in interact mode"
                print "    -h | --help: Displays this help text"
                print "    No args: Renders to %s" % pngname
                sys.exit()
    canvas.png(pngname)
