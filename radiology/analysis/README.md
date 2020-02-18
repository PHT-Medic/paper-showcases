# Note

WIP! This code is not ready to use.

Currently operating on decathlon challenge with segmentation - config file for challenge in ./config
Based on:
Packages from: https://github.com/lab-midas/torch-mednet
From Tobias: https://github.com/lab-midas/torch-mednet

Current main file runs with this config on local gpu machine with decathlon challange data.

Models folder removed due to size. (80GB)

Next steps to get valid train:
- Choose model and dataset
- Write script to put input data (10 challanges) in required format
- Evaluate scores on different datasets to choose challenge
- Finalize code, clean up (remove all unnecessary) and create valid train
- Deploy three stations with same data setup
- Run analysis
