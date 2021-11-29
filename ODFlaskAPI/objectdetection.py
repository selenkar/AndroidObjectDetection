import io
import os

import numpy as np

import cv2

from PIL import Image


class ObjectDetection():

    confthres = 0.5
    nmsthres = 0.1

    def get_labels(labels_path):
        # YOLO modelin eğitildiği COCO sınıf etiketleri
        lpath = os.path.sep.join(['./', labels_path])
        LABELS = open(lpath).read().strip().split("\n")
        return LABELS

    def get_colors(LABELS):
        # olası sınıf etiketleri için renk listesi
        np.random.seed(42)
        COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
        return COLORS

    def get_weights(weights_path):
        # YOLO ağırlıklarının ve model yapılanmasının yollarını oluşturma
        weightsPath = os.path.sep.join(['./', weights_path])
        return weightsPath

    def get_config(config_path):
        configPath = os.path.sep.join(['./', config_path])
        return configPath


    def load_model(configpath, weightspath):
        # COCO veri kümesinde eğitilmiş olan YOLO nesne tanımanın yüklenmesi
        print("[INFO] loading YOLO from disk...")
        model = cv2.dnn.readNetFromDarknet(configpath, weightspath)
        return model


    def get_predection(image, model, LABELS, COLORS):
        (H, W) = image.shape[:2]

        # modelden ihtiyaç duyulan katmanların belirlenmesi
        ln = model.getLayerNames()
        ln = [ln[i[0] - 1] for i in model.getUnconnectedOutLayers()]

        # giriş görüntüsü sinir ağı için blob haline getirildi
        # olasılık ve sınırlayıcılar verilir
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                     swapRB=True, crop=False)
        model.setInput(blob)
        layerOutputs = model.forward(ln)

        boxes = []
        confidences = []
        classIDs = []

        # dnn katmanları için döngü
        for output in layerOutputs:
            # nesne tanımları için döngü
            for detection in output:
                # geçerli olan nesne tanıma ağının sınıf IDsi
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # tespit edilen olasılığın minimum olasılık değerinden büyük olmasını sağlayan zayıf tahminlerin ayrılması
                if confidence > 0.5:
                    # tespit edilen nesnenin -kutunun- görüntü boyutları yeniden ölçeklendirildi
                    # YOLO'nun sınırlayıcı kutusu (x, y) koordinatları ve kutu genişlik-yükseklik değerleri ile döndürüldü

                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    # sınırlayıcı kutunun sol-üst köşesi için (x, y) koordinatlarının ortalaması kullanıldı
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    #değerlerin güncellenmesi
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # çakışan kutular için, non-maxima
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.1)

        if len(idxs) > 0:
            # tutulan dizinler üzerinde döngü
            for i in idxs.flatten():
                # sınırlayıcı kutu koordinatları
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                # fotoğrafon üzerinde tespit işlemleri için sınırlayıcı kutuyu ve etiketi çizme
                color = [int(c) for c in COLORS[classIDs[i]]]
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(LABELS[classIDs[i]], confidences[i])
                print(boxes)
                print(classIDs)
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return image


