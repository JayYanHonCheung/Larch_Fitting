#!/bin/bash -l   
#$ -S /bin/bash   
# Set wallclock time (format hours:minutes:seconds) 
#$ -l h_rt=72:00:00 
# Select the name of the job. 
#$ -N exafs_multifit_101
# Enter the email for job notification. 
#$ -M jay.yan.15@ucl.ac.uk  
# Set the working directory to the current one. 
#$ -cwd 
 
WORKDIR=$SGE_O_WORKDIR 

# Activate virtual environment with xraylarch
module load python/3.8.6
source xraylarch/bin/activate

# Changing to the directory where the submission file is located
cd $WORKDIR

# Printing the start date and time
var=`date`
echo "The start date and time"
echo "$var"

#Calling the python file to be executed 
/lustre/home/zcechcy/python/exafs_fttings_101.py
 

# printing the end date and time
var=`date`
echo "The end date and time"
echo "$var"
