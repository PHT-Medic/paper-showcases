#!/usr/bin/env python3

from glob import glob
import os

from train import training
from train_lib.train.ISICTrain import Train

if __name__ == "__main__":
    train = Train(results='results.pkl', query='query.json')  # /opt/pht_train/results/
    results = train.load_results()

    queries = train.load_queries()

    station = str(len(results["exec"]) + 1)

    print("Central analysis on all data")

    print(results)

    # run analysis
    performance = training(cfgs_name='example', save_dir='effb6_central_multigpu', gpus='gpu=0,1', prev_station=None)
    print(performance)
    # Find best CV Fold bases on F1 score performance
    best_cv = train.find_best_cv(performance)

    path_best_model = glob('/mnt/vdb/data/isic/effb6_central_multigpu/CVSet' + str(best_cv) + '/**_best**.pt')
    _, best_model_name = os.path.split(path_best_model[0])

    # Copy mat files to train for plotting
    mat_files = glob('/mnt/vdb/data/isic/effb6_central_multigpu/**/*.mat')
    train.create_stat_res_dirs(1)

    for i, mat_file in enumerate(mat_files):
        _, file_name = os.path.split(mat_file)
        dest_file = '/opt/pht_results/res_' + str(1) + '/mat_' + str(i) + file_name
        train.copy_file(mat_file, dest_file)
        print('Copied file {} from to {}'.format(mat_file, dest_file))
    # Copy best model of current station to train directory
    print('Copy best model of current station to train directory')
    train.copy_file(path_best_model[0], '/opt/pht_results/' + best_model_name)

    train.central_plot(['/opt/pht_results/res_1'], ['acc', 'sens'],
                       '/opt/pht_results/central_train_performance.png', smoothing_factor=.5,
                       save=True, num_stations=1)
    train.clean_up('/opt/pht_results/res_1')

    results['analysis'] = performance
    train.save_results(results=results)
    print('New results:\n' + str(results) + "\nupdated and files saved")
    train.save_queries(queries)

    # clean up
    # if train.clean_up('/mnt/vdb/data/isic/effb6_central_multigpu'):
    #    exit(0)
    exit(0)
