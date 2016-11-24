#!/usr/bin/python

import sys, getopt, csv, re

vcf_filename = "/home/gmslwkg/all.somatic.snvs.vcf"
print("Hello World!\n")

chromosomes = {'1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','X','Y'}

def get_tier1(input_string):
        tier1_val = input_string.split(",")[0]
        return tier1_val

with open(vcf_filename, 'rb') as tsvin:
	tsvin = csv.reader(tsvin, delimiter = '\t')
	for row in tsvin:
		if row[0] not in chromosomes:
			#print(row[0])
			continue
		#print row
		tumor_string = row[10]
		tumor_split = tumor_string.split(":")
		#print(tumor_split)
		#print(get_tier1(tumor_split[4]) + " " + get_tier1(tumor_split[5]))
		normal_string = row[9]
		normal_split = normal_string.split(":")
		#print(tumor_string + " " + normal_string)
		#a,c,g,t
		tumor_a_count = int(get_tier1(tumor_split[4]))
		tumor_c_count = int(get_tier1(tumor_split[5]))
		tumor_g_count = int(get_tier1(tumor_split[6]))
		tumor_t_count = int(get_tier1(tumor_split[7]))
		
		normal_a_count = int(get_tier1(normal_split[4]))
                normal_c_count = int(get_tier1(normal_split[5]))
                normal_g_count = int(get_tier1(normal_split[6]))
                normal_t_count = int(get_tier1(normal_split[7]))
		
		tumor_counts = (tumor_a_count, tumor_c_count, tumor_g_count, tumor_t_count)
		tumor_depth = sum(tumor_counts)
		normal_counts = (normal_a_count, normal_c_count, normal_g_count, normal_t_count)
		normal_depth = sum(normal_counts)
		tumor_vaf = float(float(sorted(tumor_counts)[2]) / float(tumor_depth))
		if tumor_depth >= 30 and normal_depth >= 20 and tumor_vaf >= 0.05 and not re.search('QSS_ref',row[6]):
			#print(str(sorted(tumor_counts)[2]) + " " + str(tumor_depth) + " " + str(tumor_vaf) + str(row))
			print(row[7] + ";TAF=" + str(tumor_vaf))
			#print(str(tumor_depth) + " " + str(normal_depth) + " " + str(tumor_vaf))
#def get_tier1(input_string):
#	tier1_val = input_string.split(",")[0]
#	return tier1_val
