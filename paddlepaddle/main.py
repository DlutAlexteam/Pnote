# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
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
import os
import sys

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.append(os.path.abspath(os.path.join(__dir__, "../..")))

import tools.infer.utility as utility
from ppocr.utils.utility import initial_logger

logger = initial_logger()
import cv2
import tools.infer.predict_det as predict_det
import tools.infer.predict_rec as predict_rec
import tools.infer.predict_cls as predict_cls
import copy
import numpy as np
import math
import time
from ppocr.utils.utility import get_image_file_list, check_and_read_gif
from PIL import Image
from tools.infer.utility import draw_ocr
from tools.infer.utility import draw_ocr_box_txt
import pdfkit


class TextSystem(object):
    def __init__(self, args):
        self.text_detector = predict_det.TextDetector(args)
        self.text_recognizer = predict_rec.TextRecognizer(args)
        self.use_angle_cls = args.use_angle_cls
        if self.use_angle_cls:
            self.text_classifier = predict_cls.TextClassifier(args)

    def get_rotate_crop_image(self, img, points):
        '''
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        '''
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]),
                np.linalg.norm(points[2] - points[3])))
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]),
                np.linalg.norm(points[1] - points[2])))
        pts_std = np.float32([[0, 0], [img_crop_width, 0],
                              [img_crop_width, img_crop_height],
                              [0, img_crop_height]])
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M, (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC)
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def print_draw_crop_rec_res(self, img_crop_list, rec_res):
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite("./doc/img_crop_%d.jpg" % bno, img_crop_list[bno])
            print(bno, rec_res[bno])

    def __call__(self, img):
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img)
        print("dt_boxes num : {}, elapse : {}".format(len(dt_boxes), elapse))
        if dt_boxes is None:
            return None, None
        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        if self.use_angle_cls:
            img_crop_list, angle_list, elapse = self.text_classifier(
                img_crop_list)
            print("cls num  : {}, elapse : {}".format(
                len(img_crop_list), elapse))
        rec_res, elapse = self.text_recognizer(img_crop_list)
        print("rec_res num  : {}, elapse : {}".format(len(rec_res), elapse))
        # self.print_draw_crop_rec_res(img_crop_list, rec_res)
        return dt_boxes, rec_res


def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < 10 and \
                (_boxes[i + 1][0][0] < _boxes[i][0][0]):
            tmp = _boxes[i]
            _boxes[i] = _boxes[i + 1]
            _boxes[i + 1] = tmp
    return _boxes


def main(args):
    image_file_list = get_image_file_list(args.image_dir)
    # print(image_file_list)
    text_sys = TextSystem(args)
    is_visualize = True
    font_path = args.vis_font_path
    message = """"""
    textList = []
    height_sum = 0
    blank = 20  # 设置每张图片之间的像素距离
    if not os.path.exists('/usr/web/outputs'):
        os.makedirs('/usr/web/outputs')
    for image_file in image_file_list:
        img, flag = check_and_read_gif(image_file)
        if not flag:
            img = cv2.imread(image_file)
        if img is None:
            logger.info("error in loading image:{}".format(image_file))
            continue
        starttime = time.time()

        dt_boxes, rec_res = text_sys(img)

        elapse = time.time() - starttime
        print("Predict time of %s: %.3fs" % (image_file, elapse))

        # print("dt_boxes:", dt_boxes)
        # print()
        # print("rec_res:", rec_res)

        # drop_score = 0.5
        # dt_num = len(dt_boxes)
        # for dno in range(dt_num):
        #     text, score = rec_res[dno]
        #     if score >= drop_score:
        #         text_str = "%s, %.3f" % (text, score)
        #         print(text_str)

        if is_visualize:
            image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            w = image.width
            h = image.height

            image = image.resize((w, h))
            image = np.array(image)

            boxes = dt_boxes  # 坐标（四个点）
            txts = [rec_res[i][0] for i in range(len(rec_res))]  # 字

            print(boxes)
            print(txts)
            # scores = [rec_res[i][1] for i in range(len(rec_res))]

            print(image.shape)
            for t in range(len(boxes)):
                image[int(round(boxes[t][0][1])):int(round(boxes[t][3][1])),
                int(round(boxes[t][0][0])):int(round(boxes[t][1][0])), :] = \
                    image[int(round(boxes[t][1][1]))][int(round(boxes[t][1][0]))]

            img = Image.fromarray(image)
            savename = os.path.join("/usr/web/modify_input", image_file.split("/")[-1])
            img.save(savename)
            webname = os.path.join("./modify_input", image_file.split("/")[-1]) 
            textList.append(str(height_sum))
            textList.append(str(webname))
            message = message + """
        <div style="position:absolute; left:0px; top:%spx;">
            <img src="%s"/>
        </div>"""
            for x in range(len(txts)):
                textList.append(str((boxes[x][2][1] - boxes[x][0][1]) * 0.8))  # 字号修正
                textList.append(str(boxes[x][0][0]))
                textList.append(str(boxes[x][0][1] + height_sum))
                textList.append(txts[x])
                message = message + """
        <p style="font-size:%spx">
            <a style="position:absolute; left:%spx; top:%spx;">%s</a>
        </p>"""

            height_sum = height_sum + h + blank

        start = """<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
</head>
<body>"""
    end = """
</body>
</html>
"""
    message = (start + message + end) % tuple(textList)

    GEN_HTML = "/usr/web/test.html"
    # 打开文件，准备写入
    f = open(GEN_HTML, 'w')
    # 写入文件
    f.write(message)
    # 关闭文件
    f.close()

    # # 生成pdf文档用于返回
    confg = pdfkit.configuration(wkhtmltopdf='/root/ai_competition/wkhtmltopdf/usr/local/bin/wkhtmltopdf')
    # # 这里指定一下wkhtmltopdf的路径，这就是我为啥在前面让记住这个路径
    pdfkit.from_url('39.100.154.163/test.html', '/usr/web/test.pdf', configuration=confg)


if __name__ == "__main__":
    main(utility.parse_args())
