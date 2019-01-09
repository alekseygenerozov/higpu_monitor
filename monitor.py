from bash_command import bash_command as bc
import shlex
import numpy as np
import sys

import dateutil.parser
from datetime import datetime
import os

i=0
latest=''
tmax=2*3600
orb=500
end=str(1000000+orb)+'.dat'


for i in range(4, 6):
	t0=datetime.now()
	os.chdir('trial_{0}'.format(i))
	x=bc.bash_command('pwd')
	print x
	sys.stdout.flush()
	##Time limit of tmax (2 hours) for each trial
	while ((datetime.now()-t0).seconds<tmax):
		out=bc.bash_command('ls -lat 1*dat --time-style=full-iso')
		out=out.split('\n')
		out=[row.split(' ') for row in out][:-1]
		out=np.array(out)
		##Check how much time has passed since the last output file.
		try:
			latest=out[0][-1]
			out=[dateutil.parser.parse(row[-4]+' '+row[-3]) for row in out]
			##Stop if job has been completed
			if latest==end:
				break
			delta_t=(datetime.now()-out[0]).seconds
		##If there are no output files--submit the job and wait until we have produced an output file
		except IndexError:
			bc.bash_command('sbatch run_aleksey_sim_0.sh')
			out=bc.bash_command('ls -lat 1*dat --time-style=full-iso')
			while len(out)==0:
				out=bc.bash_command('ls -lat 1*dat --time-style=full-iso')
			delta_t=0

		if (delta_t>60):
			##Cancel job if running
			try:
				job=shlex.split(bc.bash_command('squeue -u alge9397 -t running|grep -i gpu'))[0]
				bc.bash_command('scancel {0}'.format(job))	
			except IndexError:
				pass
			##Using higpus built-in restart capability
			bc.bash_command('cat run_aleksey_sim_restart_template.sh | sed s/xx/{1}/g > run_aleksey_sim_restart.sh'.format(i, latest))
			bc.bash_command('sbatch run_aleksey_sim_restart.sh')

			#Wait until job has left the queue so we don't end up submitting a bunch of repeat jobs to the queue 
			job=shlex.split(bc.bash_command('squeue -u alge9397 -t running|grep -i gpu'))
			while (len(job)==0):
				job=shlex.split(bc.bash_command('squeue -u alge9397 -t running|grep -i gpu'))


			##For cold restart
			# bc.bash_command('mkdir run_{0}'.format(i))
			# bc.bash_command('mv init_disk run_{0}'.format(i))
			# bc.bash_command('cp {0} init_disk'.format(latest))
			# bc.bash_command('mv *dat run_{0}'.format(i))
			# bc.bash_command('sbatch run_aleksey_sim_0.sh')

			i+=1
			##Is it necessary to set script to sleep here?
			bc.bash_command('sleep 60')
		bc.bash_command('sleep 10')
	os.chdir('..')