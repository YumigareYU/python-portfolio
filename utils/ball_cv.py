import cv2
import numpy as np
import os


def process_video(input_path, output_filename):
    """
    讀取 input_path 的影片，進行球體辨識，
    將結果存到 static/results/output_filename，
    並回傳相對路徑給 app.py 使用。
    """

    pre, ext = os.path.splitext(output_filename)
    output_filename = pre + ".webm"

    # 設定輸出路徑 (存到 static/results)
    output_dir = os.path.join('static', 'results')
    output_path = os.path.join(output_dir, output_filename)

    cap = cv2.VideoCapture(input_path)

    # 取得影片資訊以設定 VideoWriter
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 設定編碼器 (mp4v 比較通用)
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc = cv2.VideoWriter_fourcc(*'vp80')  # vp80 對應 .webm
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    # fourcc = cv2.VideoWriter_fourcc(*'avc1')
    # out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # --- 您的核心辨識邏輯 (與之前相同) ---
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # 這裡沿用您之前的設定
        lower_pink = np.array([130, 50, 50])
        upper_pink = np.array([175, 255, 255])
        mask = cv2.inRange(hsv, lower_pink, upper_pink)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.erode(mask, None, iterations=1)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area < 100:
                continue

            perimeter = cv2.arcLength(c, True)
            if perimeter == 0:
                continue

            circularity = (4 * np.pi * area) / (perimeter * perimeter)

            if circularity > 0.6:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(frame, (int(x), int(y)),
                           int(radius), (0, 255, 0), 2)
                cv2.putText(frame, f"Ball: {circularity:.2f}", (int(x), int(y)-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # -----------------------------------

        # 寫入影格 (而不是 imshow)
        out.write(frame)

    cap.release()
    out.release()

    # 回傳給網頁用的路徑 (不包含 static，因為 flask url_for 會自動處理)
    return f"results/{output_filename}"
