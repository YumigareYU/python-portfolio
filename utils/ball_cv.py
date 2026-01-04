import cv2
import numpy as np
import os


def process_video(input_path, output_filename):
    """
    優化版：強制縮小影片尺寸以節省 Render 記憶體，並輸出為 WebM
    """
    # 設定輸出檔名 (.webm)
    name_no_ext, _ = os.path.splitext(output_filename)
    new_filename = name_no_ext + ".webm"

    # 設定輸出路徑
    output_dir = os.path.join('static', 'results')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, new_filename)

    cap = cv2.VideoCapture(input_path)

    # --- 【關鍵修改 1】取得原始尺寸，計算縮放比例 ---
    # 我們強制把寬度縮小到 640 像素 (對 OpenCV 來說很夠用了)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    target_width = 640
    # 計算等比例的高度
    aspect_ratio = original_height / original_width
    target_height = int(target_width * aspect_ratio)

    fps = cap.get(cv2.CAP_PROP_FPS)

    # --- 【關鍵修改 2】Writer 使用「縮小後」的尺寸 ---
    fourcc = cv2.VideoWriter_fourcc(*'vp80')
    out = cv2.VideoWriter(output_path, fourcc, fps,
                          (target_width, target_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # --- 【關鍵修改 3】在處理前，先縮小畫面！(省記憶體救星) ---
        frame = cv2.resize(frame, (target_width, target_height))

        # --- 以下辨識邏輯維持不變 ---
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

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

            if circularity > 0.8:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(frame, (int(x), int(y)),
                           int(radius), (0, 255, 0), 2)
                cv2.putText(frame, f"Ball: {circularity:.2f}", (int(x), int(y)-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 寫入縮小後的 Frame
        out.write(frame)

    cap.release()
    out.release()

    return f"results/{new_filename}"
