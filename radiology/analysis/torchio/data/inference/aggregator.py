import os
import nibabel as nib
import numpy as np
import SimpleITK as sitk
import nilearn
from typing import Union, Sequence, Tuple
import shutil
import glob
import matplotlib.pylab as plt
import imageio
import datetime
import torch
import numpy as np
import scipy
from scipy import ndimage
from torchio.utils import to_tuple


#### Create MIP GIF
def create_gif(filenames, duration):
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    output_file = 'Gif-%s.gif' % datetime.datetime.now().strftime('%Y-%M-%d-%H-%M-%S')
    imageio.mimsave(output_file, images, duration=duration)


def create_mipGIF_from_3D(img, nb_image=40, duration=0.1, is_mask=False, borne_max=None):
    ls_mip = []

    img_data = img.get_data()
    img_data += 1e-5

    for angle in np.linspace(0, 360, nb_image):
        ls_slice = []
        vol_angle = scipy.ndimage.interpolation.rotate(img_data, angle)

        MIP = np.amax(vol_angle, axis=1)
        MIP -= 1e-5
        MIP[MIP < 1e-5] = 0
        MIP = np.flipud(MIP.T)
        ls_mip.append(MIP)
    try:
        shutil.rmtree('test_gif/')
    except:
        pass
    os.mkdir('test_gif/')

    ls_image = []
    for mip, i in zip(ls_mip, range(len(ls_mip))):
        fig, ax = plt.subplots()
        ax.set_axis_off()
        if borne_max is None:
            if is_mask == True:
                borne_max = 1
            else:
                borne_max = 15000
        plt.imshow(mip, cmap='Greys', vmax=borne_max)
        fig.savefig('test_gif/MIP' + '%04d' % (i) + '.png')
        plt.close(fig)

    filenames = glob.glob('test_gif/*.png')

    create_gif(filenames, duration)
    try:
        shutil.rmtree('test_gif/')
    except:
        pass


import numpy as np


class GridAggregator:
    """
    Adapted from NiftyNet.
    See https://niftynet.readthedocs.io/en/dev/window_sizes.html
    """
    def __init__(
            self,
            data: Union[torch.Tensor, np.ndarray],
            patch_overlap: Union[int, Sequence[int]],
            ):
        self.output_array = np.full(
            data.shape,
            fill_value=0,
            dtype=np.uint16,
        )
        self.patch_overlap = to_tuple(patch_overlap)

    @staticmethod
    def crop_batch(windows, location, border):
        location = location.astype(np.int)
        batch_shape = windows.shape
        spatial_shape = batch_shape[2:]  # ignore batch and channels dim
        num_dimensions = 3
        for idx in range(num_dimensions):
            location[:, idx] = location[:, idx] + border[idx]
            location[:, idx + 3] = location[:, idx + 3] - border[idx]
        cropped_shape = np.max(location[:, 3:6] - location[:, 0:3], axis=0)
        diff = spatial_shape - cropped_shape
        left = np.floor(diff / 2).astype(np.int)
        i_ini, j_ini, k_ini = left
        i_fin, j_fin, k_fin = left + cropped_shape
        batch = windows[
            :,  # batch dimension
            :,  # channels dimension
            i_ini:i_fin,
            j_ini:j_fin,
            k_ini:k_fin,
        ]
        return batch, location

    def add_batch(self, windows: torch.Tensor, locations: torch.Tensor):
        windows = windows.cpu()
        location_init = np.copy(locations)
        init_ones = np.ones_like(windows)
        windows, _ = self.crop_batch(
            windows, location_init,
            self.patch_overlap,
        )
        location_init = np.copy(locations)
        _, locations = self.crop_batch(
            init_ones,
            location_init,
            self.patch_overlap,
        )
        for window, location in zip(windows, locations):
            window = window[0]
            i_ini, j_ini, k_ini, i_fin, j_fin, k_fin = location
            self.output_array[i_ini:i_fin, j_ini:j_fin, k_ini:k_fin] = window
