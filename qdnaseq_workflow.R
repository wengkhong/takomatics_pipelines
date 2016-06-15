#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
} else if (length(args)==1) {
  # default output file
  args[2] = "out.txt"
}

input_bamfile = args[1]
bins_path = args[2]
library(QDNAseq)
library(CGHregions)
library(Kmisc)
sample_name = strip_extension(input_bamfile)
load(bins_path)
#bins <- getBinAnnotations(binSize=15)
print("Reading BAM file")
readCounts <- binReadCounts(bins, bamfiles=input_bamfile)
save(readCounts, file = paste(sample_name, "_ReadCounts.RData", sep = ""))
readCountsFiltered <- applyFilters(readCounts, residual=TRUE, blacklist=TRUE)
readCountsFiltered <- estimateCorrection(readCountsFiltered)
copyNumbers <- correctBins(readCountsFiltered)
copyNumbersNormalized <- normalizeBins(copyNumbers)
copyNumbersSmooth <- smoothOutlierBins(copyNumbersNormalized)
png(file = paste(sample_name, "_CN.png", sep = ""), width=800, height=600, type = "cairo")
plot(copyNumbersSmooth)
dev.off()
#exportBins(copyNumbersSmooth, file="LGG150.txt")
exportBins(copyNumbersSmooth, file=paste(sample_name, ".igv", sep = ""), format="igv")
exportBins(copyNumbersSmooth, file=paste(sample_name, ".bed", sep = ""), format="bed")
copyNumbersSegmented <- segmentBins(copyNumbersSmooth, transformFun="sqrt")
copyNumbersSegmented <- normalizeSegmentedBins(copyNumbersSegmented)
png(file = paste(sample_name, "_CNSeg.png", sep = ""), width=800, height=600, type = "cairo")
plot(copyNumbersSegmented)
dev.off()
copyNumbersCalled <- callBins(copyNumbersSegmented)
#cgh <- makeCgh(copyNumbersCalled)
exportBins(copyNumbersSegmented, file=paste(sample_name, "_segments.tsv", sep = ""), format="tsv", type="segments")
exportBins(copyNumbersCalled, file=paste(sample_name, "_calls.tsv", sep = ""), format="tsv", type="calls")
