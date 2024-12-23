# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import os
import ast
import argparse
import numpy as np


def argsparser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model_dir",
        type=str,
        default=None,
        help=("Directory include:'model.pdiparams', 'model.pdmodel', "
              "'infer_cfg.yml', created by tools/export_model.py."),
        required=True)
    parser.add_argument(
        "--image_file", type=str, default=None, help="Path of image file.")
    parser.add_argument(
        "--image_dir",
        type=str,
        default=None,
        help="Dir of image file, `image_file` has a higher priority.")
    parser.add_argument(
        "--batch_size", type=int, default=1, help="batch_size for inference.")
    parser.add_argument(
        "--video_file",
        type=str,
        default=None,
        help="Path of video file, `video_file` or `camera_id` has a highest priority."
    )
    parser.add_argument(
        "--camera_id",
        type=int,
        default=-1,
        help="device id of camera to predict.")
    parser.add_argument(
        "--threshold", type=float, default=0.5, help="Threshold of score.")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory of output visualization files.")
    parser.add_argument(
        "--run_mode",
        type=str,
        default='paddle',
        help="mode of running(paddle/trt_fp32/trt_fp16/trt_int8)")
    parser.add_argument(
        "--device",
        type=str,
        default='cpu',
        help="Choose the device you want to run, it can be: CPU/GPU/XPU/NPU, default is CPU."
    )
    parser.add_argument(
        "--use_gpu",
        type=ast.literal_eval,
        default=False,
        help="Deprecated, please use `--device`.")
    parser.add_argument(
        "--run_benchmark",
        type=ast.literal_eval,
        default=False,
        help="Whether to predict a image_file repeatedly for benchmark")
    parser.add_argument(
        "--enable_mkldnn",
        type=ast.literal_eval,
        default=False,
        help="Whether use mkldnn with CPU.")
    parser.add_argument(
        "--enable_mkldnn_bfloat16",
        type=ast.literal_eval,
        default=False,
        help="Whether use mkldnn bfloat16 inference with CPU.")
    parser.add_argument(
        "--cpu_threads", type=int, default=1, help="Num of threads with CPU.")
    parser.add_argument(
        "--trt_min_shape", type=int, default=1, help="min_shape for TensorRT.")
    parser.add_argument(
        "--trt_max_shape",
        type=int,
        default=1280,
        help="max_shape for TensorRT.")
    parser.add_argument(
        "--trt_opt_shape",
        type=int,
        default=640,
        help="opt_shape for TensorRT.")
    parser.add_argument(
        "--trt_calib_mode",
        type=bool,
        default=False,
        help="If the model is produced by TRT offline quantitative "
        "calibration, trt_calib_mode need to set True.")
    parser.add_argument(
        '--save_images',
        type=ast.literal_eval,
        default=True,
        help='Save visualization image results.')
    parser.add_argument(
        '--save_mot_txts',
        action='store_true',
        help='Save tracking results (txt).')
    parser.add_argument(
        '--save_mot_txt_per_img',
        action='store_true',
        help='Save tracking results (txt) for each image.')
    parser.add_argument(
        '--scaled',
        type=bool,
        default=False,
        help="Whether coords after detector outputs are scaled, False in JDE YOLOv3 "
        "True in general detector.")
    parser.add_argument(
        "--tracker_config", type=str, default=None, help=("tracker donfig"))
    parser.add_argument(
        "--reid_model_dir",
        type=str,
        default=None,
        help=("Directory include:'model.pdiparams', 'model.pdmodel', "
              "'infer_cfg.yml', created by tools/export_model.py."))
    parser.add_argument(
        "--reid_batch_size",
        type=int,
        default=50,
        help="max batch_size for reid model inference.")
    parser.add_argument(
        '--use_dark',
        type=ast.literal_eval,
        default=True,
        help='whether to use darkpose to get better keypoint position predict ')
    parser.add_argument(
        "--action_file",
        type=str,
        default=None,
        help="Path of input file for action recognition.")
    parser.add_argument(
        "--window_size",
        type=int,
        default=50,
        help="Temporal size of skeleton feature for action recognition.")
    parser.add_argument(
        "--random_pad",
        type=ast.literal_eval,
        default=False,
        help="Whether do random padding for action recognition.")
    parser.add_argument(
        "--save_results",
        action='store_true',
        default=False,
        help="Whether save detection result to file using coco format")
    parser.add_argument(
        '--use_coco_category',
        action='store_true',
        default=False,
        help='Whether to use the coco format dictionary `clsid2catid`')
    parser.add_argument(
        "--slice_infer",
        action='store_true',
        help="Whether to slice the image and merge the inference results for small object detection."
    )
    parser.add_argument(
        '--slice_size',
        nargs='+',
        type=int,
        default=[640, 640],
        help="Height of the sliced image.")
    parser.add_argument(
        "--overlap_ratio",
        nargs='+',
        type=float,
        default=[0.25, 0.25],
        help="Overlap height ratio of the sliced image.")
    parser.add_argument(
        "--combine_method",
        type=str,
        default='nms',
        help="Combine method of the sliced images' detection results, choose in ['nms', 'nmm', 'concat']."
    )
    parser.add_argument(
        "--match_threshold",
        type=float,
        default=0.6,
        help="Combine method matching threshold.")
    parser.add_argument(
        "--match_metric",
        type=str,
        default='ios',
        help="Combine method matching metric, choose in ['iou', 'ios'].")
    parser.add_argument(
        "--collect_trt_shape_info",
        action='store_true',
        default=False,
        help="Whether to collect dynamic shape before using tensorrt.")
    parser.add_argument(
        "--tuned_trt_shape_file",
        type=str,
        default="shape_range_info.pbtxt",
        help="Path of a dynamic shape file for tensorrt.")
    parser.add_argument("--use_fd_format", action="store_true")
    parser.add_argument(
        "--task_type",
        type=str,
        default='Detection',
        help="How to save the coco result, it only work with save_results==True.  Optional inputs are Rotate or Detection, default is Detection."
    )
    return parser


class Times(object):
    def __init__(self):
        self.time = 0.
        # start time
        self.st = 0.
        # end time
        self.et = 0.

    def start(self):
        self.st = time.time()

    def end(self, repeats=1, accumulative=True):
        self.et = time.time()
        if accumulative:
            self.time += (self.et - self.st) / repeats
        else:
            self.time = (self.et - self.st) / repeats

    def reset(self):
        self.time = 0.
        self.st = 0.
        self.et = 0.

    def value(self):
        return round(self.time, 4)


class Timer(Times):
    def __init__(self, with_tracker=False):
        super(Timer, self).__init__()
        self.with_tracker = with_tracker
        self.preprocess_time_s = Times()
        self.inference_time_s = Times()
        self.postprocess_time_s = Times()
        self.tracking_time_s = Times()
        self.img_num = 0

    def info(self, average=False):
        pre_time = self.preprocess_time_s.value()
        infer_time = self.inference_time_s.value()
        post_time = self.postprocess_time_s.value()
        track_time = self.tracking_time_s.value()

        total_time = pre_time + infer_time + post_time
        if self.with_tracker:
            total_time = total_time + track_time
        total_time = round(total_time, 4)
        print("------------------ Inference Time Info ----------------------")
        print("total_time(ms): {}, img_num: {}".format(total_time * 1000,
                                                       self.img_num))
        preprocess_time = round(pre_time / max(1, self.img_num),
                                4) if average else pre_time
        postprocess_time = round(post_time / max(1, self.img_num),
                                 4) if average else post_time
        inference_time = round(infer_time / max(1, self.img_num),
                               4) if average else infer_time
        tracking_time = round(track_time / max(1, self.img_num),
                              4) if average else track_time

        average_latency = total_time / max(1, self.img_num)
        qps = 0
        if total_time > 0:
            qps = 1 / average_latency
        print("average latency time(ms): {:.2f}, QPS: {:2f}".format(
            average_latency * 1000, qps))
        if self.with_tracker:
            print(
                "preprocess_time(ms): {:.2f}, inference_time(ms): {:.2f}, postprocess_time(ms): {:.2f}, tracking_time(ms): {:.2f}".
                format(preprocess_time * 1000, inference_time * 1000,
                       postprocess_time * 1000, tracking_time * 1000))
        else:
            print(
                "preprocess_time(ms): {:.2f}, inference_time(ms): {:.2f}, postprocess_time(ms): {:.2f}".
                format(preprocess_time * 1000, inference_time * 1000,
                       postprocess_time * 1000))

    def report(self, average=False):
        dic = {}
        pre_time = self.preprocess_time_s.value()
        infer_time = self.inference_time_s.value()
        post_time = self.postprocess_time_s.value()
        track_time = self.tracking_time_s.value()

        dic['preprocess_time_s'] = round(pre_time / max(1, self.img_num),
                                         4) if average else pre_time
        dic['inference_time_s'] = round(infer_time / max(1, self.img_num),
                                        4) if average else infer_time
        dic['postprocess_time_s'] = round(post_time / max(1, self.img_num),
                                          4) if average else post_time
        dic['img_num'] = self.img_num
        total_time = pre_time + infer_time + post_time
        if self.with_tracker:
            dic['tracking_time_s'] = round(track_time / max(1, self.img_num),
                                           4) if average else track_time
            total_time = total_time + track_time
        dic['total_time_s'] = round(total_time, 4)
        return dic

def crop_image_with_det(batch_input, det_res, thresh=0.3):
    boxes = det_res['boxes']
    score = det_res['boxes'][:, 1]
    boxes_num = det_res['boxes_num']
    start_idx = 0
    crop_res = []
    for b_id, input in enumerate(batch_input):
        boxes_num_i = boxes_num[b_id]
        if boxes_num_i == 0:
            continue
        boxes_i = boxes[start_idx:start_idx + boxes_num_i, :]
        score_i = score[start_idx:start_idx + boxes_num_i]
        res = []
        for box, s in zip(boxes_i, score_i):
            if s > thresh:
                crop_image, new_box, ori_box = expand_crop(input, box)
                if crop_image is not None:
                    res.append(crop_image)
        crop_res.append(res)
    return crop_res


def normal_crop(image, rect):
    imgh, imgw, c = image.shape
    label, conf, xmin, ymin, xmax, ymax = [int(x) for x in rect.tolist()]
    org_rect = [xmin, ymin, xmax, ymax]
    if label != 0:
        return None, None, None
    xmin = max(0, xmin)
    ymin = max(0, ymin)
    xmax = min(imgw, xmax)
    ymax = min(imgh, ymax)
    return image[ymin:ymax, xmin:xmax, :], [xmin, ymin, xmax, ymax], org_rect


def crop_image_with_mot(input, mot_res, expand=True):
    res = mot_res['boxes']
    crop_res = []
    new_bboxes = []
    ori_bboxes = []
    for box in res:
        if expand:
            crop_image, new_bbox, ori_bbox = expand_crop(input, box[1:])
        else:
            crop_image, new_bbox, ori_bbox = normal_crop(input, box[1:])
        if crop_image is not None:
            crop_res.append(crop_image)
            new_bboxes.append(new_bbox)
            ori_bboxes.append(ori_bbox)
    return crop_res, new_bboxes, ori_bboxes

def crop_image(image,box,ratio=0.3):
    # id, conf, xmin, ymin, width, height, width, height
    box[:,4] += box[:,2]
    box[:,5] += box[:,3]
    image_h, image_w, _ = image.shape
    h_half = (box[:, 5] - box[:, 3]) * (1 + ratio) / 2.0
    w_half = (box[:, 4] - box[:, 2]) * (1 + ratio) / 2.0
    w_half = np.maximum(w_half,h_half*0.75)
    bbox = np.column_stack((
        (box[:, 2] + box[:, 4]) / 2.0 - w_half, # xmin
        (box[:, 3] + box[:, 5]) / 2.0 - h_half, # ymin
        (box[:, 2] + box[:, 4]) / 2.0 + w_half, # xmax
        (box[:, 3] + box[:, 5]) / 2.0 + h_half, # ymax
    ))
    cropped = np.clip(bbox, [0]*4, [image_w - 1, image_h - 1]*2).astype(int)
    return [image[ymin:ymax, xmin:xmax,:] for xmin, ymin, xmax, ymax in cropped]

def rescale_box(box,scale):
    box[:,2:8] *= np.array([scale[0],scale[1]]*3)
    

# def expand_crop(images, rect, expand_ratio=0.3):
#     imgh, imgw, c = images.shape
#     label, conf, xmin, ymin, xmax, ymax = [int(x) for x in rect.tolist()]
#     if label != 0:
#         return None, None, None
#     org_rect = [xmin, ymin, xmax, ymax]
#     h_half = (ymax - ymin) * (1 + expand_ratio) / 2.
#     w_half = (xmax - xmin) * (1 + expand_ratio) / 2.
#     if h_half > w_half * 4 / 3:
#         w_half = h_half * 0.75
#     center = [(ymin + ymax) / 2., (xmin + xmax) / 2.]
#     ymin = max(0, int(center[0] - h_half))
#     ymax = min(imgh - 1, int(center[0] + h_half))
#     xmin = max(0, int(center[1] - w_half))
#     xmax = min(imgw - 1, int(center[1] + w_half))
#     return images[ymin:ymax, xmin:xmax, :], [xmin, ymin, xmax, ymax], org_rect

def tlwh2tlbr(tlwh):
    tlwh[:,4] += tlwh[:,2]
    tlwh[:,5] += tlwh[:,3]

def parse_mot_res(res):
    res[:,4] += res[:,2]
    res[:,5] += res[:,3]
    return {'boxes': res}
    # boxes, scores, ids = input[0]
    # for box, score, i in zip(boxes[0], scores[0], ids[0]):
    #     xmin, ymin, w, h = box
    #     res = [i, 0, score, xmin, ymin, xmin + w, ymin + h]
    #     mot_res.append(res)
    # return {'boxes': np.array(mot_res)}

def parse_mot_keypoint(input, coord_size):
    parsed_skeleton_with_mot = {}
    ids = []
    skeleton = []
    for tracker_id, kpt_seq in input:
        ids.append(tracker_id)
        kpts = np.array(kpt_seq.kpts, dtype=np.float32)[:, :, :2]
        kpts = np.expand_dims(np.transpose(kpts, [2, 0, 1]),
                              -1)  #T, K, C -> C, T, K, 1
        bbox = np.array(kpt_seq.bboxes, dtype=np.float32)
        skeleton.append(refine_keypoint_coordinary(kpts, bbox, coord_size))
    parsed_skeleton_with_mot["mot_id"] = ids
    parsed_skeleton_with_mot["skeleton"] = skeleton
    return parsed_skeleton_with_mot

def refine_keypoint_coordinary(kpts, bbox, coord_size):
    """
        This function is used to adjust coordinate values to a fixed scale.
    """
    tl = bbox[:, 0:2]
    wh = bbox[:, 2:] - tl
    tl = np.expand_dims(np.transpose(tl, (1, 0)), (2, 3))
    wh = np.expand_dims(np.transpose(wh, (1, 0)), (2, 3))
    target_w, target_h = coord_size
    res = (kpts - tl) / wh * np.expand_dims(
        np.array([[target_w], [target_h]]), (2, 3))
    return res


def get_current_memory_mb():
    """
    It is used to Obtain the memory usage of the CPU and GPU during the running of the program.
    And this function Current program is time-consuming.
    """
    import pynvml
    import psutil
    import GPUtil
    gpu_id = int(os.environ.get('CUDA_VISIBLE_DEVICES', 0))

    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    cpu_mem = info.uss / 1024. / 1024.
    gpu_mem = 0
    gpu_percent = 0
    gpus = GPUtil.getGPUs()
    if gpu_id is not None and len(gpus) > 0:
        gpu_percent = gpus[gpu_id].load
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_mem = meminfo.used / 1024. / 1024.
    return round(cpu_mem, 4), round(gpu_mem, 4), round(gpu_percent, 4)


def multiclass_nms(bboxs, num_classes, match_threshold=0.6, match_metric='iou'):
    final_boxes = []
    for c in range(num_classes):
        idxs = bboxs[:, 0] == c
        if np.count_nonzero(idxs) == 0: continue
        r = nms(bboxs[idxs, 1:], match_threshold, match_metric)
        final_boxes.append(np.concatenate([np.full((r.shape[0], 1), c), r], 1))
    return final_boxes


def nms(dets, match_threshold=0.6, match_metric='iou'):
    """ Apply NMS to avoid detecting too many overlapping bounding boxes.
        Args:
            dets: shape [N, 5], [score, x1, y1, x2, y2]
            match_metric: 'iou' or 'ios'
            match_threshold: overlap thresh for match metric.
    """
    if dets.shape[0] == 0:
        return dets[[], :]
    scores = dets[:, 0]
    x1 = dets[:, 1]
    y1 = dets[:, 2]
    x2 = dets[:, 3]
    y2 = dets[:, 4]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    ndets = dets.shape[0]
    suppressed = np.zeros((ndets), dtype=np.int32)

    for _i in range(ndets):
        i = order[_i]
        if suppressed[i] == 1:
            continue
        ix1 = x1[i]
        iy1 = y1[i]
        ix2 = x2[i]
        iy2 = y2[i]
        iarea = areas[i]
        for _j in range(_i + 1, ndets):
            j = order[_j]
            if suppressed[j] == 1:
                continue
            xx1 = max(ix1, x1[j])
            yy1 = max(iy1, y1[j])
            xx2 = min(ix2, x2[j])
            yy2 = min(iy2, y2[j])
            w = max(0.0, xx2 - xx1 + 1)
            h = max(0.0, yy2 - yy1 + 1)
            inter = w * h
            if match_metric == 'iou':
                union = iarea + areas[j] - inter
                match_value = inter / union
            elif match_metric == 'ios':
                smaller = min(iarea, areas[j])
                match_value = inter / smaller
            else:
                raise ValueError()
            if match_value >= match_threshold:
                suppressed[j] = 1
    keep = np.where(suppressed == 0)[0]
    dets = dets[keep, :]
    return dets


coco_clsid2catid = {
    0: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
    10: 11,
    11: 13,
    12: 14,
    13: 15,
    14: 16,
    15: 17,
    16: 18,
    17: 19,
    18: 20,
    19: 21,
    20: 22,
    21: 23,
    22: 24,
    23: 25,
    24: 27,
    25: 28,
    26: 31,
    27: 32,
    28: 33,
    29: 34,
    30: 35,
    31: 36,
    32: 37,
    33: 38,
    34: 39,
    35: 40,
    36: 41,
    37: 42,
    38: 43,
    39: 44,
    40: 46,
    41: 47,
    42: 48,
    43: 49,
    44: 50,
    45: 51,
    46: 52,
    47: 53,
    48: 54,
    49: 55,
    50: 56,
    51: 57,
    52: 58,
    53: 59,
    54: 60,
    55: 61,
    56: 62,
    57: 63,
    58: 64,
    59: 65,
    60: 67,
    61: 70,
    62: 72,
    63: 73,
    64: 74,
    65: 75,
    66: 76,
    67: 77,
    68: 78,
    69: 79,
    70: 80,
    71: 81,
    72: 82,
    73: 84,
    74: 85,
    75: 86,
    76: 87,
    77: 88,
    78: 89,
    79: 90
}


def gaussian_radius(bbox_size, min_overlap):
    height, width = bbox_size

    a1 = 1
    b1 = (height + width)
    c1 = width * height * (1 - min_overlap) / (1 + min_overlap)
    sq1 = np.sqrt(b1**2 - 4 * a1 * c1)
    radius1 = (b1 + sq1) / (2 * a1)

    a2 = 4
    b2 = 2 * (height + width)
    c2 = (1 - min_overlap) * width * height
    sq2 = np.sqrt(b2**2 - 4 * a2 * c2)
    radius2 = (b2 + sq2) / 2

    a3 = 4 * min_overlap
    b3 = -2 * min_overlap * (height + width)
    c3 = (min_overlap - 1) * width * height
    sq3 = np.sqrt(b3**2 - 4 * a3 * c3)
    radius3 = (b3 + sq3) / 2
    return min(radius1, radius2, radius3)


def gaussian2D(shape, sigma_x=1, sigma_y=1):
    m, n = [(ss - 1.) / 2. for ss in shape]
    y, x = np.ogrid[-m:m + 1, -n:n + 1]

    h = np.exp(-(x * x / (2 * sigma_x * sigma_x) + y * y / (2 * sigma_y *
                                                            sigma_y)))
    h[h < np.finfo(h.dtype).eps * h.max()] = 0
    return h


def draw_umich_gaussian(heatmap, center, radius, k=1):
    """
    draw_umich_gaussian, refer to https://github.com/xingyizhou/CenterNet/blob/master/src/lib/utils/image.py#L126
    """
    diameter = 2 * radius + 1
    gaussian = gaussian2D(
        (diameter, diameter), sigma_x=diameter / 6, sigma_y=diameter / 6)

    x, y = int(center[0]), int(center[1])

    height, width = heatmap.shape[0:2]

    left, right = min(x, radius), min(width - x, radius + 1)
    top, bottom = min(y, radius), min(height - y, radius + 1)

    masked_heatmap = heatmap[y - top:y + bottom, x - left:x + right]
    masked_gaussian = gaussian[radius - top:radius + bottom, radius - left:
                               radius + right]
    if min(masked_gaussian.shape) > 0 and min(masked_heatmap.shape) > 0:
        np.maximum(masked_heatmap, masked_gaussian * k, out=masked_heatmap)
    return heatmap

def expand_crop(images, rect, expand_ratio=0.3):
    imgh, imgw, c = images.shape
    label, conf, xmin, ymin, xmax, ymax = [int(x) for x in rect.tolist()]
    if label != 0:
        return None, None, None
    org_rect = [xmin, ymin, xmax, ymax]
    h_half = (ymax - ymin) * (1 + expand_ratio) / 2.
    w_half = (xmax - xmin) * (1 + expand_ratio) / 2.
    if h_half > w_half * 4 / 3:
        w_half = h_half * 0.75
    center = [(ymin + ymax) / 2., (xmin + xmax) / 2.]
    ymin = max(0, int(center[0] - h_half))
    ymax = min(imgh - 1, int(center[0] + h_half))
    xmin = max(0, int(center[1] - w_half))
    xmax = min(imgw - 1, int(center[1] + w_half))
    return images[ymin:ymax, xmin:xmax, :], [xmin, ymin, xmax, ymax], org_rect
