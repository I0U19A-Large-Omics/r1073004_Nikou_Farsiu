# SNP Calling Workflow

This is my snakemake workflow for the SNP calling assignment. It takes raw sequencing 
files and finds genetic variants between a tumor and normal sample.

## What you need before running

You need these two fastq files in your work folder:
- TLE66_N.fastq
- TLE66_T.fastq

You can get them by running:
ln -sf /staging/leuven/stg_00079/teaching/data_manual_snpcall/*.fastq .

## How to run it

First get an interactive session:
srun -n 1 -c 2 --mem 16G --time=3:00:00 -A lp_edu_large_omics -p interactive --cluster wice --pty bash -

Then load the tools:
export PATH=/lustre1/project/stg_00079/teaching/I0U19a_conda_2026/bin/:$PATH

Then go to your scratch folder and run snakemake:
cd /scratch/leuven/381/vsc38197/snakemake_snpcalling
snakemake --snakefile /user/leuven/381/vsc38197/r1073004_Nikou_Farsiu/030_snakemake_snpcalling/Snakefile --cores 2

## What you get at the end

The final file is 100.final/snps.annotated.tsv
It contains the SNPs found between the tumor and normal sample with annotations.

## Folder structure

- 010.fastqc/ has the quality control reports
- 020.aligned/ has the aligned bam files
- 030.snps/ has the raw snp calls
- 040.filtered/ has the filtered snps
- 050.annotated/ has the annotated snps
- 100.final/ has the final output file