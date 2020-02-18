import torchio

import torchio
from torchio import ImagesDataset, Image, Subject

subject_a = Subject[
    Image('ct', '/media/herr/Platte/segmentation/Task02_Heart/imagesTr/la_003.nii.gz', torchio.INTENSITY),
    Image('label', '/media/herr/Platte/segmentation/Task02_Heart/labelsTr/la_003.nii.gz', torchio.LABEL),
]
subject_b = Subject[
    Image('ct', '/media/herr/Platte/segmentation/Task02_Heart/imagesTr/la_004.nii.gz', torchio.INTENSITY),
    Image('label', '/media/herr/Platte/segmentation/Task02_Heart/labelsTr/la_004.nii.gz', torchio.LABEL),
]

subjects_list = [subject_a, subject_b]
subjects_dataset = ImagesDataset(subjects_list)
subject_sample = subjects_dataset[0]

print(subject_sample)