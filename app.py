from flask import Flask, render_template, request

app = Flask(__name__)

# 模擬資料庫
WELDING_DATA = {
    "板材 (Plate)": {
        "碳鋼 (Carbon Steel)": {"薄件 (Thin / 1~3mm)": {"1.6": 60, "2.0": 80, "2.6": 90}, "中厚件 (Medium / 4~6mm)": {"2.6": 100, "3.2": 120, "4.0": 150}},
        "不鏽鋼 (Stainless)": {"薄件 (Thin / 1~3mm)": {"1.6": 55, "2.0": 70, "2.6": 85}, "中厚件 (Medium / 4~6mm)": {"2.6": 90, "3.2": 110, "4.0": 140}},
        "低合金鋼 (Alloy)": {"薄件 (Thin / 1~3mm)": {"1.6": 65, "2.0": 85, "2.6": 95}, "中厚件 (Medium / 4~6mm)": {"2.6": 105, "3.2": 125, "4.0": 155}}
    },
    "管材 (Pipe)": {
        "碳鋼 (Carbon Steel)": {"薄件 (Thin / 1~3mm)": {"1.6": 55, "2.0": 75, "2.6": 85}, "中厚件 (Medium / 4~6mm)": {"2.6": 95, "3.2": 115, "4.0": 140}},
        "不鏽鋼 (Stainless)": {"薄件 (Thin / 1~3mm)": {"1.6": 50, "2.0": 65, "2.6": 80}, "中厚件 (Medium / 4~6mm)": {"2.6": 85, "3.2": 105, "4.0": 130}},
        "低合金鋼 (Alloy)": {"薄件 (Thin / 1~3mm)": {"1.6": 60, "2.0": 80, "2.6": 90}, "中厚件 (Medium / 4~6mm)": {"2.6": 100, "3.2": 120, "4.0": 145}}
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            weld_type = request.form.get('weld_type')
            material = request.form.get('material')
            thickness = request.form.get('thickness')
            diameter = request.form.get('diameter')
            user_current_str = request.form.get('user_current', '').strip()
            
            recommended_current = None
            if (weld_type in WELDING_DATA and 
                material in WELDING_DATA[weld_type] and 
                thickness in WELDING_DATA[weld_type][material] and 
                diameter in WELDING_DATA[weld_type][material][thickness]):
                recommended_current = WELDING_DATA[weld_type][material][thickness][diameter]
            else:
                recommended_current = float(diameter) * 40

            # 英文版資料
            pos_en = {
                "1G (Flat)": f"Base: {recommended_current}A. Good fluidity.",
                "2G (Horizontal)": f"Ref: {int(recommended_current * 0.9)}A. Reduce 10%.",
                "3G (Vertical)": f"Ref: {int(recommended_current * 0.85)}A. Reduce 15%.",
                "4G (Overhead)": f"Ref: {int(recommended_current * 0.85)}A. Keep short arc."
            }
            effects_en = [
                {"range": f"< {int(recommended_current - 15)}A", "effect": "Arc unstable, high risk of slag inclusion."},
                {"range": f"{int(recommended_current - 15)}A ~ {int(recommended_current - 5)}A", "effect": "Narrow bead, shallow penetration."},
                {"range": f"{int(recommended_current - 5)}A ~ {int(recommended_current + 5)}A", "effect": "Optimal range, stable arc."},
                {"range": f"{int(recommended_current + 5)}A ~ {int(recommended_current + 15)}A", "effect": "High fluidity, risk of undercut."},
                {"range": f"> {int(recommended_current + 15)}A", "effect": "Severe undercut, burn-through risk."}
            ]

            # 中文版資料
            pos_zh = {
                "平銲 (1G)": f"基準電流 {recommended_current}A。流動性佳，可獲最大熔深。",
                "橫銲 (2G)": f"約 {int(recommended_current * 0.9)}A (調降10%)。需避免熔池受重力下垂。",
                "立銲 (3G)": f"約 {int(recommended_current * 0.85)}A (調降15%)。需精準控制熔池避免包渣。",
                "仰銲 (4G)": f"約 {int(recommended_current * 0.85)}A (調降15%)。保持短電弧，防止鐵水滴落。"
            }
            effects_zh = [
                {"range": f"低於 {int(recommended_current - 15)}A", "effect": "電弧不穩，極易發生包渣或滲透不足。"},
                {"range": f"{int(recommended_current - 15)}A ~ {int(recommended_current - 5)}A", "effect": "銲道偏高，熔深較淺，起弧稍微困難。"},
                {"range": f"{int(recommended_current - 5)}A ~ {int(recommended_current + 5)}A", "effect": "最佳參數區間，電弧穩定，銲道平順。"},
                {"range": f"{int(recommended_current + 5)}A ~ {int(recommended_current + 15)}A", "effect": "熔池流動快，銲道扁平，有咬邊風險。"},
                {"range": f"高於 {int(recommended_current + 15)}A", "effect": "容易造成嚴重咬邊、燒穿及飛濺。"}
            ]

            # 測試驗證邏輯
            user_current = None
            test_res_en, test_adv_en = None, None
            test_res_zh, test_adv_zh = None, None
            
            if user_current_str:
                user_current = float(user_current_str)
                if user_current < recommended_current - 15:
                    test_res_en, test_adv_en = "Critically Low", "Increase current to avoid lack of fusion."
                    test_res_zh, test_adv_zh = "嚴重偏低", "大幅調高電流，否則極易發生包渣或假銲。"
                elif user_current < recommended_current - 5:
                    test_res_en, test_adv_en = "Slightly Low", "Slightly increase for better penetration."
                    test_res_zh, test_adv_zh = "稍微偏低", "建議稍微調高電流以獲取更好熔深。"
                elif user_current > recommended_current + 15:
                    test_res_en, test_adv_en = "Critically High", "Risk of burn-through. Reduce immediately."
                    test_res_zh, test_adv_zh = "嚴重偏高", "極高風險燒穿或咬邊，請立刻調低。"
                elif user_current > recommended_current + 5:
                    test_res_en, test_adv_en = "Slightly High", "Monitor for undercut and spatter."
                    test_res_zh, test_adv_zh = "稍微偏高", "建議稍微調低，減少飛濺與咬邊風險。"
                else:
                    test_res_en, test_adv_en = "Optimal", "Parameters meet professional standards."
                    test_res_zh, test_adv_zh = "最佳範圍", "設定非常合理，符合實務標準。"

            result = {
                "weld_type": weld_type, "material": material, "thickness": thickness,
                "diameter": diameter, "recommended_current": recommended_current,
                "user_current": user_current,
                "en": {"pos": pos_en, "matrix": effects_en, "res": test_res_en, "adv": test_adv_en},
                "zh": {"pos": pos_zh, "matrix": effects_zh, "res": test_res_zh, "adv": test_adv_zh}
            }
        except Exception as e:
            result = {"error": "System Error / 系統錯誤"}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
