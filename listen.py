import os

oldnum = 0
while True:
    path = './paddlepaddle/input'      # 输入文件夹地址
    files = os.listdir(path)   # 读入文件夹
    num_png = len(files)       # 统计文件夹中的文件个数
    if oldnum != num_png:
        os.system('python ./main.py --image_dir="./input/" --det_model_dir="./inference/ch_ppocr_mobile_v1.1_det_infer/"  --rec_model_dir="./inference/ch_ppocr_mobile_v1.1_rec_infer/" --cls_model_dir="./inference/ch_ppocr_mobile_v1.1_cls_infer/" --use_angle_cls=True --use_space_char=True --use_gpu=False')
        oldnum = num_png
