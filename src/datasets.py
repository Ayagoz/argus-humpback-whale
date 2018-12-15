import tqdm
import torch
import pandas as pd
from turbojpeg import TurboJPEG

from torch.utils.data import Dataset


def get_samples(train_val_cvs_path, train):
    data_df = pd.read_csv(train_val_cvs_path)
    if train:
        data_df = data_df[~data_df.val]
    else:
        data_df = data_df[data_df.val]
        data_df = data_df[data_df.class_index != -1]

    images = []
    class_indexes = []
    bboxes = []

    for i, row in tqdm.tqdm(data_df.iterrows(), total=len(data_df)):
        image = open(row.image_path, 'rb').read()
        images.append(image)
        class_indexes.append(row.class_index)
        bboxes.append((row.x0, row.y0, row.x1, row.y1))

    return images, class_indexes, bboxes


class WhaleDataset(Dataset):
    def __init__(self, train_val_cvs_path, train,
                 image_transform=None):
        super().__init__()
        self.train_folds_path = train_val_cvs_path
        self.train = train
        self.image_transform = image_transform
        self.turbo_jpeg = TurboJPEG('/usr/lib/x86_64-linux-gnu/libturbojpeg.so.0')

        self.images, self.class_indexes, self.bboxes = \
            get_samples(train_val_cvs_path, train)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        image = self.turbo_jpeg.decode(image)
        class_index = self.class_indexes[idx]
        bbox = self.bboxes[idx]

        if self.image_transform is not None:
            image = self.image_transform(image)

        class_index = torch.tensor(class_index)

        return image, class_index, bbox
