import os
from flask import Flask, render_template, request, redirect, url_for
from utils.ball_cv import process_video  # 匯入剛剛寫的模組
from utils.stock_api import get_stock_plot

app = Flask(__name__)

# 設定上傳存檔路徑
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 確保資料夾存在


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


# 新增：滾球專案的路由
@app.route('/portfolio/ball-tracking', methods=['GET', 'POST'])
def ball_tracking():
    if request.method == 'POST':

        input_filepath = None
        output_filename = None
        original_url = None

        # 情況 A: 使用者點擊「使用範本影片」
        if request.form.get('source_type') == 'template':
            filename = "範本.mp4"
            input_filepath = os.path.join(UPLOAD_FOLDER, filename)

            # 防呆：檢查範本是否存在
            if not os.path.exists(input_filepath):
                return "錯誤：找不到範本影片，請確認 static/uploads/範本.mp4 是否存在。"

            output_filename = "processed_template.mp4"  # 或 .webm
            original_url = f"uploads/{filename}"

        # 情況 B: 使用者上傳檔案
        elif 'video_file' in request.files:
            file = request.files['video_file']
            if file.filename == '':
                return "沒有選擇檔案"

            if file:
                input_filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(input_filepath)

                output_filename = "processed_" + file.filename
                original_url = f"uploads/{file.filename}"

        # 如果有取得輸入路徑，就開始處理
        if input_filepath and output_filename:
            # 呼叫您的辨識功能
            result_video_path = process_video(input_filepath, output_filename)

            return render_template('ball_tracking.html',
                                   original=original_url,
                                   result=result_video_path)

    return render_template('ball_tracking.html', original=None, result=None)


# 新增：股票
@app.route('/portfolio/stock-analysis', methods=['GET', 'POST'])
def stock_analysis():
    graph_json = None
    error = None

    if request.method == 'POST':
        ticker = request.form.get('ticker', '').upper().strip()  # 轉大寫並去空白
        if ticker:
            graph_json, error = get_stock_plot(ticker)

    return render_template('stock_analysis.html', graph_json=graph_json, error=error)


if __name__ == '__main__':
    # app.run(debug=True)
    # 記得要把 debug 改成 False，或是不要寫 port 設定，讓雲端自動決定
    app.run(host='0.0.0.0', port=5000)
