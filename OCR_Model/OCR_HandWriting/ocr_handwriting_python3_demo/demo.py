# -*- coding: utf-8 -*-
from urllib import parse
import base64
import os
import hashlib
import time
import json
import requests
from glob import glob
from PIL import Image
import numpy as np
import pdfkit
"""
  手写文字识别WebAPI接口调用示例接口文档(必看):https://doc.xfyun.cn/rest_api/%E6%89%8B%E5%86%99%E6%96%87%E5%AD%97%E8%AF%86%E5%88%AB.html
  图片属性：jpg/png/bmp,最短边至少15px，最长边最大4096px,编码后大小不超过4M,识别文字语种：中英文
  webapi OCR服务参考帖子(必看)：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=39111&highlight=OCR
  (Very Important)创建完webapi应用添加服务之后一定要设置ip白名单，找到控制台--我的应用--设置ip白名单，如何设置参考：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=41891
  错误码链接：https://www.xfyun.cn/document/error-code (code返回错误码时必看)
  @author iflytek
"""
# OCR手写文字识别接口地址
URL = "http://webapi.xfyun.cn/v1/service/v1/ocr/handwriting"
# 应用APPID(必须为webapi类型应用,并开通手写文字识别服务,参考帖子如何创建一个webapi应用：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=36481)
APPID = ""
# 接口密钥(webapi类型应用开通手写文字识别后，控制台--我的应用---手写文字识别---相应服务的apikey)
API_KEY = ""


def getHeader():
    curTime = str(int(time.time()))
    param = "{\"language\":\"" + language + "\",\"location\":\"" + location + "\"}"
    paramBase64 = base64.b64encode(param.encode('utf-8'))

    m2 = hashlib.md5()
    str1 = API_KEY + curTime + str(paramBase64, 'utf-8')
    m2.update(str1.encode('utf-8'))
    checkSum = m2.hexdigest()
    # 组装http请求头
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


def getBody(filepath):
    with open(filepath, 'rb') as f:
        imgfile = f.read()
    data = {'image': str(base64.b64encode(imgfile), 'utf-8')}
    return data


message = """"""
textList = []
height_sum = 0
blank = 30  # 设置每张图片之间的像素距离
if not os.path.exists('/usr/web/outputs'):
    os.makedirs('/usr/web/outputs')

# 语种设置
language = "cn|en"
# 是否返回文本位置信息
location = "true"

image_files = glob('./test_images/*.*')
for image_file in sorted(image_files):
    # 图片上传接口地址
    picFilePath = image_file
    r = requests.post(URL, headers=getHeader(), data=getBody(picFilePath))
    result = []
    anchordata = []
    for i in range(len(json.loads(r.text)['data']['block'][0]['line'])):
        result.append(json.loads(r.text)['data']['block'][0]['line'][i]['word'][0]['content'])
    for j in range(len(json.loads(r.text)['data']['block'][0]['line'])):
        anchordata.append(json.loads(r.text)['data']['block'][0]['line'][j]['location']['top_left']['x'])
        anchordata.append(json.loads(r.text)['data']['block'][0]['line'][j]['location']['top_left']['y'])
        anchordata.append(json.loads(r.text)['data']['block'][0]['line'][j]['location']['right_bottom']['x'])
        anchordata.append(json.loads(r.text)['data']['block'][0]['line'][j]['location']['right_bottom']['y'])

    print(result)
    print(anchordata)

    img = Image.open(image_file)
    print(img.size)
    w = img.width
    h = img.height
    img = np.array(img)
    print(w, h)
    print(img.shape)

    for t in range(len(result)):
        img[int(anchordata[4 * t + 1]):int(anchordata[4 * t + 3]),
        int(anchordata[4 * t]):int(anchordata[4 * t + 2]), :] = 255

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
        textList.append(str((anchordata[4 * x + 3] - anchordata[4 * x + 1]) * 0.6))  # 字号修正
        textList.append(str(anchordata[4 * x]))
        textList.append(str(anchordata[4 * x + 1] + height_sum))
        textList.append(result[x])
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
pdfkit.from_url('39.100.154.163/test.html', '/usr/web/test.pdf',configuration=confg)
