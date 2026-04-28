from flask import Flask, render_template, request

app = Flask(__name__)

# 資料庫：標準工業規格 1.6, 2.4, 3.2
WELDING_DATA = {
    "plate": {
        "carbon": {
            "thin": {"1.6": 60, "2.4": 90, "3.2": 120}, 
            "medium": {"1.6": 80, "2.4": 110, "3.2": 140},
            "thick": {"2.4": 130, "3.2": 160} 
        },
        "stainless": {
            "thin": {"1.6": 55, "2.4": 85, "3.2": 110}, 
            "medium": {"1.6": 70, "2.4": 100, "3.2": 130},
            "thick": {"2.4": 120, "3.2": 150} 
        }
    },
    "pipe": {
        "carbon": {
            "thin": {"1.6": 55, "2.4": 85, "3.2": 110}, 
            "medium": {"1.6": 75, "2.4": 105, "3.2": 135},
            "thick": {"2.4": 125, "3.2": 150} 
        },
        "stainless": {
            "thin": {"1.6": 50, "2.4": 80, "3.2": 105}, 
            "medium": {"1.6": 70, "2.4": 95, "3.2": 125},
            "thick": {"2.4": 115, "3.2": 140} 
        }
    }
}

DICT_EN = {
    "type": {"plate": "Plate", "pipe": "Pipe"},
    "mat": {"carbon": "Carbon Steel", "stainless": "Stainless Steel"},
    "thick": {"thin": "Thin (1~3mm)", "medium": "Medium (4~6mm)", "thick": "Thick (>6mm)"}
}
DICT_ZH = {
    "type": {"plate": "板材", "pipe": "管材"},
    "mat": {"carbon": "碳鋼", "stainless": "不鏽鋼"},
    "thick": {"thin": "薄件 (1~3mm)", "medium": "中厚件 (4~6mm)", "thick": "特殊厚件 (>6mm)"}
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
            
            # --- 後端雙重防呆檢查 ---
            if diameter == "1.6" and thickness == "thick":
                return render_template('index.html', result={"error": "邏輯錯誤：1.6mm 銲條不建議用於厚件銲接 (電流過大易熔損)。"})
            if diameter == "3.2" and thickness == "thin":
                return render_template('index.html', result={"error": "邏輯錯誤：3.2mm 銲條不建議用於薄件銲接 (電弧不穩且易燒穿)。"})

            recommended_current = None
            if (weld_type in WELDING_DATA and 
                material in WELDING_DATA[weld_type] and 
                thickness in WELDING_DATA[weld_type][material] and 
                diameter in WELDING_DATA[weld_type][material][thickness]):
                recommended_current = WELDING_DATA[weld_type][material][thickness][diameter]
            else:
                recommended_current = float(diameter) * 40

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
            
            user_current = None
            test_res_en, test_adv_en = None, None
            test_res_zh, test_adv_zh = None, None
            if user_current_str:
                user_current = float(user_current_str)
                if user_current < recommended_current - 15:
                    test_res_en, test_adv_en = "Critically Low", "Increase current to avoid lack of fusion."
                    test_res_zh, test_adv_zh = "嚴重偏低", "大幅調高電流，避免假銲。"
                elif user_current > recommended_current + 15:
                    test_res_en, test_adv_en = "Critically High", "Risk of burn-through."
                    test_res_zh, test_adv_zh = "嚴重偏高", "極高燒穿風險，請調低。"
                else:
                    test_res_en, test_adv_en = "Optimal", "Standard parameters."
                    test_res_zh, test_adv_zh = "最佳範圍", "符合實務標準。"

            result = {
                "summary_en": f"{DICT_EN['type'].get(weld_type, '')} | {DICT_EN['mat'].get(material, '')} | {DICT_EN['thick'].get(thickness, '')} | {diameter} mm",
                "summary_zh": f"{DICT_ZH['type'].get(weld_type, '')} | {DICT_ZH['mat'].get(material, '')} | {DICT_ZH['thick'].get(thickness, '')} | {diameter} mm",
                "recommended_current": recommended_current,
                "user_current": user_current,
                "en": {"pos": pos_en, "matrix": effects_en, "res": test_res_en, "adv": test_adv_en},
                "zh": {"pos": pos_zh, "matrix": effects_zh, "res": test_res_zh, "adv": test_adv_zh}
            }
        except Exception as e:
            result = {"error": "System Error / 系統錯誤"}
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
