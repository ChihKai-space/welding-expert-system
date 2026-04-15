from flask import Flask, render_template, request

app = Flask(__name__)

# 模擬的資料庫 (WELDING_DATA)
WELDING_DATA = {
    "碳鋼": {"1.6": 60, "2.0": 80, "2.6": 100, "3.2": 120},
    "不鏽鋼": {"1.6": 55, "2.0": 75, "2.6": 90, "3.2": 110}
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            material = request.form.get('material')
            diameter = request.form.get('diameter')
            user_current_str = request.form.get('user_current', '').strip()
            
            # 1. 尋找系統最佳電流
            recommended_current = None
            if material in WELDING_DATA and diameter in WELDING_DATA[material]:
                recommended_current = WELDING_DATA[material][diameter]
            else:
                # 如果選了特殊尺寸查不到資料，啟動 40 倍經驗公式備案
                recommended_current = float(diameter) * 40

            # 2. 動態生成「電流影響分析表」
            effects_matrix = [
                {"range": f"低於 {recommended_current - 15}A", "effect": "電弧極不穩，極易發生包渣、滲透不足或假銲。"},
                {"range": f"{recommended_current - 15}A ~ {recommended_current - 5}A", "effect": "銲道容易偏高，熔深稍淺，起弧稍微困難。"},
                {"range": f"{recommended_current - 5}A ~ {recommended_current + 5}A", "effect": "最佳參數區間，電弧穩定，銲道平順，滲透良好。"},
                {"range": f"{recommended_current + 5}A ~ {recommended_current + 15}A", "effect": "熔池流動性較大，銲道偏扁平，有輕微咬邊風險。"},
                {"range": f"高於 {recommended_current + 15}A", "effect": "容易造成嚴重咬邊、燒穿、銲道過寬及飛濺過多。"}
            ]

            # 3. 判斷使用者測試電流 (如果有輸入的話)
            user_current = None
            test_result = None
            test_advice = None
            
            if user_current_str: # 如果字串不是空的，代表使用者有輸入
                user_current = float(user_current_str)
                lower_limit = recommended_current - 5
                upper_limit = recommended_current + 5
                
                if user_current < recommended_current - 15:
                    test_result = "嚴重偏低"
                    test_advice = "請大幅調高電流，否則極易包渣。"
                elif user_current < lower_limit:
                    test_result = "稍微偏低"
                    test_advice = "建議稍微調高電流，以獲得更好的熔深。"
                elif user_current > recommended_current + 15:
                    test_result = "嚴重偏高"
                    test_advice = "極高風險燒穿或咬邊，請立刻調低電流。"
                elif user_current > upper_limit:
                    test_result = "稍微偏高"
                    test_advice = "建議稍微調低，減少飛濺與咬邊風險。"
                else:
                    test_result = "最佳範圍"
                    test_advice = "設定非常完美，請保持此參數進行銲接。"

            result = {
                "material": material,
                "diameter": diameter,
                "recommended_current": recommended_current,
                "effects_matrix": effects_matrix,
                "user_current": user_current,
                "test_result": test_result,
                "test_advice": test_advice
            }
        except Exception as e:
            result = {"error": "系統發生錯誤，請確認數值格式是否正確。"}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
