import os
from typing import List

import numpy as np
import torch

from cvu.interface.model import IModel
from cvu.utils.general import get_path
from cvu.image_text_matching.unicl.backends.common import download_weights


class UniCL(IModel):

    def __init__(self, weight: str = "swin_b", device="auto") -> None:
        # initiate class attributes
        self._device = None
        self._model = None

        # setup device
        self._set_device(device)

        # load model
        self._load_model(weight)

    def _set_device(self, device: str) -> None:
        """Internally setup torch.device

        Args:
            device (str): name of the device to be used.
        """
        if device in ('auto', 'gpu'):
            self._device = torch.device(
                'cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            self._device = torch.device(device)

    def _load_model(self, weight: str) -> None:
        """Internally load torch model

        Args:
            weight (str): path to torch .pth weight files or predefined-identifiers (such as swin_b, swin_t)
        """
        # attempt to load predefined weights
        if not os.path.exists(weight):
            if self._device != 'cpu':
                weight += '.cuda'

            # get path to pretrained weights
            weight = get_path(__file__, "weights", f"{weight}.pth")

            # download weights if not already downloaded
            download_weights(weight, "torch")

        # load model
        self._model = torch.load(weight, map_location=self._device)

        # use FP16 if GPU is being used
        # TODO - test this
        if self._device != 'cpu':
            self._model.half()

        # set model to eval mode
        self._model.eval()