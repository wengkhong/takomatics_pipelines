#!/usr/bin/python

import sys, getopt, csv, re, argparse

vcf_filename = "/home/gmslwkg/all.somatic.snvs.vcf"
vcf_filename = ''
parser = argparse.ArgumentParser()
#parser.add_argument('-i', '--ifile', dest = 'vcf_filename')
parser.add_argument("-i", "--ifile", dest="vcf_filename", help = "Input file")
args = parser.parse_args()
print args.vcf_filename
#sys.exit()

if args.vcf_filename:
	vcf_filename = args.vcf_filename
#else:

chromosomes = []
for i in range(1,23):
	chromosomes.append(str(i))
	chromosomes.append("chr" + str(i))
chromosomes.extend(['X','Y','chrX','chrY'])

def get_tier1(input_string):
        tier1_val = input_string.split(",")[0]
        return tier1_val

with open(vcf_filename, 'rb') as tsvin:
	tsvin = csv.reader(tsvin, delimiter = '\t')
	for row in tsvin:
		if row[0][0] is "#":
			print "\t".join(row)
			continue
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
			row[7] = row[7] + ";VAF=" + "{0:.3f}".format(tumor_vaf) + ";TDP=" + str(tumor_depth) + ";NDP=" + str(normal_depth)
			#print(str(tumor_depth) + " " + str(normal_depth) + " " + str(tumor_vaf))
			print "\t".join(row)
#def get_tier1(input_string):
#	tier1_val = input_string.split(",")[0]
#	return tier1_val
