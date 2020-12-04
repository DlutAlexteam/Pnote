# 【飞桨】爱笔记——基于深度学习的智慧笔记系统

##  app部分

### 功能介绍：

作为一款笔记识别的项目，我们力图使用的便捷性，考虑到学习生活中的实际情况，我 们决定开发安卓端的手机 app 应用。用户可以通过打开 app，对现有的笔记进行拍照或是选 定已经存储在手机中的图片，将图片进行上传，经过后台服务器中的算法处理及 pdf 生成， 用户可以对生成的 pdf 文件版本的笔记进行下载。从而完成了从图片到电子笔记的转化。

用户打开 app 将看到用户界面，界面通过 activity_main.xml 进行布局，并通过 MainActivity 类进行后台控制。

随后用户可以点击选择图片来进行图片的上传。点击后将会出现选择框，用户可通过拍照或者是从相册中进行选择来选择想要上传的照片。

用户上传完毕后即可点击按钮进入服务器网站进行转化后 pdf 文件的下载。

### 代码构成：

采用 android studio 进行安卓 app 设计，使用 java 语言进行开发， 并使用 Gradle 框架进行安卓项目管理。

前端布局由 activity_crop.xml，fragment_main.xml，layout_picture_selection.xml，

toolbar_layout.xml， activity_main.xml 五个 xml 文件进行构建。

后端中， MainActivity 类负责 app 启动后的处理以及网站跳转按钮的对应操作， MainFragment 类负责图片监听和图片的上传以及与服务器的通讯操作。



### HTML 文件转化：

完成文本检测和识别后进行 HTML 文件转化，该部分旨在于根据神经网络输出的文本位置 和文本内容，将原图对应文本位置的地方进行底色填充，并在原图对应的位置插入可选择的、 大小合适的原文本内容。以便于后续转化为 PDF 文件。神经网络输出含有文本内容的 result 列表和对应文字检测框坐标的 anchordata 列表。

* 根据 anchorlist 我们可以得出文本检测框的像素范围，并将像素范围内的文本利用 底色进行填充
* 将底色填充后的图片保存至 output 目录，以便于 html 文件对图片进行调用。
* 由 anchorlist 计算出字体的大小，并将计算得出的字体大小填入 html 的 p 标签中。
* 由 anchorlist 计 算 得 出 文 本 的 起 始 位 置 坐 标 ， 并 利 用 HTML 文 件 中 的 position:absolute 属性对文本的绝对位置进行约束。
* 由 result 导出每个 p 标签的对应文本内容并导入对应位置。
* 对于多页图片，我们设置间隔像素以便于区分每一页的内容。
* 保存 HTML 文件。

## 模型

### 介绍:

我们的OCR旨在创建多语言、卓越、领先和实用的OCR工具，帮助用户培训更好的模型，并将它们应用到实践中。由于我们不能给出比paddlepaddleocr更好的结果，我们再PPocr的推理模型的基础上改进网络，进行识别

### OCR 预训练模型

| Model introduction                              | Model name              | Recommended scene | Detection model                                              | Direction classifier                                         | Recognition model                                            |
| ----------------------------------------------- | ----------------------- | ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Chinese and English ultra-lightweight OCR model | ch_ppocr_mobile_v1.1_xx | Mobile & server   | [inference model](https://paddleocr.bj.bcebos.com/20-09-22/mobile/det/ch_ppocr_mobile_v1.1_det_infer.tar) | [inference model](https://paddleocr.bj.bcebos.com/20-09-22/cls/ch_ppocr_mobile_v1.1_cls_infer.tar) | [inference model](https://paddleocr.bj.bcebos.com/20-09-22/mobile/rec/ch_ppocr_mobile_v1.1_rec_infer.tar) |