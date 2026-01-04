import cv2
import numpy as np
import os


def process_video(input_path, output_filename):
    """
    讀取影片，進行辨識，並強制轉存為 .webm 格式 (Linux/Web 最佳容錯方案)
    """

    # 1. 【關鍵修改】強制把副檔名改成 .webm
    # 不管原本傳進來是 .mp4 還是 .avi，輸出都變成 .webm
    name_no_ext, _ = os.path.splitext(output_filename)
    new_filename = name_no_ext + ".webm"

    # 設定輸出路徑
    output_dir = os.path.join('static', 'results')
    # 確保資料夾存在 (雲端環境有時候需要這行)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, new_filename)

    cap = cv2.VideoCapture(input_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 2. 【關鍵修改】改用 VP8 編碼器 (對應 .webm)
    # 這是 Linux 伺服器最安全的選擇
    fourcc = cv2.VideoWriter_fourcc(*'vp80')

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # --- 影像處理邏輯 (維持原本的樣子) ---
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

            if circularity > 0.6:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(frame, (int(x), int(y)),
                           int(radius), (0, 255, 0), 2)
                cv2.putText(frame, f"Ball: {circularity:.2f}", (int(x), int(y)-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # -----------------------------------

        out.write(frame)

    cap.release()
    out.release()

    # 3. 回傳新的檔名 (.webm) 給 app.py
    return f"results/{new_filename}"
