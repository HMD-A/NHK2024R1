import cv2
import numpy as np
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from matplotlib import pyplot as plt
from ultralytics import YOLO
import ctypes
import time
import statistics
import pyautogui as pag




# Kinect V2の初期化
kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth)
# ICoordinateMapperの取得
coordinate_mapper = kinect._mapper

model = YOLO("C:/Users/Robotism/ultralytics/runs/detect/train/weights/best.pt")

def color_point_2_depth_point(kinect, depth_space_point, depth_frame_data, color_point):
    """

    :param kinect: kinect class
    :param depth_space_point: _DepthSpacePoint from PyKinectV2
    :param depth_frame_data: kinect._depth_frame_data
    :param color_point: color_point pixel location as [x, y]
    :return: depth point of color point
    """
    # Map Color to Depth Space
    # Make sure that the kinect was able to obtain at least one color and depth frame, else the dept_x and depth_y values will go to infinity
    color2depth_points_type = depth_space_point * int(1920 * 1080)
    color2depth_points = ctypes.cast(color2depth_points_type(), ctypes.POINTER(depth_space_point))
    kinect._mapper.MapColorFrameToDepthSpace(ctypes.c_uint(512 * 424), depth_frame_data, ctypes.c_uint(1920 * 1080), color2depth_points)
    # Where color_point = [xcolor, ycolor]
    depth_x = color2depth_points[color_point[1] * 1920 + color_point[0] - 1].x
    depth_y = color2depth_points[color_point[1] * 1920 + color_point[0] - 1].y
    return [int(depth_x) if depth_x != float('-inf') and depth_x != float('inf') else 0, int(depth_y) if depth_y != float('-inf') and depth_y != float('inf') else 0]

def depth_point_2_world_point(kinect, depth_space_point, depthPoint, depth):
    """

    :param kinect: kinect class
    :param depth_space_point: _DepthSpacePoint from PyKinectV2
    :param depthPoint: depth point as array [x, y]
    :return: return the camera space point
    """

    depth_point_data_type = depth_space_point * int(1)
    depth_point = ctypes.cast(depth_point_data_type(), ctypes.POINTER(depth_space_point))
    depth_point.contents.x = depthPoint[0]
    depth_point.contents.y = depthPoint[1]
    world_point = kinect._mapper.MapDepthPointToCameraSpace(depth_point.contents, ctypes.c_uint16(depth))
    return [world_point.x, world_point.y, world_point.z]

def depth_points_2_camera_points(kinect, depth_space_point, camera_space_point, xys, as_array=False):
    """
    :param kinect: kinect class
    :param depth_space_point: _DepthSpacePoint
    :param camera_space_point: _CameraSpacePoint
    :return camera space points as camera_points[y*512 + x].x/y/z
    """
    
    length_of_points = len(xys)
    depth_points_type = depth_space_point * int(length_of_points)
    depth_points = ctypes.cast(depth_points_type(), ctypes.POINTER(depth_space_point))
    camera_points_type = camera_space_point * int(length_of_points)
    camera_points = ctypes.cast(camera_points_type(), ctypes.POINTER(camera_space_point))
    depths = ctypes.POINTER(ctypes.c_ushort) * int(length_of_points)
    depths = ctypes.cast(depths(), ctypes.POINTER(ctypes.c_ushort))
    for i, point in enumerate(xys):
        depth_points[i].x = point[0]
        depth_points[i].y = point[1]
    kinect._mapper.MapDepthPointsToCameraSpace(ctypes.c_uint(length_of_points), depth_points, ctypes.c_uint(length_of_points), depths, ctypes.c_uint(length_of_points), camera_points)
    if as_array:
        camera_points = ctypes.cast(camera_points, ctypes.POINTER(ctypes.c_float))
        camera_points = np.ctypeslib.as_array(camera_points, shape=(length_of_points, 3))
        return camera_points
    return camera_points

indexNo = 0
while True:
    # カラー画像とデプス画像を取得
    if kinect.has_new_color_frame():
        color_frame = kinect.get_last_color_frame()
        depth_frame = kinect.get_last_depth_frame()

        # カラー画像の表示
        color_image = color_frame.reshape((kinect.color_frame_desc.Height, kinect.color_frame_desc.Width, 4))
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
        #color_image = cv2.flip(color_image,1)

        results = model.predict(color_image,verbose=False)
        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        #cv2.imshow('Color Image', color_image)

        # デプス画像の表示
        depth_image = depth_frame.reshape((kinect.depth_frame_desc.Height, kinect.depth_frame_desc.Width)).astype(np.uint16)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)
        #depth_colormap = cv2.flip(depth_colormap,1)
        

        # キャプチャした画像サイズを取得
        imageWidth = results[0].orig_shape[0]
        imageHeight = results[0].orig_shape[1]

		# 後のオブジェクト名出力などのため
        names = results[0].names
        classes = results[0].boxes.cls
        boxes = results[0].boxes

		# 検出したオブジェクトのバウンディングボックス座標とオブジェクト名を取得し、ターミナルに出力
        for box, cls in zip(boxes, classes):
            name = names[int(cls)]
            x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]
            avex = int((x1+x2)/2)
            avey = int((y1+y2)/2)
            aroundx = int(abs(x2-x1)/4)
            aroundy = int(abs(y2-y1)/4)
            x1 += aroundx
            y1 += aroundy
            x2 -= aroundx
            y2 -= aroundy
            dx1,dy1 = color_point_2_depth_point(kinect,_DepthSpacePoint,kinect._depth_frame_data,(x1,y1))
            dx2,dy2 = color_point_2_depth_point(kinect,_DepthSpacePoint,kinect._depth_frame_data,(x2,y2))
            
            if dx1 != 0 and dx2 != 0 and dy1 != 0 and dy2 != 0:
                cv2.rectangle(depth_colormap,(dx1,dy1),(dx2,dy2),(255,255,0))

                trim = depth_image[ dx1  : dx2 , dy1  : dy2 ]
                trim = trim[trim>0]
                #trim_depth = statistics.mode(trim.flatten())

                world_depths = []
                for i in range(dx1,dx2,1):
                    for j in range(dy1,dy2,1):
                        var = depth_point_2_world_point(kinect,_DepthSpacePoint,(i,j),depth_image[j,i])
                        if(float('-inf') not in var):
                            world_depths.append(var)

                world_depth_np = np.array(world_depths)
                world_point = np.mean(world_depth_np,axis=0)
                print(world_point)
                            
                #world_depths = np.array(world_depths)
                #world_depths = world_depths[world_depths>0]
                #world_depth = statistics.mode(world_depths.flatten())
                
                
                #print(trim_depth,world_depth)

            if cv2.waitKey(1) & 0xFF == ord('p'):
                plt.hist(trim.flatten(), bins=250, range=(0, 20000), color="red", alpha=0.7)
                plt.title('Histogram_trim')
                plt.xlabel('Value')
                plt.ylabel('Frequency')
                plt.grid(True)

                plt.show()

                cv2.imwrite("trim.png",depth_colormap)

			# バウンディングBOXの座
            # 標情報を書き込む
            #cv2.putText(annotatedFrame, f"{x1} {y1} {x2} {y2}", (x1, y1 - 40), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow('Depth Image', depth_colormap)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        time.sleep(0.1)

# 終了処理
kinect.close()
cv2.destroyAllWindows()



