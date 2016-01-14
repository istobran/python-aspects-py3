import urllib
import aspects
import timeout_advice
import sys
import time

if len(sys.argv)<2:
    print "Usage: httpget URL [URL ...]"

aspects.wrap_around( urllib.URLopener.open,
                    timeout_advice.create_timeout_advice(1,1) )

for url in sys.argv[1:]:
    start_time = time.time()
    ufile = urllib.urlopen(url)
    elapsed_time = time.time() - start_time
    if ufile:
        print ufile.read()
        ufile.close
        sys.stderr.write(url + " arrived in " + str(elapsed_time) + " seconds\n")
    else:
        sys.stderr.write(url + " could not be retrieved, tried " + str(elapsed_time) + " seconds\n")
