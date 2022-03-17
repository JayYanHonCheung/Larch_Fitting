#!/bin/bash -l   
#$ -S /bin/bash   
# Set wallclock time (format hours:minutes:seconds) 
#$ -l h_rt=72:00:00 
# Select the name of the job. 
#$ -N   Test_run
# Enter the email for job notification. 
#$ -M sai.yadavalli.18@ucl.ac.uk  
# Set the working directory to the current one. 
#$ -cwd 
 
WORKDIR=$SGE_O_WORKDIR 

# Loading python module
module load python3/recommended

# Changing to the directory where the submission file is located
cd $WORKDIR

# Printing the start date and time
var=`date`
echo "The start date and time"
echo "$var"

#Calling the python file to be executed 
/lustre/scratch/scratch/ucecssy/KMC_becnhamrk_simulation/python_script/Sample.py > Output.txt
 

# printing the end date and time
var=`date`
echo "The end date and time"
echo "$var"
