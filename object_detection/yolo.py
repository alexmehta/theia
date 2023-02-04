from damo.damo.base_models.core.ops import RepConv
from damo.damo.apis.detector_inference import inference
from damo.damo.config.base import parse_config
from damo.damo.dataset import build_dataloader, build_dataset
from damo.damo.detectors.detector import build_ddp_model, build_local_model
from damo.damo.utils import fuse_model, get_model_info
from damo.tools.demo import Infer

import os
class Config(MyConfig):
    def __init__(self):
        super(Config, self).__init__()

        self.miscs.exp_name = os.path.split(
            os.path.realpath(__file__))[1].split('.')[0]
        self.miscs.eval_interval_epochs = 10
        self.miscs.ckpt_interval_epochs = 10
        # optimizer
        self.train.batch_size = 256
        self.train.base_lr_per_img = 0.01 / 64
        self.train.min_lr_ratio = 0.05
        self.train.weight_decay = 5e-4
        self.train.momentum = 0.9
        self.train.no_aug_epochs = 16
        self.train.warmup_epochs = 5

        # augment
        self.train.augment.transform.image_max_range = (640, 640)
        self.train.augment.mosaic_mixup.mixup_prob = 0.15
        self.train.augment.mosaic_mixup.degrees = 10.0
        self.train.augment.mosaic_mixup.translate = 0.2
        self.train.augment.mosaic_mixup.shear = 0.2
        self.train.augment.mosaic_mixup.mosaic_scale = (0.1, 2.0)

        self.dataset.train_ann = ('coco_2017_train', )
        self.dataset.val_ann = ('coco_2017_val', )

        # backbone
        structure = self.read_structure(
            './damo/base_models/backbones/nas_backbones/tinynas_L20_k1kx.txt')
        TinyNAS = {
            'name': 'TinyNAS_res',
            'net_structure_str': structure,
            'out_indices': (2, 4, 5),
            'with_spp': True,
            'use_focus': True,
            'act': 'relu',
            'reparam': True,
        }

        self.model.backbone = TinyNAS

        GiraffeNeckV2 = {
            'name': 'GiraffeNeckV2',
            'depth': 1.0,
            'hidden_ratio': 1.0,
            'in_channels': [96, 192, 384],
            'out_channels': [64, 128, 256],
            'act': 'relu',
            'spp': False,
            'block_name': 'BasicBlock_3x3_Reverse',
        }

        self.model.neck = GiraffeNeckV2

        ZeroHead = {
            'name': 'ZeroHead',
            'num_classes': 80,
            'in_channels': [64, 128, 256],
            'stacked_convs': 0,
            'reg_max': 16,
            'act': 'silu',
            'nms_conf_thre': 0.05,
            'nms_iou_thre': 0.7
        }
        self.model.head = ZeroHead

        self.dataset.class_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

class Yolo:
    def __init__(self,loco,ckpt_file,fuse,config=Config()) -> None:
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        model = build_local_model(config, device)
        model.head.nms = True
        model = build_ddp_model(model, local_rank=args.local_rank)
        model.eval()
        ckpt = torch.load(ckpt_file, map_location=device)
        new_state_dict = {}
        for k, v in ckpt['model'].items():
            k = 'module.' + k
            new_state_dict[k] = v
        model.load_state_dict(new_state_dict, strict=False)

        for layer in model.modules():
            if isinstance(layer, RepConv):
                layer.switch_to_deploy()

        if fuse:
            model = fuse_model(model)

        self.infer_engine = Infer(config, infer_size=(256,256), device=device,
        engine_type='torch',  ckpt=ckpt)

    def get_bounds(self,origin_image):
        bboxes, scores, cls_inds = self.infer_engine.forward(origin_image)
        return bboxes