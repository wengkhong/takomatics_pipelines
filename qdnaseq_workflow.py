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

input_bamfile = '0315-0051-NHC-SNJ.bam'
sambamba_threads = 10
sambamba_fraction = 0.1
sambamba_path = '/data/public/tools/bin/'

parser = argparse.ArgumentParser()
parser.add_argument("input_bamfile", help="BAM file")
parser.add_argument("-t","--threads", help = "Threads")
parser.add_argument("-f","--fraction", help = "Fraction")
args = parser.parse_args()

#print args.input_bamfile
input_bamfile = args.input_bamfile
if(args.threads):
    sambamba_threads = args.threads
if(args.fraction):
    sambamba_fraction = args.fraction

print "Subsampling BAM file"
command = sambamba_path + "sambamba view " + input_bamfile + " -o " + os.path.splitext(input_bamfile)[0] + ".subsampled.bam -fbam -t" + str(sambamba_threads) + " -s" + str(sambamba_fraction) + " -p" 
print command
#call(command, shell = True)


