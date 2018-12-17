from bash_command import bash_command as bc
import shlex
import numpy as np
import sys

import dateutil.parser
from datetime import datetime

i=0
latest=''
while ():
	out=bc.bash_command('ls -lat 1*dat --time-style=full-iso')
	out=out.split('\n')
	out=[row.split(' ') for row in out][:-1]
	out=np.array(out)
	try:
		latest=out[0][-1]
	except IndexError:
		continue
	out=[dateutil.parser.parse(row[-4]+' '+row[-3]) for row in out]
	print latest
	if latest=='1000500.dat':
		break
	delta_t=(datetime.now()-out[0]).seconds
	if (delta_t>60):
		try:
			job=shlex.split(bc.bash_command('squeue -u alge9397 -t running|grep -i gpu'))[0]
			bc.bash_command('scancel {0}'.format(job))	
		except IndexError:
			pass
		##Using higpus built-in restart capability
		bc.bash_command('cat run_aleksey_sim_restart_template.sh | sed s/xx/{0}/g >run_aleksey_sim_restart.sh'.format(latest))
		bc.bash_command('sbatch run_aleksey_sim_restart.sh')

		##For cold restart
		# bc.bash_command('mkdir run_{0}'.format(i))
		# bc.bash_command('mv init_disk run_{0}'.format(i))
		# bc.bash_command('cp {0} init_disk'.format(latest))
		# bc.bash_command('mv *dat run_{0}'.format(i))
		# bc.bash_command('sbatch run_aleksey_sim_0.sh')

		i+=1
	
		bc.bash_command('sleep 60')
	bc.bash_command('sleep 10')
