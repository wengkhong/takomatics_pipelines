#!/usr/bin/python
import os.path
from subprocess import call
import subprocess
import csv
import shutil

#Get reference sequences
if not os.path.isfile("/home/ec2-user/ref/hs37d5.fa.gz"):
        command = "aws s3 cp s3://takomaticsdata/reference_genomes/hg19/ /home/ec2-user/ref --recursive --exclude \"*\" --include \"hs37d5*\""
        print(command)
        call(command, shell = True)


command = "docker pull wengkhong/speedseq-manual"
call(command, shell = True)
command = "docker pull wengkhong/vcflib"
call(command, shell = True)

class sample_run:
    def __init__(self, sample_name, sample_type, file1, file2):
        self.sample_type = sample_type
        self.file1 = file1
        self.file2 = file2
        self.sample_name = sample_name

def checkFileInS3(command):
        proc = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
        (out,err) = proc.communicate()
        #print out
        if out:
                return True;
        if not out:
                return False;

#Get sample list
call("aws s3 cp s3://takomaticsdata/Cedric_FEL/SampleSheet.csv . ", shell = True)
#Get target region
call("aws s3 cp s3://takomaticsdata/SureSelect_V5_plusUTRs_hs37d5.bed.tar.gz . ", shell = True)
call("tar xzvf SureSelect_V5_plusUTRs_hs37d5.bed.tar.gz", shell = True)
call("rm -f SureSelect_V5_plusUTRs_hs37d5.bed.tar.gz", shell = True)

with open('SampleSheet.csv','r') as tsv:
	sample_list = [line.strip().split(',') for line in tsv]

samples = {}
for line in sample_list:
    sample_name = line[0]
    sample_type = line[1]
    sample_file1 = line[2]
    sample_file2 = line[3]
    
    if(sample_file1 == "File1"):
        continue
    #print sample_name + "\t" + sample_type + "\t" + sample_file1 + "\t" + sample_file2

    myrun = sample_run(sample_name,sample_type, sample_file1, sample_file2)
    #samples[sample_name]["Tumor"]
    #print myrun.sample_name
    
    if sample_name in samples:
        #print "Already exists. Appending"
        samples[sample_name].append(myrun)
    else:
        samples[sample_name] = []
        samples[sample_name].append(myrun)    

#For each sample
for mykeys in samples:
    #print mykeys + " " + str(len(samples[mykeys]))
    for element in samples[mykeys]:
        print element.sample_type + " " + element.file1 + " " + element.file2
    #print samples[mykeys][1].sample_type
    #print mykeys + str(len(samples[mykeys]))
    
    normal_file1 = []
    normal_file2 = []
    tumor_file1  = []
    tumor_file2  = []

    for element in samples[mykeys]:
        if element.sample_type == "Normal":
            normal_file1.append(element.file1)
            normal_file2.append(element.file2)
        elif element.sample_type == "Tumor":
            tumor_file1.append(element.file1)
            tumor_file2.append(element.file2)


    for i in range(0,len(normal_file1)):
        print normal_file1[i]
        #print os.path.basename(normal_file1[i])
        command = "aws s3 cp s3://takomaticsdata/" + normal_file1[i] + " ."
        print command
        command = "aws s3 cp s3://takomaticsdata/" + normal_file2[i] + " ."
        print command

        command = "docker run --rm=true -v /home/ec2-user/:/home wengkhong/speedseq-manual code/speedseq/bin/speedseq align -o " + mykeys + " -R \"@RG\\tID:" + mykeys + "\\tSM:" + mykeys + "\\tLB:lib1\" -t32 -T /home/" + mykeys + "_temp -M 10 /home/ref/hs37d5.fa /home/" + os.path.basename(normal_file1[i]) + " /home/" + os.path.basename(normal_file2[i]) + " ; aws s3 cp . s3://takomaticsdata/Cedric_FEL/" + mykeys + "/ --recursive --exclude \"*\" --include \"" + mykeys + "*bam*\" --storage-class REDUCED_REDUNDANCY ; curl -s --user 'api:key-73ddfd4799ad4e0fc4e93db4aa1fce6c'     https://api.mailgun.net/v3/sandboxd9f4c585920d4834945e6f42a721fd1f.mailgun.org/messages     -F from='Mailgun Sandbox <postmaster@sandboxd9f4c585920d4834945e6f42a721fd1f.mailgun.org>'     -F to='Weng Khong Lim <wengkhong@gmail.com>'    -F subject='Hello Weng Khong Lim'     -F text='Align Done'"
        print command
        #Align,sort,dedup normal
        #If more than one normal, merge BAMs


    #Do same for tumor

    #Run strelka
    break    

