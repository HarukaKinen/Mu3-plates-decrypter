import fnmatch
import io
import os
import cv2
import numpy as np

i = 0

os.makedirs("Plates", exist_ok=True)
os.makedirs("Plates/Original", exist_ok=True)
os.makedirs("Plates/Alpha", exist_ok=True)
os.makedirs("Plates/Split", exist_ok=True)

for filename in os.listdir(os.getcwd()):
    if fnmatch.fnmatch(filename, f"UI_UserPlate_*.png"):
        print(f"{filename}...", end="")

        image = cv2.imread(filename)

        b, g, r = cv2.split(image)

        # 原通道的 Grean 是 Y 通道
        y = g

        # 原通道的 Blue 左半边是 U 通道，右半边是 V 通道
        # 拉伸处理过后的 UV 通道图片
        # cv2.resize(img[x:h, y:w], (w, h))
        u = cv2.resize(b[0:296, 0:540], (1080, 296))
        v = cv2.resize(b[0:296, 540:1080], (1080, 296))

        # https://stackoverflow.com/questions/60729170/python-opencv-converting-planar-yuv-420-image-to-rgb-yuv-array-format
        # 开一个基于内存的比特流
        f = io.BytesIO()

        # 把 YUV 通道的图片写入比特流
        f.write(y.tobytes())
        f.write(u.tobytes())
        f.write(v.tobytes())

        # 回到内存的第 0 个索引（回到开头）
        f.seek(0)

        # 读取 YUV 通道并重写为相同长宽的 numpy 数组（行列式）
        # Read Y color channel and reshape to height x width numpy array
        y = np.frombuffer(f.read(y.size), dtype=np.uint8).reshape(
            (y.shape[0], y.shape[1]))
        # Read U color channel and reshape to height x width numpy array
        u = np.frombuffer(f.read(y.size), dtype=np.uint8).reshape(
            (y.shape[0], y.shape[1]))
        # Read V color channel and reshape to height x width numpy array
        v = np.frombuffer(f.read(y.size), dtype=np.uint8).reshape(
            (y.shape[0], y.shape[1]))

        yvu = cv2.merge((y, v, u))

        # YUV 转 BGR
        bgr = cv2.cvtColor(yvu, cv2.COLOR_YCrCb2BGR)

        # BGR 转 BGRA
        bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)

        # 给丫 Alpha 通道干进去
        bgra[:, :, 3] = r

        filename = filename.replace(".png", "")
        cv2.imwrite(f"./Plates/Original/{filename}.png", bgr)
        cv2.imwrite(f"./Plates/Alpha/{filename}.png", bgra)
        cv2.imwrite(f"./Plates/Split/{filename}_Upper.png", bgra[:168, :])
        cv2.imwrite(f"./Plates/Split/{filename}_Lower.png", bgra[168:, :])

        i += 1

        print("Done")

if i != 0:
    print(f"{i} plates processed.")
else:
    print(f"Can't find any plates. Make sure you have placed exe file in the directory where you need to decrypt plates.")

os.system('pause')
