#This module contains the classes for managing the processing of a runlist through a stage of vegas

import subprocess
import os
import re
import time
#from . import config_writer
from . import condor

#Base class consisting of the shared methods of the VEGAS analysis stages.
class VAStage:
			
	def is_condor_enabled(self):
		
		if 'USECONDOR' in stgconfigdict.keys():
			if stgconfigdict.get('USECONDOR') in ['1','True', 'true']:
				self.usecondor = True
		elif 'USECONDOR' in gconfigdict.get('GLOBALCONFIG').keys():
			if gconfigdict.get('GLOBALCONFIG').get('USECONDOR') in ['1', 'True', 'true']:
				self.usecondor = True
		else
			self.usecondor = False
		return self.usecondor

	#Loop over the rungroup and write the condor submission files
	def write_condor_files(self):
		
		juniverse='vanilla'
		jexecutable='vaStage' + self.stage
		jrequirments=''
				
		self.jobs = {}  
		for run in self.runlist.keys():
			jsubid = run
			jarguments = self.get_arguments_str(run)
			jlog = self.outputdir + '/' + 'condor_' + run + '.log'	
			jout = self.outputdir + '/' + 'condor_' + run + '.out'
			jerror = self.outputdir + '/' + 'condor_' + run + '.error'
			cj = CondorJob(executable=jexectutable, universe=juniverse, requirments=jrequirments, arguments=jarguments, log=jlog, error=jerror, out=jout, subid=jsubid)
			self.jobs.update({run : cj})		
	
	def execute(self):
		if is_condor_enabled():
			for run, job in self.jobs.items()
				if self.use_existing == True:
					if self.existing_output.get(run) == True:
						#A file for this run already exist in the output directory
						job.status = 'succeeded'
                                                job.existstatus = '0'						
					else:
						job.execute()
		else:
			raise JobExecError('I don\'t know how to exectute properly without using condor yet...')	
	
	#Defined for each stage individually
	def get_arguments_str(self,run):
		return ''
	
	def update_status(self):
		n_submitted=0
		n_executing=0
		n_terminated=0
		n_failed=0
		for run in self.jobs.keys():
			jstatus=self.jobs(run).get_status()
			if jstatus == 'submitted':
				n_submitted = nsubmitted + 1
			elif jstatus == 'executing':
				n_executing = n_executing + 1
			elif jstatus == 'terminated':
				n_terminated = n_terminated + 1
				jexiststatus = self.jobs(run).exitstatus
				if jexiststatus != '0'
					n_failed = n_failed + 1
		#Abort processing this run group if one of the runs fails	
		if n_failed > 0:
			print('Error occured while running analysis for ', stgconfigkey, '. This analysis has been aborted.')
			self.kill()
			self.status = 'failed'
		elif n_terminated == len(self.jobs.keys()):
			self.status = 'succeeded'
		elif n_executing > 0:
			self.status = 'executing'
		elif n_submitted > 0:
			self.status = 'submitted'
		

	def get_status(self):
		self.update_status()
		return self.status

	def is_working(self):
		if self.status in ['initialized', 'executing', 'submitted']:
			return True
		else:
			return False

	def kill(self):
		if self.usecondor:
			for run in self.jobs.keys():
				self.jobs(run).kill()
		else:	
			raise JobExecError('I don\'t know how to exectute properly without using condor yet...')
	
	#copies root files from the input directory to the outputdirectory. This is needed as some stages modify an existing file rather than creating a new one
	def copy_input_to_output(self):
		copyprocs = []
		file_pat = re.compile('([0-9]+)([.]*.*[.])root')
		for dir in self.inputdirs:
			for file in os.listdir(dir):
				m = file_pat.match(file)
					if m != None :
					#Only the copy the files if they appear in the runlist for this stage
					if m.match(1) in self.runlist.keys():
						oldfile = dir + '/' + m.group()
						newfile = self.outputdir + '/' + m.group(1) + 'stg' + self.stage + '.root'
						proc = subprocess.Popen(['cp', oldfile, newfile])
						copyprocs.append(proc)
		#Ensure we wait for all the copying jobs to finish
		is_copying=True
		while(is_copying):
			poll_results = []
			for p in copyprocs:
				poll_results.append(p.poll())
			if not None in poll_results:
				is_copying = False
			else:
				time.sleep(0.25)

	#returns the path to the file for a specific run. Searchs directories in the list dirs.
	#Setting the ddate_dir argument to True will a append a prefix directory of the form dyyyymmdd to the search path 
	def get_file(self, run, filetype, dirs, ddate_dir=False):
		
		filename=None
		file_pat = re.compile(run + '([.]*.*[.])' + filetype
		
		for dir in dirs:
			#append the ddata directory if necessary
			if ddate_dir == True:
				dir = dir + '/' + self.runlist(run).ddate

			files = os.listdir(dir)
			for file in files:
				m = file_pat.match(file)
				if m != None:
					filename = dir + '/' + file
		return filename
				
		
		

	#Check the input directorys for a file associated with a run
	def check_for_input(self, filetype, inputdirs, ddate_dir=False):
										
		for run in self.runlist.keys():
			file = self.get_file(run,filetype,ddate_dir)
			if file == None:
				err_str = 'input ' + filetype + ' file could not be found for run ' + run
				raise InputFileError(err_str)

		return True #No errors raised

	#check whether to us existing output root files. Overwrite old files by default.
	def use_existing_output(self)

		use_existing = False
		
		if 'USEEXISTINGOUTPUT' in self.gconfigdict.get(self.stgconfigkey).keys():
			if self.gconfigdict.get(self.stgconfigkey).get('USEEXISTINGOUTPUT').lower() in ['true', '1', 'totally']
				use_existing = True
		elif 'USEEXISTINGOUTPUT' in self.gconfigdict.get('GLOBALCONFIG').keys():
			if self.gconfigdict.get('GLOBALCONFIG').get('USEEXISTINGOUTPUT').lower() in ['true', '1', 'totally']
                                use_existing = True
		
		return use_existing
	
	#Check the output directory to determine what runs have an existing output root file.
	def anl_existing_output(self):
		has_existing = {}
		for run in self.runlist.keys():
			file = self.get_file(run,filetype,[self.outputdir])
			if file != None:
				has_existing.update({run, True})
			else:
				has_existing.update({run, False})
		return has_existing
		
	#Cleans up files produced by this stage based on the contents of the clean_opts list.						
	def clean_up(self, clean_opts):
		for co in clean_opts:
			if co.lower() == 'all':
				subprocess.run(['rm','-r', self.outputdir])
                        else:
				outfile_pat = re.compile('[0-9]+[.]*.*[.]root')
				logfile_pat = re.compile('.*[.](log|err|out|sub)')                 
                                if co.lower() == 'output':
					for file in os.listdir(self.outputdir):
						m = outfile_pat.match(file)
						if m != None:
							path_to_file = self.outputdir + '/' + file
							subprocess.run(['rm', path_to_file])
						
                                elif co.lower() == 'output_bad':
					for run in stg.runlist.keys()
						if stg.jobs.get(run).existstatus != '0':
							file = get_file(run,'root',[self.outputdir])
							subprocess.run(['rm', file])
                                                                
                                if co.lower() == 'logs':
					for file in os.listdir(self.outputdir)
						m = logfile_pat.match(file)
						if m != None
							path_to_file = self.outputdir + '/' + self.outputdir
							subprocess.run(['rm', path_to_file])
					
                                elif co.lower() == 'logs_bad':
					for run in stg.runlist.key():
						if stg.jobs(run).existstatus != '0':
							run_logfile_pat = re.compile('.*' + run + '[.](log|err|out|sub)')
							for file in os.listdir(self.outputdir):
								m = run_logfile_pat.match(file)
								if m != None:
									path_to_file = self.outputdir + '/' + file
									subprocess.run(['rm', path_to_file])
						
	
#Standard stage 1 analysis 
class VAStage1(VAStage):

	self.stage = '1'

	def __init__(self, **kwargs):
      
                self.rungroups=kwargs.get('rungroups')
		self.grouptag=kwargs.get('grouptag')
                self.gconfigdict=kwargs.get('configdict')
                self.inputdirs=kwargs.get('inputdirs')
		self.outputdir=kwargs.get('outputdir')
                
		if grouptag != '':
                	self.stgconfigkey='VASTAGE' + str(self.stage) + ':' + self.grouptag
		else
			self.stgconfigkey='VASTAGE' + str(self.stage)
                 
		self.use_existing = self.use_existing_output()
				
		#for stage 1, we need to create a combined run list with both calibration and data runs
		
		self.runlist = {}
		for k, rg in self.rungroups.items():
			self.runlist.update(rg.dataruns)
			self.runlist.update(rg.calibruns)
		
		self.existing_output = self.anl_existing_output()
		self.use_existing = self.use_existing_output()
		
		#Check that the input files exist
                self.check_for_input('cvbf', self.inputdirs, True)

                #write config and cut files
                #cw = config_writer.config_writer(self.stgconfigdict,self.outputdir)
                #self.config=get_config_filename()

                #write condor files (if condor enables)
		if self.is_condor_enabled():
			self.write_condor_files()

                self.status='initialized'

	def get_arguments_str(self,run):
		arg_str = ''
    			
			arg_str = arg_str + "-Stage1_DBHost=" + gconfigdict.get('GLOBALCONFIG').get('DBHOSTNAME')
			if self.runlist(run).type == 'calib':
				arg_str = arg_str + " -Stage1_RunMode=" + "flasher"
			else:
				arg_str = arg_str + " -Stage1_RunMode=" + "data"
			
			arg_str = arg_str + " -config=" + self.configfile			
			
			rawdir = gconfigdict.get('GLOBALCONFIG').get('RAWDATADIR') + '/' + self.runlist(run).ddate
			#Check for the file in the raw data directory
			pattern=re.compile(run + '*.cvbf')
			file_exist=False
			for file in os.listdir(rawdir):
				m = pattern.match(file)
				if(m != None):
					inputfile = m.group()
					file_exist = True
					break
			if not file_exist:
				err_str = 'Could not find a raw data file for run ' + run + ' in input directory ' + rawdir
				raise InputFileError(err_str)
			
			arg_str = arg_str + " " + rawdir + "/" + inputfile
			arg_str = arg_str + " " + self.outputdir + "/" + run + '.stg1.root'
			
		return arg_str

class VAStage2(VAStage):

	self.stage='2'

	def __init__(self,*args,**kwargs):
               
		self.rungroups=kwargs.get('rungroups')
                self.grouptag=kwargs.get('grouptag')
                self.gconfigdict=kwargs.get('configdict')
                self.inputdirs=kwargs.get('inputdirs')
                self.outputdir=kwargs.get('outputdir')

                if grouptag != '':
                        self.stgconfigkey='VASTAGE' + str(self.stage) + ':' + self.grouptag
                else
                        self.stgconfigkey='VASTAGE' + str(self.stage)
 
                self.runlist = {}
		for k, rg in self.rungroups.items():
			runlist.update(rg.dataruns)
		
		self.existing_output = self.anl_existing_output()
                self.use_existing = self.use_existing_output()
	
		#Check that the input files exist
		self.check_for_input('cvbf', self.gconfigdict.get('GLOBALCONFIG').get('RAWDATADIR'), True)
		self.check_for_input('root', self.inputdirs)
		
		self.copy_input_to_output()
		
                #write config and cut files
                #cw = config_writer.config_writer(self.stgconfigdict,self.outputdir)
                #self.config=get_config_filename()

                #write condor files (if condor enables)
                if self.is_condor_enabled():
                        self.write_condor_files()

                self.status='initialized'
	
	def get_arguments_str(self, run):
		arg_str = ''
		arg_str = arg_str + '-config='+self.config
		
		rawdatafile = get_file(run, 'cvbf', self.gconfigdict.get('GLOBALCONFIG').get('RAWDATADIR'), True)
		calibfile = get_file(self.runlist.get(run).calib, 'root', self.inputdirs)
		#Recall that stage 1 file has been copied into the data directory
		datafile = get_file(run, '.root', self.outputdir)

		arg_str = arg_str + ' ' + rawdatafile + ' ' + datafile + ' ' + calibfile
		
		return arg_str

class VAStage4(VAStage):

	self.stage='4.2'

	def __init__(self, **kwargs):
		
		self.rungroups=kwargs.get('rungroups')
                self.grouptag=kwargs.get('grouptag')
                self.gconfigdict=kwargs.get('configdict')
                self.inputdirs=kwargs.get('inputdirs')
                self.outputdir=kwargs.get('outputdir')

                if grouptag != '':
                        self.stgconfigkey='VASTAGE' + str(self.stage) + ':' + self.grouptag
                else
                        self.stgconfigkey='VASTAGE' + str(self.stage)

		self.use_existing = self.use_existing_output()		

                self.runlist = {}
		for k, rg in rungroups.items():
			self.runlist.update(rg.dataruns)

                #Check that the input files exist
                self.check_for_input('root', self.inputdirs)
		
		self.existing_output = self.anl_existing_output()
                self.use_existing = self.use_existing_output()

		self.copy_input_to_output()

                #write config and cut files
                #cw = config_writer.config_writer(self.stgconfigdict,self.outputdir)
                #self.cuts=cw.get_cuts_filename()
                #self.config=get_config_filename()

                #write condor files (if condor enables)
                if self.is_condor_enabled():
                        self.write_condor_files()

                self.status='initialized'
	
	def get_arguments_str(self, run):
		arg_str = ''
		arg_str = arg_str + '-config=' + self.config
		arg_str = arg_str + ' -cuts=' + self.cuts
		
		datafile = get_file(run, 'root', self.outputdir)
		arg_str = arg_str + ' ' + datafile
		
		return arg_str

class VAStage5(VAStage):
	
	self.stage='5'

	def __init__(self, **kwargs):

		self.rungroups=kwargs.get('rungroups')
                self.grouptag=kwargs.get('grouptag')
                self.gconfigdict=kwargs.get('configdict')
                self.inputdirs=kwargs.get('inputdirs')
                self.outputdir=kwargs.get('outputdir')

                if grouptag != '':
                        self.stgconfigkey='VASTAGE' + str(self.stage) + ':' + self.grouptag
                else
                        self.stgconfigkey='VASTAGE' + str(self.stage)

		self.use_existing = self.use_existing_output()

                self.runlist = {}
		for k, rg in rungroups.items():
			self.runlist.update(rg.dataruns)

		self.existing_output = self.anl_existing_output()
                self.use_existing = self.use_existing_output()		

                #Check that the input files exist
                self.check_for_input('root', self.inputdirs)

                #write config and cut files
                #cw = config_writer.config_writer(self.stgconfigdict,self.outputdir)
                #self.cuts=cw.get_cuts_filename()
                #self.config=get_config_filename()

                #write condor files (if condor enables)
                if self.is_condor_enabled():
                        self.write_condor_files()

                self.status='initialized'


	def get_arguments_str(self, run)
		arg_str = ' '
		arg_str = arg_str + '-config=' + self.config
		arg_str = arg_str + ' -cuts=' + self.cuts
		
		#time cuts
		timecut_str = self.runlist.get(run).timecuts
		arg_str = arg_str + ' -ES_CutTimes=' + timecut_str		

		stg4file = get_file(run, 'root', self.inputdirs)
		stg5file = self.outputdir + '/' + run + '.stg5.root'
		
		arg_str = arg_str + ' -inputFile ' + stg4file
		arg_str = arg_str + ' -outputFile ' + stg5file

		return arg_str

class VAStage6(VAStage):
	
	self.stage='6'

	def __init__(self, **kwargs):

		self.rungroups=kwargs.get('rungroups')
                self.grouptag=kwargs.get('grouptag')
                self.gconfigdict=kwargs.get('configdict')
                self.inputdirs=kwargs.get('inputdirs')
                self.outputdir=kwargs.get('outputdir')

                if grouptag != '':
                        self.stgconfigkey='VASTAGE' + str(self.stage) + ':' + self.grouptag
                else
                        self.stgconfigkey='VASTAGE' + str(self.stage)

                #Check that the input files exist
                self.check_for_input('root', self.inputdirs)

		self.stg6_group_config()
		self.write_stg6_runlist()

                #write config and cut files
                #cw = config_writer.config_writer(self.stgconfigdict,self.outputdir)
                #self.cuts=cw.get_cuts_filename()
                #self.config=get_config_filename()

                #write condor files (if condor enables)
                if self.is_condor_enabled():
                        self.write_condor_files()

                self.status='initialized'

	def get_arguments_str(self):

		arg_str = ''
		arg_str = arg_str + '-S6A_OutputFileName=' + self.outputdir + '/' + 'results_stg6'
		arg_str = arg_str + ' -S6A_ConfigDir=' + self.outputdir
		arg_str = arg_str + ' -S6A_Batch=1'
		arg_str = arg_str + ' -cuts=' + self.cuts 
		arg_str = arg_str + ' -config=' + self.config
		arg_str = arg_str + ' ' + self.stg6_rlfilename

		return arg_str
	
	#Writes the runlist for stage6
	#The file format follows the specifications found at https://veritas.sao.arizona.edu/OAWGwiki/index.php/Vegas_v2_5_newRunStyle	
	def write_stg6_runlist(self):

		self.stg6_rlfilename = self.outputdir + '/' + 'runlist_stg6.txt'
		
		with open(self.stg6_rlfilename) as rl:
			for gidx, group in enumerate(self.rungroups.keys()):

				if gidx != 0:
					rl.write('[RUNLIST ID: ' + gidx + ']\n')

				for ridx, run in enumerate(self.rungroups.get(group).dataruns):
					stg5file = self.get_file(run, 'root', self.inputdirs)
					rl.write(self.inputdir + '/' + stg5file + '\n')

				if gidx !=0:
					rl.write('/RUNLIST ID: ' + gidx + ']\n')
				
				rl.write('[EA ID: ' + gidx + ']\n')
				rl.write(self.ea_dict.get(group) + '\n')
				rl.write('[/EA ID: ' + gidx + ']\n')
				
				rl.write('[CONFIG ID: ' + gidx + ']\n')
				for opt in self.group_config.get(group):
					rl.write(opt + '\n')
				rl.write('[/CONFIG ID: ' + gidx + ']\n')			

	#determine the the configuration and effective area to be used for each rungroup in stage 6
	def stg6_group_config(self):
		self.group_config = {}
		self.ea_dict = {}		
		for group in self.rungroups.keys():
			config_list = []
			for k, v in self.stgconfigdict.items():
				if group == k.partition(':')[2]:
					opt = k.partition(':')[0]
					if opt == 'EA':
						self.ea_dict.update({group : v})
					else:
						config_list.append(opt + ' ' + v)
			self.group_config.update({group : config_list})
	
	#Need only one submit file needed for stage6
	def write_condor_files(self):

                juniverse='vanilla'
                jexecutable='vaStage' + self.stage
                jrequirments=''

		self.jobs = {}

                jsubid = ''
                jarguments = self.get_arguments_str()
                jlog = self.outputdir + '/' + 'condor_' + self.stage + '.log'
                jout = self.outputdir + '/' + 'condor_' + self.stage + '.out'
                jerror = self.outputdir + '/' + 'condor_' + self.stage + '.error'

                cj = CondorJob(executable=jexectutable, universe=juniverse, requirments=jrequirments, arguments=jarguments, log=jlog, error=jerror, out=jout, subid=jsubid)
		self.jobs.update({'stg6' : cj})
						
		
class InputFileError(Exception):
	pass
				
class JobExecError(Exception):
	pass			