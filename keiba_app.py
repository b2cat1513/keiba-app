import streamlit as st
import pandas as pd
import json
from streamlit.components.v1 import html

# --- [新ジョッキー事典・大幅拡充マスターデータ] ---
JOCKEY_MASTER = {
    "C.ルメール": {"base": 1.35, "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "長距離": 0.05, "東京": 0.15, "芝2400以上": 0.15, "重賞8枠": 0.15, "中山": -0.15}, "note": "東京・長距離・重賞8枠◎。勝負強さ現役No.1"},
    "川田将雅": {"base": 1.35, "factors": {"芝1枠": 0.15, "小回り2000": 0.15, "交流重賞": 0.15, "長距離": -0.05}, "note": "芝1枠・小回り・交流重賞◎。確勝級の馬での信頼度抜群"},
    "坂井瑠星": {"base": 1.25, "factors": {"先行": 0.10, "内枠": 0.05, "ダート重賞": 0.15}, "note": "逃げ先行・ダート重賞◎。海外・大舞台での積極策光る"},
    "武豊": {"base": 1.20, "factors": {"芝": 0.05, "継続騎乗": 0.15, "人気薄": 0.15, "距離延長": 0.15}, "note": "継続騎乗・大舞台での一発◎。レジェンドのペース配分は健在"},
    "松山弘平": {"base": 1.15, "factors": {"ダート": 0.15, "新馬戦": 0.15, "前哨戦": 0.15}, "note": "ダート・新馬戦◎。非常に堅実で、乗り替わりも苦にしない"},
    "岩田望来": {"base": 1.10, "factors": {"マイル以下の差し": 0.15, "乗り替わり": 0.15}, "note": "乗り替わり・マイル以下の差し○。平場・特別戦での安定感高い"},
    "西村淳也": {"base": 1.10, "factors": {"京都芝": 0.15, "先行": 0.05}, "note": "京都芝・先行策◎。G1でも穴を明ける度胸あり"},
    "団野大成": {"base": 1.10, "factors": {"短距離重賞": 0.15, "荒れ馬場": 0.15}, "note": "短距離重賞・荒れた芝◎。勝負どころでの思い切りの良さ魅力"},
    "鮫島克駿": {"base": 1.10, "factors": {"イン突き": 0.15, "中長距離": 0.15, "ダート外枠": 0.15}, "note": "好位イン突き・中長距離◎。ロス性能の高い立ち回りが得意"},
    "藤岡佑介": {"base": 1.10, "factors": {"自在性": 0.15, "重賞の人気馬": -0.15}, "note": "展開読み◎（展開アドバイザー）。重賞人気馬はやや割引"},
    "幸英明": {"base": 1.05, "factors": {"ダート": 0.15, "牡馬のタフ条件": 0.15}, "note": "タフなダート戦・牡馬◎。とにかくタフで騎乗数も多い"},
    "池添謙一": {"base": 1.15, "factors": {"大舞台＆重賞": 0.15, "差し＆追い込み": 0.15}, "note": "G1・重賞での勝負強さ抜群。人気薄のグランプリで激走"},
    "岩田康誠": {"base": 1.15, "factors": {"重賞": 0.15, "内枠": 0.15}, "note": "内枠からのイン突き強襲◎。ベテランのイン攻め注意"},
    "M.デムーロ": {"base": 1.15, "factors": {"大舞台＆重賞": 0.15, "追い込み": 0.15}, "note": "出遅れケア必要も、大舞台でのマクリ・追い込みは破壊力あり"},
    "浜中俊": {"base": 1.05, "factors": {"芝": 0.05, "1番人気": 0.15}, "note": "芝の短〜中距離・人気馬○。乗れている時の爆発力あり"},
    "北村友一": {"base": 1.10, "factors": {"芝8枠": 0.15, "中長距離戦": 0.15}, "note": "外枠からの差し・中長距離○。復活後の大舞台でも健闘"},
    "横山典弘": {"base": 1.15, "factors": {"芝内枠": 0.15, "継続騎乗": 0.15}, "note": "ポツン注意も内枠・継続◎。馬の気分に合わせた一発あり"},
    "和田竜二": {"base": 1.05, "factors": {"荒れ馬場": 0.15, "先行": 0.05}, "note": "追えるベテラン。タフな消耗戦やズブい馬で真価発揮"},
    "高杉吏麒": {"base": 1.05, "factors": {"減量活かした先行": 0.15, "ローカル": 0.10, "短距離": 0.05}, "note": "急成長中の若手。減量を活かした積極策やローカルでの穴に警戒"},
    "永島まなみ": {"base": 1.05, "factors": {"ダート": 0.15, "先行": 0.10}, "note": "ローカルやダートの逃げ・先行は無類の強さ"},
    "田口貫太": {"base": 1.05, "factors": {"ダート": 0.15, "芝1枠": 0.15}, "note": "減量ブレイクから定着した若手。ダート人気馬・イン戦◎"},
    "古川吉洋": {"base": 1.00, "factors": {"先行": 0.10}, "note": "穴の逃げ・先行で警戒が必要なベテラン"},
    "松若風馬": {"base": 1.05, "factors": {"逃げ": 0.15, "ダート": 0.05}, "note": "積極的な逃げ・先行策が持ち味。ダート○"},
    "荻野極": {"base": 1.00, "factors": {"短距離": 0.10}, "note": "ローカルの短距離戦などで一発を秘める"},
    "小沢大仁": {"base": 1.00, "factors": {"ローカル": 0.10}, "note": "若手の中でもローカル開催で着実に着を拾うタイプ"},
    "今村聖奈": {"base": 1.00, "factors": {"逃げ": 0.10, "芝": 0.05}, "note": "軽斤量を活かした前残り・ローカル芝で警戒"},
    "吉村誠之助": {"base": 1.00, "factors": {"ダート": 0.10}, "note": "期待の若手。ダート戦や減量を活かした競馬で台頭"},

    # === 美浦（関東）所属・主要＆実力派 ===
    "戸崎圭太": {"base": 1.25, "factors": {"前走ルメール": 0.15, "ダート外枠": 0.15, "東京1600": 0.15, "重賞": 0.10}, "note": "東京マイル・ダート外枠・前走ルメールからの乗り替わり◎"},
    "横山武史": {"base": 1.25, "factors": {"中山重賞": 0.15, "先行": 0.10, "持久力戦": 0.15}, "note": "中山重賞・先行持久力戦◎。関東のエース格"},
    "菅原明良": {"base": 1.15, "factors": {"長距離": 0.10, "差し": 0.05}, "note": "G1制覇を経て大舞台の信頼度UP。穴を明ける長距離差し"},
    "佐々木大輔": {"base": 1.15, "factors": {"芝内枠": 0.15, "函館札幌": 0.15}, "note": "若手屈指の立ち回り。内枠＆北海道（函館・札幌）の鬼"},
    "丹内祐次": {"base": 1.10, "factors": {"ローカル": 0.15, "芝": 0.05}, "note": "ローカル（函館・札幌・小倉等）の帝王。人気薄の激走多数"},
    "田辺裕信": {"base": 1.10, "factors": {"長距離戦": 0.15, "逃げ": 0.10}, "note": "人気薄の大胆な逃げや、ポツン差しなどノリに勝る奇策注意"},
    "横山和生": {"base": 1.15, "factors": {"ダート重賞": 0.15, "長距離戦": 0.10}, "note": "長距離の逃げ・先行や、ダート重賞での信頼度高"},
    "津村明秀": {"base": 1.10, "factors": {"直線競馬": 0.15, "左回り": 0.05}, "note": "新潟直線1000m◎。G1制覇後、勝負強さが一段と増した"},
    "三浦皇成": {"base": 1.05, "factors": {"1番人気": 0.15, "重賞": -0.15}, "note": "平場・条件戦の1番人気は堅実。重賞ではやや割引"},
    "大野拓哉": {"base": 1.05, "factors": {"ダートの外枠": 0.15, "追い込み": 0.15}, "note": "ダート外枠の追い込み穴馬で強烈な追い込みを見せる"},
    "石川裕紀人": {"base": 1.10, "factors": {"芝1枠": 0.15, "積極策": 0.10}, "note": "大舞台での思い切った先行策・イン突きの魅力あり"},
    "北村宏司": {"base": 1.05, "factors": {"東京芝": 0.10, "内枠": 0.10}, "note": "ベテランの安定感。東京の芝コースや内枠での立ち回り○"},
    "木幡巧也": {"base": 1.00, "factors": {"ダート逃げ": 0.10}, "note": "ダート戦での積極的な前残り・単勝妙味あり"},
    "石橋脩": {"base": 1.05, "factors": {"先行": 0.10, "中山": 0.05}, "note": "ベテランの先行押し切り。中山などタフなコースで注意"},
    "柴田善臣": {"base": 1.00, "factors": {"人気薄": 0.10}, "note": "現役最年長レジェンド。時折見せる絶妙な差し込み注意"},
    "丸山元気": {"base": 1.00, "factors": {"ローカル": 0.05}, "note": "ローカル開催の特別戦などで伏兵を上位に持ってくる"},

    # === 短期免許外国人・地方・その他エリア ===
    "J.モレイラ": {"base": 1.35, "factors": {"中長距離": 0.15, "ダート": 0.10}, "note": "マジックマン。短期免許で来日時は勝率・連対率が異次元"},
    "D.レーン": {"base": 1.30, "factors": {"重賞": 0.15, "芝": 0.10}, "note": "追って伸びる。日本の馬場適性が非常に高くG1での信頼度絶大"},
    "R.キング": {"base": 1.25, "factors": {"先行": 0.15, "内枠": 0.10}, "note": "抜群のスタートセンスと好位キープ力で前残り連発"},
    "T.マーカンド": {"base": 1.20, "factors": {"ダート": 0.15, "荒れ馬場": 0.10}, "note": "剛腕。タフな馬場やダート戦での追い比べは無類の強さ"},
    "H.ドイル": {"base": 1.15, "factors": {"先行": 0.10, "芝": 0.05}, "note": "ロンドン新星。好位からの手堅い立ち回りが光る"},
    "短期免許外国人": {"base": 1.20, "factors": {"重賞": 0.10}, "note": "その他短期免許の外国人騎手。有力馬配置が多く一律高評価"},
    "地方所属騎手": {"base": 1.05, "factors": {"ダート": 0.15}, "note": "大井・川崎などの地方所属（御神本・笹川等）。ダート戦◎"},
    
    # === 例外・予備 ===
    "その他（自由手入力）": {"base": 1.00, "factors": {}, "note": "リスト外の騎手です。右の入力欄に名前を記入してください。"}
}
   

COURSE_MASTER = {
    "東京芝1600m": {"note": "重賞は差し・追い込み有利。ロードカナロア/エピファネイア/モーリス産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス"]},
    "東京芝2000m": {"note": "【2024-2026G1傾向: 1桁馬番(①〜⑧)が超強力】1枠有利。前走同距離＆距離短縮が好走。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "モーリス", "キズナ", "キタサンブラック"]},
    "東京芝2400m": {"note": "【2024-2026G1傾向: 内〜中枠の立ち回り重視】前走速い脚を使った先行・差しが健闘。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ドゥラメンテ", "ハービンジャー"]},
    "東京ダート1600m": {"note": "外枠有利。ヘニーヒューズ/ドレフォン○。馬体重480kg以上○", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "ロードカナロア"]},
    "中山芝2000m": {"note": "荒れ馬場は外差し○。エピファネイア/ハービンジャー/モーリス○", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "ハービンジャー", "モーリス"]},
    "中山芝2500m": {"note": "【2024-2026G1傾向: 有馬記念は1桁馬番の勝率突出】高速馬場は内枠、荒れ馬場は外枠有利。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キズナ", "ドゥラメンテ", "ゴールドシップ"]},
    "阪神芝1600m": {"note": "内枠有利。高速馬場は外差し、ロードカナロア/エピファネイア産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "キズナ"]},
    "阪神芝2000m": {"note": "外枠の先行馬有利。大阪杯は内差し。ドゥラメンテ/ルーラーシップ○", "track": "芝", "dist": "中距離", "good_lineage": ["ドゥラメンテ", "ルーラーシップ", "キズナ"]}
}

st.set_page_config(page_title="競馬予想・ジョッキー＆コース事典完全版", layout="wide")
st.title("🏇 競馬予想・ジョッキー＆コース事典 【バグ修正完了版】")

if "loaded_data" not in st.session_state:
    st.session_state["loaded_data"] = None

query_params = st.query_params
if "loaded_json" in query_params:
    try:
        st.session_state["loaded_data"] = json.loads(query_params["loaded_json"])
        st.query_params.clear()
    except:
        pass

# --- 🗺️ コース選択 ---
st.header("🗺️ コース選択")
saved_course = st.session_state["loaded_data"].get("course", "(未選択)") if st.session_state["loaded_data"] else "(未選択)"
sel_course = st.selectbox("レースが行われるコースを選択してください:", ["(未選択)"] + list(COURSE_MASTER.keys()), index=(["(未選択)"] + list(COURSE_MASTER.keys())).index(saved_course) if saved_course in COURSE_MASTER else 0)

auto_track, auto_dist, good_blood_list = "設定なし", "設定なし", []
if sel_course != "(未選択)":
    c_info = COURSE_MASTER[sel_course]
    st.info(f"**【{sel_course} の特徴・有力血統】**\n\n{c_info['note']}")
    auto_track, auto_dist, good_blood_list = c_info["track"], c_info["dist"], c_info["good_lineage"]

st.divider()

# --- 📋 出馬表入力エリア ---
st.write("### 📝 出馬表データ入力（18頭フル対応・複数特記セレクト機能付き）")

save_cols = st.columns([2, 2, 8])
with save_cols[0]:
    save_clicked = st.button("📥 入力内容をスマホに一時保存", use_container_width=True)
with save_cols[1]:
    load_clicked = st.button("📤 保存したデータを読み込む", use_container_width=True, type="secondary")

calculated_results = []

c_widths = [0.6, 1.4, 0.6, 0.6, 0.9, 1.4, 1.8, 1.2, 0.9, 0.9, 0.9, 0.9, 1.1, 1.1, 1.1, 1.1, 0.9]
cols = st.columns(c_widths)
headers = ["馬番", "馬名", "人気", "指数", "前3F", "父馬", "騎手選択", "手入力用", "馬場", "脚質", "枠順", "距離", "⑤プラス①", "⑤プラス②", "⑥マイナス①", "⑥マイナス②", "スコア"]
for col, h in zip(cols, headers):
    col.write(f"**{h}**")

current_inputs = {"course": sel_course, "rows": {}}

for i in range(1, 19):
    c = st.columns(c_widths)
    s_row = st.session_state["loaded_data"].get("rows", {}).get(str(i), {}) if st.session_state["loaded_data"] else {}
    
    num_val = s_row.get("num", str(i))
    num = c[0].text_input(f"num_{i}", value=num_val, label_visibility="collapsed")
    name = c[1].text_input(f"name_{i}", value=s_row.get("name", ""), label_visibility="collapsed", placeholder="馬名")
    pop = c[2].number_input(f"pop_{i}", min_value=1, max_value=18, value=int(s_row.get("pop", 10)), label_visibility="collapsed")
    idx = c[3].number_input(f"idx_{i}", value=float(s_row.get("idx", 0.0)), step=0.1, label_visibility="collapsed")
    l3f = c[4].number_input(f"l3f_{i}", value=float(s_row.get("l3f", 35.0)), step=0.1, label_visibility="collapsed")
    sire = c[5].text_input(f"sire_{i}", value=s_row.get("sire", ""), label_visibility="collapsed", placeholder="父馬")
    
    jock_list = [k for k in JOCKEY_MASTER.keys() if k != "その他（自由手入力）"]
    jock_list = sorted(jock_list) + ["その他（自由手入力）"]
    s_jock = s_row.get("jock", "その他（自由手入力）" if s_row.get("custom_jock") else "(未選択)")
    j_idx = (["(未選択)"] + jock_list).index(s_jock) if s_jock in (["(未選択)"] + jock_list) else 0
    jock = c[6].selectbox(f"jock_{i}", ["(未選択)"] + jock_list, index=j_idx, label_visibility="collapsed")
    
    custom_jock = ""
    if jock == "その他（自由手入力）":
        custom_jock = c[7].text_input(f"custom_jock_{i}", value=s_row.get("custom_jock", ""), label_visibility="collapsed", placeholder="騎手名")
    else:
        c[7].write("---")
        
    t_opts = ["選択なし", "芝", "ダート"]
    t_def = t_opts.index(s_row.get("sel_track")) if s_row.get("sel_track") in t_opts else (t_opts.index(auto_track) if auto_track in t_opts else 0)
    sel_track = c[8].selectbox(f"p1_{i}", t_opts, index=t_def, label_visibility="collapsed")
    
    sty_opts = ["選択なし", "逃げ", "先行", "差し", "追い込み"]
    sty_def = sty_opts.index(s_row.get("sel_style")) if s_row.get("sel_style") in sty_opts else 0
    sel_style = c[9].selectbox(f"p2_{i}", sty_opts, index=sty_def, label_visibility="collapsed")
    
    f_opts = ["選択なし", "内枠", "外枠"]
    try:
        int_num = int(num)
        f_def_idx = 1 if int_num <= 8 else (2 if int_num >= 13 else 0)
    except:
        f_def_idx = 0
    f_def = f_opts.index(s_row.get("sel_frame")) if s_row.get("sel_frame") in f_opts else f_def_idx
    sel_frame = c[10].selectbox(f"p3_{i}", f_opts, index=f_def, label_visibility="collapsed")
    
    d_opts = ["選択なし", "短距離", "中距離", "長距離"]
    d_def = d_opts.index(s_row.get("sel_dist")) if s_row.get("sel_dist") in d_opts else (d_opts.index(auto_dist) if auto_dist in d_opts else 0)
    sel_dist = c[11].selectbox(f"p4_{i}", d_opts, index=d_def, label_visibility="collapsed")
    
    plus_opts, minus_opts = ["選択なし"], ["選択なし"]
    if jock in JOCKEY_MASTER:
        for k, v in JOCKEY_MASTER[jock]["factors"].items():
            if k not in ["芝", "ダート", "逃げ", "先行", "差し", "追い込み", "内枠", "外枠", "短距離", "中距離", "長距離"]:
                if v > 0: plus_opts.append(k)
                elif v < 0: minus_opts.append(k)
                
    sel_plus1 = c[12].selectbox(f"p5_1_{i}", plus_opts, index=plus_opts.index(s_row.get("sel_plus1")) if s_row.get("sel_plus1") in plus_opts else 0, label_visibility="collapsed")
    sel_plus2 = c[13].selectbox(f"p5_2_{i}", plus_opts, index=plus_opts.index(s_row.get("sel_plus2")) if s_row.get("sel_plus2") in plus_opts else 0, label_visibility="collapsed")
    
    sel_minus1 = c[14].selectbox(f"p6_1_{i}", minus_opts, index=minus_opts.index(s_row.get("sel_minus1")) if s_row.get("sel_minus1") in minus_opts else 0, label_visibility="collapsed")
    sel_minus2 = c[15].selectbox(f"p6_2_{i}", minus_opts, index=minus_opts.index(s_row.get("sel_minus2")) if s_row.get("sel_minus2") in minus_opts else 0, label_visibility="collapsed")
    
    current_inputs["rows"][str(i)] = {
        "num": num, "name": name, "pop": pop, "idx": idx, "l3f": l3f, "sire": sire, "jock": jock, "custom_jock": custom_jock,
        "sel_track": sel_track, "sel_style": sel_style, "sel_frame": sel_frame, "sel_dist": sel_dist,
        "sel_plus1": sel_plus1, "sel_plus2": sel_plus2, "sel_minus1": sel_minus1, "sel_minus2": sel_minus2
    }
    
    # --- 🧮 スコア計算 ---
    score = 0.0
    note_text = "" # 🛠️ 事前初期化でエラーを防止
    
    if jock != "(未選択)":
        j_data = JOCKEY_MASTER.get(jock, JOCKEY_MASTER["その他（自由手入力）"])
        modifier = j_data["base"]
        factors = j_data["factors"]
        note_text = j_data.get("note", "")
        
        chosen_conditions = set([sel_track, sel_style, sel_frame, sel_dist, sel_plus1, sel_plus2, sel_minus1, sel_minus2])
        for cond in chosen_conditions:
            if cond in factors:
                val = factors[cond]
                if val < 0 and l3f <= 33.9: val = 0.0
                modifier += val
                
        if sel_course in ["東京芝2000m", "東京芝2400m", "中山芝2500m"]:
            if sel_frame == "内枠": modifier += 0.10
            elif sel_frame == "外枠" and l3f > 33.9: modifier -= 0.05
        
        if sire != "" and any(target in sire for target in good_blood_list):
            modifier += 0.10
            
        if (sel_style in ["逃げ", "先行"]) and (l3f <= 34.5):
            modifier += 0.15
            
        score = (idx * modifier) - (pop * 0.7)
        
    c[16].write(f"**{score:.2f}**")
    
    display_jock = custom_jock if jock == "その他（自由手入力）" else (jock if jock != "(未選択)" else "")
    calculated_results.append({
        "馬番": num, "馬name": name, "スコア": score, "父馬": sire, "騎手": display_jock, "戦略メモ": note_text
    })

# --- ストレージ管理 ---
if save_clicked:
    json_str = json.dumps(current_inputs, ensure_ascii=False)
    html(f"<script>localStorage.setItem('keiba_app_data', `{json_str}`); alert('📥 データを一時保存しました！');</script>", height=0)

if load_clicked:
    html("<script>var data = localStorage.getItem('keiba_app_data'); if (data) { const url = new URL(window.parent.location.href); url.searchParams.set('loaded_json', data); window.parent.location.href = url.toString(); } else { alert('⚠️ データが見つかりません'); }</script>", height=0)

# --- ランキング生成 ---
st.divider()
if st.button("🏆 最終予想ランキングを生成", type="primary", use_container_width=True):
    res_df = pd.DataFrame(calculated_results)
    res_df = res_df[res_df["馬name"] != ""].sort_values(by="スコア", ascending=False)
    
    if not res_df.empty:
        st.balloons()
        st.header(f"🎯 本命推奨馬: {res_df.iloc[0]['馬name']} ({res_df.iloc[0]['騎手']})")
        st.dataframe(res_df[["馬番", "馬name", "父馬", "スコア", "騎手", "戦略メモ"]], use_container_width=True, hide_index=True)
