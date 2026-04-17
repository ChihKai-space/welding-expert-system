from flask import Flask, render_template, request

app = Flask(__name__)

# 模擬的資料庫 (加入板厚度，統測完你可以隨意擴充)
WELDING_DATA = {
    "碳鋼": {
        "薄板(1~3mm)": {"1.6": 60, "2.0": 80, "2.6": 90},
        "中厚板(4~6mm)": {"2.6": 100, "3.2": 120, "4.0": 150}
    },
    "不鏽鋼": {
        "薄板(1~3mm)": {"1.6": 55, "2.0": 70, "2.6": 85},
        "中厚板(4~6mm)": {"2.6": 90, "3.2": 110, "4.0": 140}
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            material = request.form.get('material')
            thickness = request.form.get('thickness')
            diameter = request.form.get('diameter')
            user_current_str = request.form.get('user_current', '').strip()
            
            # 1. 尋找系統最佳電流 (加入板厚度與 40 倍備案邏輯)
            recommended_current = None
            calc_method = ""
            
            # 檢查是否有對應的 材質 -> 厚度 -> 直徑 資料
            if (material in WELDING_DATA and 
                thickness in WELDING_DATA[material] and 
                diameter in WELDING_DATA[material][thickness]):
                recommended_current = WELDING_DATA[material][thickness][diameter]
                calc_method = "資料庫建議值"
            else:
                # 如果查不到資料 (範圍外)，啟動 40 倍經驗公式備案
                recommended_current = float(diameter) * 40
                calc_method = "範圍外備案 (直徑 x 40)"

            # 2. 動態生成「電流影響分析表」
            effects_matrix = [
                {"range": f"低於 {recommended_current - 15}A", "effect": "電弧極不穩，極易發生包渣、滲透不足或假銲。"},
                {"range": f"{recommended_current - 15}A ~ {recommended_current - 5}A", "effect": "銲道容易偏高，熔深稍淺，起弧稍微困難。"},
                {"range": f"{recommended_current - 5}A ~ {recommended_current + 5}A", "effect": "最佳參數區間，電弧穩定，銲道平順，滲透良好。"},
                {"range": f"{recommended_current + 5}A ~ {recommended_current + 15}A", "effect": "熔池流動性較大，銲道偏扁平，有輕微咬邊風險。"},
                {"range": f"高於 {recommended_current + 15}A", "effect": "容易造成嚴重咬邊、燒穿、銲道過寬及飛濺過多。"}
            ]

            # 3. 判斷使用者測試電流 (如果有輸入)
            user_current = None
            test_result = None
            test_advice = None
            
            if user_current_str:
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
                "thickness": thickness,
                "diameter": diameter,
                "recommended_current": recommended_current,
                "calc_method": calc_method,
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
