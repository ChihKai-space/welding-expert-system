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

            # 銲接位置建議 (Bilingual)
            position_advice = {
                "平銲 (Flat / 1G)": f"Base: {recommended_current}A. Good fluidity.",
                "橫銲 (Horizontal / 2G)": f"Ref: {int(recommended_current * 0.9)}A. Reduce 10%.",
                "立銲 (Vertical / 3G)": f"Ref: {int(recommended_current * 0.85)}A. Reduce 15%.",
                "仰銲 (Overhead / 4G)": f"Ref: {int(recommended_current * 0.85)}A. Keep short arc."
            }

            effects_matrix = [
                {"range": f"< {int(recommended_current - 15)}A", "effect": "Arc unstable, high risk of slag inclusion."},
                {"range": f"{int(recommended_current - 15)}A ~ {int(recommended_current - 5)}A", "effect": "Narrow bead, shallow penetration."},
                {"range": f"{int(recommended_current - 5)}A ~ {int(recommended_current + 5)}A", "effect": "Optimal range, stable arc."},
                {"range": f"{int(recommended_current + 5)}A ~ {int(recommended_current + 15)}A", "effect": "High fluidity, risk of undercut."},
                {"range": f"> {int(recommended_current + 15)}A", "effect": "Severe undercut, burn-through risk."}
            ]

            user_current = None
            test_result = None
            test_advice = None
            if user_current_str:
                user_current = float(user_current_str)
                if user_current < recommended_current - 15:
                    test_result = "Critically Low / 嚴重偏低"
                    test_advice = "Increase current to avoid lack of fusion."
                elif user_current < recommended_current - 5:
                    test_result = "Slightly Low / 稍微偏低"
                    test_advice = "Slightly increase for better penetration."
                elif user_current > recommended_current + 15:
                    test_result = "Critically High / 嚴重偏高"
                    test_advice = "Risk of burn-through. Reduce immediately."
                elif user_current > recommended_current + 5:
                    test_result = "Slightly High / 稍微偏高"
                    test_advice = "Monitor for undercut and spatter."
                else:
                    test_result = "Optimal / 最佳範圍"
                    test_advice = "Parameters meet professional standards."

            result = {
                "weld_type": weld_type, "material": material, "thickness": thickness,
                "diameter": diameter, "recommended_current": recommended_current,
                "position_advice": position_advice, "effects_matrix": effects_matrix,
                "user_current": user_current, "test_result": test_result, "test_advice": test_advice
            }
        except Exception as e:
            result = {"error": "System Error / 系統錯誤"}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
