# Note

nf-core-hlatyping baseimage availabe.
The expected outcome of optitype over all site will be in the workdir.

## Usage
First run:
```python entrypoint.py -s 1```

Second run:
```python entrypoint.py -s 2```

Last run:
```python entrypoint.py -s 1 -l 1```

Info: after each run the folder with results_X will be deleted. At the last execution the intermediate results will be also deleted.

Final plot should look like:
![Result](HLA_frequencies.pdf "Task B result")


### Downloader
Usage: ```python downloader.py```
Downloads selection (download.csv) of probes and subjects to `./data`

## Next steps for showcase:
- [ ] deploy station
- [x] write download script
- [ ] download data (specified ID and analysis from optitype paper)
- [ ] load synthetic data into tranSMART at station
- [ ] define API how data staging is handeld
- [ ] include patient information in analysis
- [ ] prepare station for execution of train

