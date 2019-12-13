# Showcases

Showcases for the publication of the personal health train


# Radiology department
Distributed analysis with PHT on imaging data for image segmentation.
With different learning settings (central vs decentral / with and without balance of data)
We have access to the de.NBI cloud now with their GPUs and can run the trains, as soon we get the algorithms
Tobias prepares the algo, such we can use it on the 


## Next steps:
- finish base image
- put algorithms on train
- test locally
- split data in different settings 

# QBiC
Constructed research question we use first hla typing pipeline from nf-core (https://github.com/nf-core/hlatyping) and then can construct two different research questions:
1. How many patients have this specific allele condition
2. Summary of HLA conditions from sites

Two steps in one train:
1. Task: Use pipeline to produce HLA mapping for each patient Input:fastQ (or already preprocessed BAM) files
Output: File for each patient
Dependencies: nextflow, java

2. Task: Answer asked questions of researcher Input: List of all patient specific HLA mappings Output: Counts of patients or summary
Dependencies: python


## Next steps:
- Number of patients
- Clearifiy if and how ICGC data (2108 patients available) can be connected to station
- Get analysis support from QBiC in second half of January
- create base image
