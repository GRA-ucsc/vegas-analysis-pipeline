#Main script for the Very Independent VEGAS Analysis (VIVA)

import sys 
from plutils import *

def section():
	print('-'*25)

section()

print('VIVA starting-up!')
print('It\'s a great day for SCIENCE!')
print('Believe me, we will have the best SCIENCE!')

section()

print('Attempting to read in the instructions file...')
inst_filename = sys.argv[1]

try:
	f = open(inst_filename)
except OSError:
	print("Instructions file ", inst_filename, " could not be opened.")
	raise
else:
	f.close()

print('Reading instructions from {0}'.format(inst_filename))

section()

print('Building configuration dictionary...')
read_inst = instreader.InstFileReader(inst_filename)
configdict = read_inst.get_config_dict()
print ('Configuration Dictionary:\n', configdict)

section()

print('Establishing DB connection...')
dbcnx=database.DBConnection(configdict=configdict)
print('host = ', dbcnx.host)
print('db = ', dbcnx.db)
print('user = ', dbcnx.user)

section()

print('Initializing the run manager...')
rgm = runmanager.RunGroupManager(configdict,dbcnx)

section()		

print('Initalizing the analysis core...')


ac = analysis.AnalysisCore(configdict=configdict, runmanager=rgm)
print('Status = {0}'.format(ac.get_status()))

section()

print('Executing the analaysis...')
ac.execute()

section()

print('All done here!')
print('Even if I reported no errors, it is still reccomended to inspect the')
print('.error, .out, and .log files in the output directories.')
