# Note
Train for showcase hlatyping
## Usage

To test on server with read data run from the directory `train`:

 ```
$ docker build -f Dockerfile -t demo-nf-core:s1 .
$ docker run -v nf_test_volume:/mnt/vdb/data --env FHIR_ADDRESS=<https://fhir.personalhealthtrain.de> --env FHIR_TOKEN=<TOKEN> demo-nf-core:s1
 ```

You can enter this train to see results or commit the train and execute the next station.
## Next steps for showcase:
- [x] deploy station
- [x] write download script
- [x] download data (specified ID and analysis from optitype paper)
- [x] solve multithrading issue in run_hlatyping()
- [x] load synthetic data into FHIR at station
- [x] define API how data staging is handeld
- [x] include patient information in analysis
- [x] prepare station for execution of train

