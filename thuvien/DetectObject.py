import numpy as np  
import sys,os  
import cv2
import pickle
import imutils



def detect_object(imgfile):
    # import caffe  

    path =os.path.dirname(os.path.realpath(__file__))
    net_file= path+'/models/MobileNetSSD_deploy.prototxt'  
    caffe_model=path+'/models/MobileNetSSD_deploy.caffemodel'  
    

    if not os.path.exists(caffe_model):
        print(caffe_model + " does not exist")
        exit()
    if not os.path.exists(net_file):
        print(net_file + " does not exist")
        exit()

    #Load the Caffe model 
    net = cv2.dnn.readNetFromCaffe(net_file, caffe_model)   

    # Labels of Network.
    classNames = { 0: 'background',
        1: 'máy bay', 2: 'xe đạp', 3: 'con chim', 4: 'boat',
        5: 'cái chai', 6: 'xe buýt', 7: 'ô tô', 8: 'con mèo', 9: 'ghế',
        10: 'con bò', 11: 'diningtable', 12: 'con chó', 13: 'con ngựa',
        14: 'xe máy', 15: 'người', 16: 'pottedplant',
        17: 'con cừu', 18: 'ghế sofa', 19: 'train', 20: 'tivi' }

    threshold = 0.6
    origimg = cv2.imread(imgfile)
    # img = preprocess(origimg)
    frame_resized = cv2.resize(origimg,(300,300)) # resize frame for prediction
    # img = img.astype(np.float32)
    # img = img.transpose((2, 0, 1))
    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    #Set to network the input blob 
    net.setInput(blob)
    detections = net.forward()

    #Size of frame resize (300x300)
    cols = frame_resized.shape[1] 
    rows = frame_resized.shape[0]

    #For get the class and location of object detected, 
    # There is a fix index for class, location and confidence
    # value in @detections array .
    # đếm số lượng class có trong hình
    object_dict = {}
    # Thuc hien object detection moi 5 frame
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2] #Confidence of prediction 
        if confidence > threshold: # Filter prediction 
            class_id = int(detections[0, 0, i, 1]) # Class label

            # Object location 
            xLeftBottom = int(detections[0, 0, i, 3] * cols) 
            yLeftBottom = int(detections[0, 0, i, 4] * rows)
            xRightTop   = int(detections[0, 0, i, 5] * cols)
            yRightTop   = int(detections[0, 0, i, 6] * rows)
            
            # Factor for scale to original size of frame
            heightFactor = origimg.shape[0]/300.0  
            widthFactor = origimg.shape[1]/300.0 
            # Scale object detection to frame
            xLeftBottom = int(widthFactor * xLeftBottom) 
            yLeftBottom = int(heightFactor * yLeftBottom)
            xRightTop   = int(widthFactor * xRightTop)
            yRightTop   = int(heightFactor * yRightTop)
            # Draw location of object  
            cv2.rectangle(origimg, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
                        (0, 255, 0))

            # Draw label and confidence of prediction in frame resized
            if class_id in classNames:
                label = classNames[class_id] + ": " + str(confidence)
                if not classNames[class_id] in object_dict:
                    object_dict[ classNames[class_id] ] = 1;
                else :
                    object_dict[ classNames[class_id] ] = int(object_dict[ classNames[class_id] ] )  +1;  

                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                yLeftBottom = max(yLeftBottom, labelSize[1])
                cv2.rectangle(origimg, (xLeftBottom, yLeftBottom - labelSize[1]),
                                    (xLeftBottom + labelSize[0], yLeftBottom + baseLine),
                                    (255, 255, 255), cv2.FILLED)
                cv2.putText(origimg, label, (xLeftBottom, yLeftBottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                    # print(label) #print class and confidence
    print(object_dict)
    # object_dict.clear() 
    # cv2.imshow("SSD", origimg)
    cv2.imwrite("Detected_img.jpg", origimg)
    
    return object_dict
    # k = cv2.waitKey(0) & 0xff
    #     #Exit if ESC pressed
    # if k == 27 : return False
    # return True

# for f in os.listdir(test_dir):
#     if detect(test_dir + "/" + f) == False:
#         break

def detect_family_person( imgfile ):

    path =os.path.dirname(os.path.realpath(__file__))
    # load our serialized face detector from disk
    # print("[INFO] loading face detector...")
    protoPath = path+ "/face_detection_model/deploy.prototxt"
    modelPath =  path+ "/face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

    # load our serialized face embedding model from disk
    print("[INFO] loading face recognizer...")
    embedder = cv2.dnn.readNetFromTorch(path+"/openface_nn4.small2.v1.t7")

    # load the actual face recognition model along with the label encoder
    recognizer = pickle.loads(open(path+"/output/recognizer.pickle", "rb").read())
    le = pickle.loads(open(path+"/output/le.pickle", "rb").read())

    # load the image, resize it to have a width of 600 pixels (while
    # maintaining the aspect ratio), and then grab the image dimensions
    image = cv2.imread( imgfile )
    image = imutils.resize(image, width=600)
    (h, w) = image.shape[:2]

    # construct a blob from the image
    imageBlob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0), swapRB=False, crop=False)

    # apply OpenCV's deep learning-based face detector to localize
    # faces in the input image
    detector.setInput(imageBlob)
    detections = detector.forward()
    object_dict = {}
    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections
        if confidence > 0.8:
            # compute the (x, y)-coordinates of the bounding box for the
            # face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # extract the face ROI
            face = image[startY:endY, startX:endX]
            (fH, fW) = face.shape[:2]

            # ensure the face width and height are sufficiently large
            if fW < 20 or fH < 20:
                continue

            # construct a blob for the face ROI, then pass the blob
            # through our face embedding model to obtain the 128-d
            # quantification of the face
            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96),
                (0, 0, 0), swapRB=True, crop=False)
            embedder.setInput(faceBlob)
            vec = embedder.forward()

            # perform classification to recognize the face
            preds = recognizer.predict_proba(vec)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]

            # nếu tỉ lệ nhận dạng đúng là 75%
            if proba > 0.60:
                object_dict[name] = proba * 100

            # draw the bounding box of the face along with the associated
            # probability
            text = "{}: {:.2f}%".format(name, proba * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(image, (startX, startY), (endX, endY),
                (0, 0, 255), 2)
            cv2.putText(image, text, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    cv2.imwrite("family_person.jpg", image)
    return object_dict