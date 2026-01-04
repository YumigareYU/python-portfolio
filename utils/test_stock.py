import yfinance as yf

# 測試兩支股票：一支美股，一支台股
tickers = ["AAPL", "2330.TW"]

print("正在測試連線到 Yahoo Finance...")

for t in tickers:
    print(f"\n--- 測試代號: {t} ---")
    try:
        stock = yf.Ticker(t)
        # 嘗試抓取最近 5 天的資料
        df = stock.history(period="5d")

        if df.empty:
            print(f"❌ 失敗: 抓不到 {t} 的資料 (Empty DataFrame)")
        else:
            print(f"✅ 成功! 抓到 {len(df)} 筆資料")
            print(df.head())  # 印出前幾筆看看

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
