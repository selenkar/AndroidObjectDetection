
import flask 
import werkzeug 
import cv2
from objectdetection import *

labelsPath = "yolo-coco\\coco.names"
cfgpath = "yolo-coco\\yolov3.cfg"
wpath = "yolo-coco\\yolov3.weights"

app = flask.Flask(__name__)

@app.route('/predict/', methods = ['GET', 'POST'])
def main():
    imagefile = flask.request.files['image0']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    print("\nReceived image file name : " + imagefile.filename)
    imagefile.save(filename)

    img = cv2.imread(filename, -1)
        
    Lables = ObjectDetection.get_labels(labelsPath)
    CFG = ObjectDetection.get_config(cfgpath)
    Weights = ObjectDetection.get_weights(wpath)
    models = ObjectDetection.load_model(CFG, Weights)
    Colors = ObjectDetection.get_colors(Lables)

    #cv2.imread('./dogcat.jpg')

    resultImage = ObjectDetection.get_predection(img,models,Lables,Colors)
    cv2.imshow("Image", resultImage)
    cv2.waitKey()
    return "object detection completed successfully"

    
if __name__ == '__main__':
    app.run ("192.168.1.69", debug = True)

