# Mednet segmentation train

Testtrain to evaluate best model on cluser.

To prepare input data, use the data preparation tool:
`/radiology/data_preparation/data_prep.py`

## Note
Tested with `docker run --gpus all -m 15G --shm-size 20G --workdir=/opt/pht_train/executions/currenty_running/_working  --entrypoint=/opt/pht_train/endpoints/mednet_test/commands/run/entrypoint.py -v /data-path/segmentation/Task02_Heart/test:/data/heart:ro imagep:tag`
