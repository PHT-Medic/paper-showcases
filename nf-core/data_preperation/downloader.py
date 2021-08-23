#!/usr/bin/env python

import shutil
import pandas as pd
import urllib.request as request
from urllib.error import URLError
import threading
from contextlib import closing
import os
import urllib.request
import urllib.error
import time
from multiprocessing import Pool
import ftplib

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


def prepare_url_file(path, root_path):
    subjects = pd.read_csv(path, header=0, delimiter=';')
    home = '/vol1/ftp/phase3/data/'
    read_1 = '_1.filt.fastq.gz'
    read_2 = '_2.filt.fastq.gz'

    pat_lis = []
    prob_lis = []
    stat_lis = []
    url_lis = []
    file_lis = []
    sub_path_lis = []
    for i in range(len(subjects)):
        pat = subjects.iloc[i, 0]
        probe = subjects.iloc[i, 1]
        station = subjects.iloc[i, 2]
        file_path = pat + '/sequence_read/' + probe
        url_1 = home + file_path + read_1
        file_1_path = root_path + '/data/' + 'station_' + str(station) + '/' + file_path + read_1
        file_2_path = root_path + '/data/' + 'station_' + str(station) + '/' + file_path + read_2
        pat_path = root_path + '/data/' + 'station_' + str(station) + '/' + pat

        pat_lis.append(pat)
        prob_lis.append(probe)
        stat_lis.append(station)
        url_lis.append(url_1)
        file_lis.append(file_1_path)
        sub_path_lis.append(pat_path)

        url_2 = home + file_path + read_2
        pat_lis.append(pat)
        prob_lis.append(probe)
        stat_lis.append(station)
        url_lis.append(url_2)
        file_lis.append(file_2_path)
        sub_path_lis.append(pat_path)

    new_d = {'Subject': pat_lis, 'Probe': prob_lis, 'Station': stat_lis, 'Url': url_lis, 'Path': file_lis, 'Pat_Path': sub_path_lis}
    trans_df = pd.DataFrame(data=new_d)

    trans_df.to_csv('transformed.csv', index=False)


def downloader(local_path, remote_path, patient_path):

    if not os.path.exists(patient_path+"/sequence_read"):
        os.makedirs(patient_path+"/sequence_read")

    if os.path.exists(local_path):
        local_size = os.path.getsize(local_path)
    else:
        local_size = 0

    with ftplib.FTP('ftp.1000genomes.ebi.ac.uk') as ftp:

        try:
            ftp.login()
            try:
                remote_size = ftp.size(remote_path)
            except:
                remote_size = -99

            if remote_size == local_size:
                print('Already downloaded file '.format(patient_path))
            else:
                print('Download {}'.format(remote_path))
                ftp.retrbinary("RETR " + remote_path, open(local_path, 'wb').write)
                ftp.quit()

        except ftplib.all_errors as e:
            print('FTP error:', e)


def multi_run_wrapper(args):
    return downloader(*args)


def main():
    root_path = '/mnt/vdb/showcases/nf-core/data_preperation'  # current directory
    prepare_url_file('download.csv', root_path)

    subjects = pd.read_csv('transformed.csv', header=0, delimiter=',')
    p = Pool(processes=12)

    station_dir = root_path + 'data/station_' + str(2) + '/'

    if not os.path.exists(station_dir):
        os.makedirs(station_dir)

    local_paths = subjects['Path']
    remote_paths = subjects['Url']
    patient_path = subjects['Pat_Path']
    lists = zip(local_paths, remote_paths, patient_path)
    result = p.map(multi_run_wrapper, lists)


if __name__ == "__main__":
    main()

