# -*- coding:utf-8 -*-
import os
from ocr import ocr
import time
import shutil
import numpy as np
import pandas as pd
from PIL import Image
from glob import glob
import chardet
from urllib3 import *
from re import *
import hashlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pdfkit

def single_pic_proc(image_file):
    image = np.array(Image.open(image_file).convert('RGB'))
    result, image_framed, anchordata = ocr(image)
    return result, image_framed, anchordata


if __name__ == '__main__':
    # 监听图片是否收到
    while(True):
        a = os.path.exists('./test_images/001.png')
        if (a == True):
            break
    image_files = glob('./test_images/*.*')
    result_dir = './test_result'
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    os.makedirs('./test_result/test_images')

    message = """"""
    textList = []
    height_sum = 0
    blank = 20  # 设置每张图片之间的像素距离
    if not os.path.exists('usr/web/outputs'):
        os.makedirs('/usr/web/outputs')

    for image_file in sorted(image_files):
        t = time.time()
        result, image_framed, anchordata = single_pic_proc(image_file)
        output_file = os.path.join(result_dir, image_file.split('/')[-1])
        txt_file = os.path.join(result_dir, image_file.split('/')[-1].split('.')[0] + '.txt')

        txt_f = open(txt_file, 'w', encoding="utf-8")
        Image.fromarray(image_framed).save(output_file)
        for key in result:
            print(result[key][1])

        txt_f.close()
        print(image_file)
        print(output_file)
        print(result)
        img = Image.open(output_file)
        w = img.width
        h = img.height

        img = Image.open(image_file)
        img = img.resize((w, h))
        img = np.array(img)

        #   字体消除
        for t in range(len(result)):
            img[int(round(anchordata[t][1])):int(round(anchordata[t][7])),
            int(round(anchordata[t][0])):int(round(anchordata[t][6])), :] = 255

        img = Image.fromarray(img)
        savename ="/usr/web/outputs/output_" + os.path.basename(image_file)
        img.save(savename)
        webname = "." + "/outputs/output_" + os.path.basename(image_file)
        textList.append(str(height_sum))
        textList.append(str(webname))
        message = message + """
    <div style="position:absolute; left:0px; top:%spx;">
        <img src="%s"/>
    </div>"""

        for x in range(len(result)):
            if x not in result:
                continue
            textList.append(str(anchordata[x][7] - anchordata[x][1] - 6))  # 字号修正
            textList.append(str(anchordata[x][0]))
            textList.append(str(anchordata[x][1] + height_sum))
            textList.append(result[x][1])
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

    # 生成pdf文档用于返回
    confg = pdfkit.configuration(wkhtmltopdf='/root/wkhtmltopdf/usr/local/bin/wkhtmltopdf')
    # 这里指定一下wkhtmltopdf的路径，这就是我为啥在前面让记住这个路径
    pdfkit.from_url('39.100.154.163/test.html', '/usr/web/test.pdf',configuration=confg

                                                        
                                       