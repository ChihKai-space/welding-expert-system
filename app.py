from flask import Flask, render_template_string, request

app = Flask(__name__)

# 專業銲接資料庫：整合電流、滲透度與外觀特徵
WELD_LOGIC = {
    "不鏽鋼": {
        "1.2": [
            {"range": (35, 45), "res": "滲透不足", "look": "銲道窄而高凸，未融合", "tip": "電流過低，無法熔透母材，建議加強電流。"},
            {"range": (45, 55), "res": "完美熔透", "look": "金黃色/銀白色魚鱗紋，背面微凸", "tip": "黃金參數！保持穩定行槍速度。"},
            {"range": (55, 100), "res": "嚴重燒穿", "look": "銲道發黑、下塌甚至穿孔", "tip": "電流過大，不鏽鋼熱影響區過大，易產生晶間腐蝕。"}
        ],
        "3.0": [
            {"range": (70, 85), "res": "熔深略顯不足", "look": "銲道表面平整但根部未透", "tip": "建議放慢速度或增加電流 5-10A。"},
            {"range": (85, 105), "res": "深度滲透", "look": "紫色/藍色魚鱗紋，熔池飽滿", "tip": "甲級標準參數，注意填料節奏。"},
            {"range": (105, 150), "res": "過熱氧化", "look": "銲道發黑、表面粗糙無光澤", "tip": "熱量堆積過多，注意冷卻或加快行槍。"}
        ]
    },
    "碳鋼": {
        "3.0": [
            {"range": (80, 95), "res": "滲透普通", "look": "銲道兩側融合不良", "tip": "碳鋼散熱快，電流需適度增加。"},
            {"range": (95, 115), "res": "全熔透", "look": "波紋均勻，邊緣整齊", "tip": "優質銲道，適合結構件使用。"},
            {"range": (115, 160), "res": "咬邊風險", "look": "銲道邊緣產生凹陷溝槽", "tip": "電流過大導致母材過度熔化，需注意槍頭角度。"}
        ]
    }
}

HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>職人級氬銲參數分析系統</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #2c3e50; color: #fff; max-width: 600px; margin: 40px auto; padding: 20px; }
        .card { background: #34495e; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #f1c40f; margin-bottom: 30px; border-bottom: 2px solid #f1c40f; padding-bottom: 10px; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; }
        select, input, button { width: 100%; padding: 12px; border-radius: 8px; border: none; font-size: 16px; margin-bottom: 10px; }
        button { background: #f1c40f; color: #2c3e50; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 15px; }
        button:hover { background: #d4ac0d; transform: scale(1.02); }
        .result-box { margin-top: 25px; padding: 20px; border-radius: 10px; background: #ecf0f1; color: #333; line-height: 1.6; }
        .status { font-weight: bold; font-size: 1.2em; color: #e67e22; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛠️ 氬銲職人診斷系統</h1>
        <form method="POST">
            <label>1. 選擇母材</label>
            <select name="mat">
                <option value="不鏽鋼" {% if mat=='不鏽鋼' %}selected{% endif %}>不鏽鋼 (SUS304/316)</option>
                <option value="碳鋼" {% if mat=='碳鋼' %}selected{% endif %}>普通碳鋼 (SS400)</option>
            </select>
            <label>2. 板材厚度 (mm)</label>
            <select name="thick">
                <option value="1.2" {% if thick=='1.2' %}selected{% endif %}>1.2 mm (薄板)</option>
                <option value="3.0" {% if thick=='3.0' %}selected{% endif %}>3.0 mm (中厚板)</option>
                <option value="6.0" {% if thick=='6.0' %}selected{% endif %}>6.0 mm (厚板)</option>
            </select>
            <label>3. 預計設定電流 (A)</label>
            <input type="number" name="amp" value="{{ amp or 80 }}" placeholder="請輸入電流值">
            <button type="submit">開始製程預測分析</button>
        </form>

        {% if analysis %}
        <div class="result-box">
            <div class="status">📊 預測結果：{{ analysis.res }}</div>
            <hr>
            <p><strong>✨ 表面外觀：</strong><br>{{ analysis.look }}</p>
            <p><strong>💡 職人回饋：</strong><br>{{ analysis.tip }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    analysis = None
    mat = request.form.get("mat")
    thick = request.form.get("thick")
    amp = request.form.get("amp")

    if request.method == "POST" and amp:
        amp_val = float(amp)
        # 尋找匹配的邏輯區間
        specs = WELD_LOGIC.get(mat, {}).get(thick, [])
        for s in specs:
            if s["range"][0] <= amp_val <= s["range"][1]:
                analysis = s
                break
        if not analysis:
            analysis = {"res": "參數超出實驗範圍", "look": "無法精準預測", "tip": "請依甲級技術手冊調整或諮詢現場老師傅。"}

    return render_template_string(HTML, analysis=analysis, mat=mat, thick=thick, amp=amp)

if __name__ == "__main__":
    app.run(debug=True)