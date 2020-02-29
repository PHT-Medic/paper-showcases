# Note

Currently operating on decathlon challenge with segmentation - config file for challenge in ./config
Based on:
Packages from: https://github.com/lab-midas/torch-mednet
From Tobias: https://github.com/lab-midas/torch-mednet

Not tested on train yet, but runs locally. Challange path hardcoded in main function currently (`config/challange.yml`).

Call: `python main.py`

To see the loss of the model, open tensorboard with:
`tensorboard --logdir ./runs`

WIP of analysis code for valid train: train code is stored in `../train/mednet/`

## Data preparation
`../data_preparation/data_prep.py` copys the file in the needed format for the station. **Within the code, the number of stations and challange name have to be specified.** 

Current main file runs with this config on local gpu machine with decathlon challange data.

## Next
Next steps to get valid train:
- [ ] Choose model and dataset
- [x] Data preprocessing
- [ ] Evaluate scores on different datasets to choose challenge
- [ ] Finalize code, clean up (remove all unnecessary parts) and create valid train
- [ ] Deploy three stations with same data setup
- [ ] Run analysis
