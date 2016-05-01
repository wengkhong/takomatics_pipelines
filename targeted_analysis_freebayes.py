#!/usr/bin/python
import os.path
from subprocess import call
import subprocess
import csv
import shutil
import sys, getopt
import getopt
import sys

sample_list_path = 's3://takomaticsdata/targeted_dev_sample_files/GS_Samples_Short.csv'
target_region_path = 's3://takomaticsdata/targeted_dev_sample_files/GS_Panel_Sorted_Merged.bed'
parent_path = os.path.dirname(sample_list_path)

#Get instance id
current_instance_id = call("wget -q -O - http://instance-data/latest/meta-data/instance-id", shell = True)

min_depth = 20
min_qual  = 30
num_cores = 16
sambamba_mem = 10
qualimap_mem = '4G'
opt_list = sys.argv[1:]
#If no sysarg apart from filename, will fail
try:
    opts, args = getopt.getopt(opt_list,"sqdtm",["sambamba_mem", "num_cores", "shutdown", "min_qual", "min_depth","qualimap_mem"])
except getopt.GetoptError:
    print 'Bad inputs'
    quit()    

shutdown_flag = False
for opt, arg in opts:
    if opt in ("-s", "--shutdown"):
        shutdown_flag = True
    elif opt in ("-q", "--min_qual"):
        min_qual = arg
    elif opt in ("-d", "--min_depth"):
        min_depth = arg
    elif opt in ("-t", "--num_cores"):
        num_cores = arg
    elif opt in ("-m", "--sambamba_mem"):
        sambamba_mem = arg
    elif opt in ("--qualimap_mem"):
        qualimap_mem = arg

#Get reference sequences
if not os.path.isfile("/home/ec2-user/ref/hs37d5.fa.gz"):
	command = "aws s3 cp s3://takomaticsdata/reference_genomes/hg19/ /home/ec2-user/ref --recursive --exclude \"*\" --include \"hs37d5*\""
	print(command)
	call(command, shell = True)

command = "docker pull wengkhong/speedseq"
call(command, shell = True)
command = "docker pull wengkhong/vcflib"
call(command, shell = True)

#Get Boto3. This is not currently in use but may be in the future
call("sudo pip install boto3", shell = True)
import boto3

#Look for qualimap. If it's not there then download and unpack
if(os.path.isfile('/home/ec2-user/qualimap_v2.2/qualimap')):
    print("AOK")
else:
    call("wget https://bitbucket.org/kokonech/qualimap/downloads/qualimap_v2.2.zip", shell = True)
    call("unzip qualimap_v2.2.zip", shell = True)

#Get sample list and target region
call("aws s3 cp " + sample_list_path + " .", shell = True)
call("aws s3 cp " + target_region_path + " .", shell = True)
with open(os.path.basename(sample_list_path), 'r') as csv:
	sample_list = [line.strip().split(',') for line in csv]

print("Length of sample list: " + str(len(sample_list)-1))

#This is a helper function to check if a file already exists in S3 or not. Primarily used to avoid reprocessing when resuming from incomplete runs
def checkFileInS3(command):
	proc = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
        (out,err) = proc.communicate()
        #print out
        if out:
		return True;
        if not out:
		return False;


for line in sample_list:
	file1 = str(line[0])
	file2 = str(line[1])
	sample_name = str(line[2])
	if file1 == "File1":
		continue
	#Check if output for this sample already exists. Skip if so
        command = "aws s3 ls " + parent_path + "/" + sample_name + "/" + sample_name + ".vcf"
	if(checkFileInS3(command)):
		print "Sample " + sample_name + " already done. Skipping"
		continue
	############################################################
	print "Currently processing " + sample_name
	#Create folder
        if not os.path.isdir(sample_name):
            os.mkdir(sample_name)
            
	#Goto folder
        os.chdir(sample_name)
        
        #Get fastq files
        print "Getting fastq files"
        command = "aws s3 cp " + file1 + " ."
        call(command, shell = True)
        command = "aws s3 cp " + file2 + " ."
        call(command, shell = True)
	
        #Align and call variants
        print "Aligning for " + sample_name
        command = "docker run --rm=true -v /home/ec2-user:/home wengkhong/speedseq code/speedseq/bin/speedseq align -o /home/" + sample_name + "/" + sample_name + " -R \"@RG\\tID:" + sample_name + "\\tSM:" + sample_name + "\\tLB:lib1\" -t" + str(num_cores) + " -T /home/" + sample_name + "/" + sample_name + "_temp -M " + str(sambamba_mem) + " /home/ref/hs37d5.fa /home/" + sample_name + "/" + os.path.basename(file1) + " /home/" + sample_name + "/" + os.path.basename(file2)
        print command
        call(command, shell = True)
        #exit()
        
        print "Calling variants for " + sample_name
        command = "docker run --rm=true -v /home/ec2-user:/home wengkhong/freebayes freebayes -f /home/ref/hs37d5.fa -b /home/" + sample_name + "/" + sample_name + ".bam -v /home/" + sample_name + "/" + sample_name + ".vcf --target /home/" + os.path.basename(target_region_path)
        print command
        call(command, shell = True)
        #exit()
        
        print "Filtering variants for " + sample_name
        command = "docker run -it --rm=true -v /home/ec2-user/:/home wengkhong/vcflib vcflib/bin/vcffilter -f 'DP >" + str(min_depth - 1) + " & QUAL > " + str(min_qual - 1) + "' /home/" + sample_name + "/" + sample_name + ".vcf > " + sample_name + ".filtered.vcf"
        print command
        call(command, shell = True)
            
        print "Getting variants in target region"
        command = "docker run --rm=true -v /home/ec2-user:/home wengkhong/vcflib bedtools intersect -a /home/" + sample_name + "/" + sample_name + ".filtered.vcf -b /home/" + os.path.basename(target_region_path) + " > " + sample_name + ".filtered.target.vcf"
        print command
        call(command, shell = True)

        #Add sample name to VCF
        vcf_filename = sample_name + ".filtered.target.vcf"
        rename_command = "awk 'BEGIN {OFS=\"\\t\"} {FS=\"\\t\"} {$7=\"" + sample_name + "\";print}' " + vcf_filename + " > " + sample_name + ".filtered.target.name.vcf"
        print rename_command
        call(rename_command, shell = True)

        #Run qualimap
        print "Running qualimap"
        #First, create 6 column BED file
        command = "awk -v OFS='\t' '{print $1,$2,$3,\".\",\".\",\".\"}' ~/" + os.path.basename(target_region_path) + " > ~/bed6.txt"
        print command
        call(command, shell = True)
        command = "~/qualimap_v2.2/qualimap bamqc -nt " + str(num_cores) + " --java-mem-size=" + qualimap_mem + " -bam ~/" + sample_name + "/" + sample_name + ".bam -gff ~/bed6.txt -c"
        print command
        call(command, shell = True)

	#Upload results
        print "Uploading results for " + sample_name
        command = " aws s3 cp . " + parent_path + "/" + sample_name + " --recursive --exclude \"*discordants*\" --exclude \"*splitters*\" --exclude \"*fq.gz\" --exclude \"*fastq*\""
        call(command, shell = True)
	#Delete folder
        os.chdir('..')
        print "Cleaning up folder for " + sample_name
        shutil.rmtree(sample_name)
        #break
        #quit()

if(shutdown_flag):
    call("sudo shutdown -h now", shell = True)
