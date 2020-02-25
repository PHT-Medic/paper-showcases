#!/usr/bin/env python

import shutil
import pandas as pd
import urllib.request as request
from contextlib import closing
import os


def main():
    # Todo separate to different stations

    subjects = pd.read_csv('download.csv', header=0, delimiter=',')

    count = 0
    home = 'ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/'

    for i in range(len(subjects)):
        probe = subjects.iloc[i, 1]
        pat = subjects.iloc[i, 0]
        read_1 = '_1.filt.fastq.gz'
        read_2 = '_2.filt.fastq.gz'

        file_path = pat + '/sequence_read/' + probe
        file_1 = file_path + read_1
        file_2 = file_path + read_2
        count += 1
        print('Download subject {} of {}'.format(count, len(subjects)))
        paths = [[home + file_1, 'data/' + file_1], [home + file_2, 'data/' + file_2]]
        patient_path = 'data/' + pat + '/sequence_read/'
        if not os.path.exists(patient_path):
            os.makedirs(patient_path)
        for path, file in paths:
            if os.path.isfile(file):
                print('{} already downlaoded'.format(file))
            else:
                print('Saving file to {}'.format(file))
                with closing(request.urlopen(path)) as r:
                    with open(file, 'wb') as f:
                        shutil.copyfileobj(r, f)



if __name__ == "__main__":
    main()
