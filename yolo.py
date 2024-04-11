import cv2
from ultralytics import YOLO
import time


MODEL="yolov8m_rc24"
model = YOLO(MODEL+'.pt') # ここのモデルを変更すると別の認識modelになります。ただし、トラッキングは別です。

# Export the model
#model.export(format='openvino')  # creates 'yolov8n_openvino_model/'

# Load the exported OpenVINO model
#model = YOLO(MODEL+'_openvino_model/')


# Open the web camera stream
cap = cv2.VideoCapture(0) # サンプルからここだけ変更するだけ

c=0
t=0.
while cap.isOpened():
    success, frame = cap.read()
    k = cv2.waitKey(1) # 一応キー入力で終了できるようにしておく

    if k != -1:
        break
    if success:
        c+=1
        t0=time.perf_counter()

        results = model.predict(frame,verbose=False)

        t+=time.perf_counter()-t0
        if(c>=10):
            print("%.1ffps %.1fms "%(c/t,1000*t/c))
            c=0
            t=0.

        #print(results[0])
        annotated_frame = results[0].plot()

        cv2.imshow("YOLOv8 Inference", annotated_frame)
cap.release()
cv2.destroyAllWindows()