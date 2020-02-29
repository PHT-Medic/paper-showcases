import shutil
import glob
import re
import os


def get_subjects_path(path, folder):
    path = path + folder
    subjects_path = glob.glob(path+'*.nii.gz')
    return subjects_path


def get_subjects(subejcts_path):
    r = re.compile(r'la_.{3}')
    subejct_strings = ''.join(subejcts_path)
    subjects = r.findall(subejct_strings)
    return subjects


def get_destination(subjects, destination):
    for subject in subjects:
        print(subject)


def divide_subjects(subject_names, stations):
    subject_split = int(len(subject_names) / stations)
    split_list = []
    for i in range(stations - 1):
        i += 1
        split_list.append(i * subject_split)

    splitted_subjects = [subject_names[i: j] for i, j in zip([0] + split_list, split_list + [None])]
    return splitted_subjects


def main():
    '''
    data preparation script to copy input files from decathlon challange
    to different station setups on cluster - prepares in equal splits
    input: challange, number of stations
    '''

    # TODO include hold-out from train_labels for overall model evaluation

    challange = 'Task02_Heart/'
    stations = 1
    base_path = '/mnt/data/rawdata/MedSegDecathlon/' + challange
    dest_folder = 'pht_preprocessed'
    challange_dest_path = base_path + dest_folder

    if not os.path.exists(challange_dest_path):
        os.makedirs(challange_dest_path)
    
    station_folders = []

    for stat in range(stations):
        stat += 1
        path = challange_dest_path + '/station_' + str(stat) + '/'

        # get folder path for station and create folder
        station_folders.append(path)
        if not os.path.exists(path):
            os.makedirs(path)

    subject_train_paths = get_subjects_path(base_path, 'imagesTr/')
    subject_label_paths = get_subjects_path(base_path, 'labelsTr/')
    subject_names = get_subjects(subject_train_paths)

    splitted_subjects = divide_subjects(subject_names, stations)
    splitted_train_paths = divide_subjects(subject_train_paths, stations)
    splitted_label_paths = divide_subjects(subject_label_paths, stations)

    for i in range(stations):

        subjects = list(zip(splitted_subjects[i], splitted_train_paths[i], splitted_label_paths[i]))
        for sub, train_path, label_path in subjects:
            print(sub)
            dest_train_path = station_folders[i] + sub + '_train.nii.gz'
            dest_label_path = station_folders[i] + sub + '_label.nii.gz'
            shutil.copyfile(train_path, dest_train_path, follow_symlinks=True)
            shutil.copyfile(label_path, dest_label_path, follow_symlinks=True)


if __name__ == "__main__":
    main()
