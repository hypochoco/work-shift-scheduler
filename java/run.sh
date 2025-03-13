#!/bin/bash

########################################
############# CSCI 2951-O ##############
########################################
E_BADARGS=65
if [ $# -ne 1 ]
then
	echo "Usage: `basename $0` <input>"
	exit $E_BADARGS
fi
	
input=$1

# export the ilog license to run the solver
export ILOG_LICENSE_FILE=/local/projects/cplex/ilm/current/linux/access.site.ilm

# export the solver libraries into the path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/local/projects/cplex/CPLEX_Studio2211/cpoptimizer/bin/x86-64_linux:/local/projects/cplex/CPLEX_Studio2211/cplex/bin/x86-64_linux

# add the solver jar to the classpath and run
java -cp /local/projects/cplex/CPLEX_Studio2211/cpoptimizer/lib/ILOG.CP.jar:src solver.cp.Main $input
