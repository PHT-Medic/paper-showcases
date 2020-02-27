#!/usr/bin/env python

import shutil
import pandas as pd
import urllib.request as request
from urllib.error import URLError
from contextlib import closing
import os


def download_file(path, file):
    if os.path.isfile(file):
        print('{} already downloaded'.format(file))
    else:
        print('Saving file to {}'.format(file))
        try:
            with closing(request.urlopen(path)) as r:
                with open(file, 'wb') as f:
                    shutil.copyfileobj(r, f)
        except URLError as e:
            print('Error {} downloading {} '.format(e, file))


def main():
    subjects = pd.read_csv('download.csv', header=0, delimiter=';')
    home = 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/'

    for i in range(len(subjects)):
        probe = subjects.iloc[i, 1]
        pat = subjects.iloc[i, 0]
        station = subjects.iloc[i, 2]
        station_dir = '/mnt/volume/data/station_' + str(station) + '/'

        read_1 = '_1.filt.fastq.gz'
        read_2 = '_2.filt.fastq.gz'

        if not os.path.exists(station_dir):
            os.makedirs(station_dir)
            print('Created station {} directory'.format(station))

        file_path = pat + '/sequence_read/' + probe
        file_1 = file_path + read_1
        file_2 = file_path + read_2

        print('Download subject {} of {}'.format(i, len(subjects)))
        paths = [[home + file_1, station_dir + file_1], [home + file_2, station_dir + file_2]]
        patient_path = station_dir + pat + '/sequence_read/'

        if not os.path.exists(patient_path):
            os.makedirs(patient_path)

        for path, file in paths:
            download_file(path, file)


if __name__ == "__main__":
    main()

