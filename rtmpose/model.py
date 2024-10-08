import os
import sys
sys.path.append("rtmpose")

from rtmcc_head import RTMCCHead    
from cspnext_pafpn import CSPNeXtPAFPN
from cspnext import CSPNeXt
from data_preprocessor import PoseDataPreprocessor
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import torch
import cv2
import time

class WholeBody:
    def __init__(self) -> None:
        # common setting
        self.num_keypoints = 133
        self.input_size = (288, 384)

        codec = dict(
            type='SimCCLabel',
            input_size=self.input_size,
            sigma=(6., 6.93),
            simcc_split_ratio=2.0,
            normalize=False,
            use_dark=False
        )

        self.data_preprocessor = PoseDataPreprocessor(
            mean=[123.675, 116.28, 103.53],
            std=[58.395, 57.12, 57.375],
            bgr_to_rgb=True
        )

        self.backbone = CSPNeXt(
            arch='P5',
            expand_ratio=0.5,
            deepen_factor=1.,
            widen_factor=1.,
            out_indices=(4, ),
            channel_attention=True,
            norm_cfg=dict(type='SyncBN'),
            act_cfg=dict(type='SiLU'),
            init_cfg=dict(
                type='Pretrained',
                prefix='backbone.',
                checkpoint='https://download.openmmlab.com/mmpose/v1/projects/'
                'rtmposev1/cspnext-l_udp-aic-coco_210e-256x192-273b7631_20230130.pth'  # noqa
            )
        )

        self.head = RTMCCHead(
            in_channels=1024,
            out_channels=self.num_keypoints,
            input_size=codec['input_size'],
            in_featuremap_size=tuple([s // 32 for s in codec['input_size']]),
            simcc_split_ratio=codec['simcc_split_ratio'],
            final_layer_kernel_size=7,
            gau_cfg=dict(
                hidden_dims=256,
                s=128,
                expansion_factor=2,
                dropout_rate=0.,
                drop_path=0.,
                act_fn='SiLU',
                use_rel_bias=False,
                pos_enc=False),
            loss=dict(
                type='KLDiscretLoss',
                use_target_weight=True,
                beta=10.,
                label_softmax=True),
            decoder=codec
        )

        model = torch.load("ckpt/rtmpose-l_simcc-coco-wholebody_pt-aic-coco_270e-384x288-eaeb96c8_20230125.pth")
        headState = {k[5:]: v for k, v in model['state_dict'].items() if k.startswith('head')}
        backboneState = {k[9:]: v for k, v in model['state_dict'].items() if k.startswith('backbone')}
        self.head.load_state_dict(headState)
        self.backbone.load_state_dict(backboneState)
    
    def predict(self, image):
        image = np.array(image)

        # (height, width, channel)
        scaleInput = (image.shape[1] / self.input_size[0], image.shape[0] / self.input_size[1])
        image = cv2.resize(image, self.input_size)
        image = torch.from_numpy(np.array(image).swapaxes(0, 2).swapaxes(1, 2))
        image = image.to("cuda").unsqueeze(0).type(torch.float32)

        res = self.data_preprocessor.forward({"inputs": image, "data_samples": None})
        res = res["inputs"].to("cuda")
        res = self.backbone.forward(res)
        res = self.head.predict(res, None)

        res = np.array(res[0]["keypoints"][0])
        res[:, 0] = res[:, 0] * scaleInput[0]
        res[:, 1] = res[:, 1] * scaleInput[1]
        return res
