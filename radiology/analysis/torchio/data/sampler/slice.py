import numpy as np
from copy import copy
from tqdm import tqdm

from torch.utils.data import Dataset, DataLoader

import torchio.utils


class SliceSampler(Dataset):
    # todo add slice min, max
    def __init__(self,
                 subjects_dataset,
                 num_workers=0,
                 shuffle_subjects=False,
                 delete_dim=False,
                 slice_min=None,
                 slice_max=None):

        self.subjects = []
        self.index_list = []
        self.slice_min = None
        self.slice_max = None

        # Load all datasets to memory!!!
        subjects_loader = DataLoader(
            subjects_dataset,
            num_workers=num_workers,
            collate_fn=lambda x: x[0],
            shuffle=shuffle_subjects)

        # Iterate over subjects using the dataloader.
        for subject_number, sample in enumerate(tqdm(subjects_loader)):
            # Get sizes for images in sample.
            sample_img_sizes = []
            for key, value in sample.items():
                if torchio.utils.is_image_dict(value):
                    sample_img_sizes.append(value['data'].size())
            # All images should have the same size.
            assert len(set(sample_img_sizes)) == 1
            sample_img_size = sample_img_sizes[0]

            # Extract slices.
            # todo add axis selection
            slices = []
            for slice_number in range(sample_img_size[3]):
                # Create index.
                self.index_list.append((subject_number, slice_number))
                cropped_sample = {}
                # For each image in sample
                for key, value in sample.items():
                    cropped_sample[key] = {}
                    if torchio.utils.is_image_dict(value):
                        # Copy all dict entries and select slice from data field.
                        for k, tmp in value.items():
                            if k == 'data':
                                if delete_dim:
                                    cropped_sample[key]['data'] = copy(value['data'][:, :, :, slice_number])
                                else:
                                    cropped_sample[key]['data'] = copy(value['data'][:, :, :, [slice_number]])
                            else:
                                cropped_sample[key][k] = tmp
                # Torch doesn't like uint16.
                cropped_sample['index_ini'] = np.array([0, 0, slice_number]).astype(int)
                slices.append(cropped_sample)
            self.subjects.append(slices)
            del sample

    def __len__(self):
        return len(self.index_list)

    def __getitem__(self, index):
        subject_number, slice_number = self.index_list[index]
        if self.slice_min:
            if slice_number < self.slice_min:
                slice_number = self.slice_min
        if self.slice_max:
            if slice_number > self.slice_max:
                slice_number = self.slice_max
        return self.subjects[subject_number][slice_number]


class SliceSelectionSampler(Dataset):
    def __init__(self, subjects_dataset,
                 selected_slices,
                 num_workers=0,
                 shuffle_subjects=False):

        self.selected_slices = selected_slices
        self.subjects = []

        # Load all datasets to memory!!!
        subjects_loader = DataLoader(
            subjects_dataset,
            num_workers=num_workers,
            collate_fn=lambda x: x[0],
            shuffle=shuffle_subjects)

        # Iterate over subjects using the dataloader.
        for sample in tqdm(subjects_loader):
            # Extract selected slices.
            # todo add axis selection
            cropped_sample = {}
            for key, value in sample.items():
                cropped_sample[key] = {}
                if torchio.utils.is_image_dict(value):
                    for k, tmp in value.items():
                        if k == 'data':
                            cropped_sample[key]['data'] = copy(value['data'][:, :, :, self.selected_slices])
                        else:
                            cropped_sample[key][k] = tmp
            self.subjects.append(cropped_sample)
            del sample

    def __getitem__(self, index):
        return self.subjects[index]

    def __len__(self):
        return len(self.subjects)


def main():
    train_dataset, eval_dataset = datasets.create_IXI_datasets(eval_split=10)
    slices_train_ds = SliceSampler(eval_dataset,
                                   num_workers=15,
                                   shuffle_subjects=True)

    slice_train_dl = torch.utils.data.DataLoader(slices_train_ds, batch_size=batch_size, shuffle=True)

    for sample in slice_train_dl:
        print(*zip(sample['index_ini'], sample['img']['id']))
        break
    return

if __name__ == '__main__':
    main()
