import sys
sys.path.insert(0, 'src')

import utils as util
import settings as ENV

startTime = datetime.datetime.now()



endTime = datetime.datetime.now()
timeSpent = endTime - startTime
print "PROGRAM COMPLETED IN " + str(timeSpent.seconds) + " SECONDS\n\n\n--------------------------\n\n\n"