#!/usr/bin/python

import sys, getopt, csv

vcf_filename = "/home/gmslwkg/all.somatic.snvs.vcf"
print("Hello World!\n")

with open(vcf_filename, 'rb') as tsvin:
	tsvin = csv.reader(tsvin, delimiter = '\t')
	for row in tsvin:
		print row

