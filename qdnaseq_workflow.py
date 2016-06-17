#!/usr/bin/python
import os.path
from subprocess import call
import subprocess
import csv
import shutil
import sys, getopt
import getopt
import sys
import argparse
import glob

input_bamfile = '0315-0051-NHC-SNJ.bam'
sambamba_threads = 10
sambamba_fraction = 0.1
sambamba_path = '/data/public/tools/bin/'
rscript_path = '/home/gmslwkg/takomatics_pipelines'

parser = argparse.ArgumentParser()
parser.add_argument("input_bamfile", help="BAM file")
parser.add_argument("bins_path", help="Bins path")
parser.add_argument("-t","--threads", help = "Threads")
parser.add_argument("-f","--fraction", help = "Fraction")
args = parser.parse_args()

#print args.input_bamfile
input_bamfile = args.input_bamfile
bins_path = args.bins_path
if(args.threads):
    sambamba_threads = args.threads
if(args.fraction):
    sambamba_fraction = args.fraction

sample_name = os.path.splitext(input_bamfile)[0]
print "Currently processing " + sample_name
#Create folder
if not os.path.isdir(sample_name):
	os.mkdir(sample_name)
#Goto folder
os.chdir(sample_name)
#shutil.move("../" + input_bamfile, ".")

print "Subsampling BAM file"
command = sambamba_path + "sambamba view ../" + input_bamfile + " -o " + sample_name + ".subsampled.bam -fbam -t" + str(sambamba_threads) + " -s" + str(sambamba_fraction) + " -p" 
print "Command: " + command
call(command, shell = True)

command = "Rscript --vanilla " + rscript_path + "/qdnaseq_workflow.R " + sample_name + ".subsampled.bam " + bins_path
print "Command: " + command
call(command, shell = True)

#Consolidate segments using awk
command = "cut -f2-5 " + sample_name + ".subsampled_segments.tsv | awk '{if(d==$4 && $1==a){newend=$3}else if(NR>2){print a\"\t\"b\"\t\"newend\"\t\"d}; {a=$1;b=$2;c=$3;d=$4;}}' > " + sample_name + ".subsampled_combined_segments.tsv"
print "Command: " + command
call(command, shell = True)

#Delete subsampled BAM
os.remove(sample_name + ".subsampled.bam")
os.chdir('..')
quit()
