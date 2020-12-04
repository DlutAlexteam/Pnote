from flask import Flask, request,jsonify

app = Flask(__name__)

@app.route('/',methods = ["GET","POST"])
def hello():
    test = request.args.get("finish")
    if test == 1:
        
        os.system('python ./main.py --image_dir="./input/" --det_model_dir="./inference/ch_ppocr_mobile_v1.1_det_infer/" --rec_model_dir="./inference/ch_ppocr_mobile_v1.1_rec_infer/" --cls_model_dir="./inference/ch_ppocr_mobile_v1.1_cls_infer/" --use_angle_cls=True --use_space_char=True --use_gpu=False')
        test = 0 
    
    return jsonify({"test":test})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)



