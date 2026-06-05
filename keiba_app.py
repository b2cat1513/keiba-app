import streamlit as st
import pandas as pd
import json
from streamlit.components.v1 import html

# --- [新ジョッキー事典・大幅拡充マスターデータ（50名超）] ---
JOCKEY_MASTER = {
    # 栗東（関西）所属・主要
    "C.ルメール": {"base": 1.30, "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "長距離": 0.05, "東京": 0.15, "芝2400以上": 0.15, "重賞8枠": 0.15, "中山": -0.15}, "note": "東京・長距離・重賞8枠◎"},
    "川田将雅": {"base": 1.30, "factors": {"芝1枠": 0.15, "小回り2000": 0.15, "交流重賞": 0.15, "長距離": -0.05}, "note": "芝1枠・小回り・交流重賞◎"},
    "坂井瑠星": {"base": 1.25, "factors": {"先行": -0.05, "内枠": 0.05, "外枠": -0.05, "ダート重賞": 0.15, "欧州血統": 0.15}, "note": "逃げ先行・ダート重賞◎"},
    "武豊": {"base": 1.20, "factors": {"芝": 0.05, "継続騎乗": 0.15, "人気薄": 0.15, "距離延長": 0.15}, "note": "継続騎乗・大舞台での一発◎"},
    "松山弘平": {"base": 1.15, "factors": {"ダート": 0.15, "新馬戦": 0.15, "前哨戦": 0.15, "堀厩舎": 0.15}, "note": "ダート・新馬戦・堀厩舎◎"},
    "岩田望来": {"base": 1.10, "factors": {"マイル以下の差し": 0.15, "乗り替わり": 0.15}, "note": "乗り替わり・マイル以下の差し○"},
    "西村淳也": {"base": 1.10, "factors": {"京都芝": 0.15, "ロードカナロア産駒": 0.15}, "note": "京都芝・カナロア産駒◎"},
    "団野大成": {"base": 1.10, "factors": {"短距離重賞": 0.15, "荒れ馬場": 0.15}, "note": "短距離重賞・荒れた芝◎"},
    "鮫島克駿": {"base": 1.05, "factors": {"イン突き": 0.15, "中長距離": 0.15, "ダート外枠": 0.15}, "note": "好位イン突き・中長距離◎"},
    "藤岡佑介": {"base": 1.10, "factors": {"自在性": 0.15, "妙味": 0.15, "重賞の人気馬": -0.15}, "note": "展開読み◎。重賞人気馬は割引"},
    "幸英明": {"base": 1.05, "factors": {"ダート": 0.15, "牡馬のタフ条件": 0.15}, "note": "タフなダート戦・牡馬◎"},
    "池添謙一": {"base": 1.15, "factors": {"大舞台＆重賞": 0.15, "差し＆追い込み": 0.15}, "note": "G1・重賞での勝負強さ◎"},
    "岩田康誠": {"base": 1.15, "factors": {"重賞": 0.15, "イン突き": 0.15}, "note": "内枠からのイン突き強襲◎"},
    "M.デムーロ": {"base": 1.15, "factors": {"大舞台＆重賞": 0.15, "マクリ追い込み": 0.15}, "note": "出遅れケア必要も大舞台マクリ◎"},
    "浜中俊": {"base": 1.05, "factors": {"芝短~中距離": 0.15, "1番人気": 0.15}, "note": "芝の短〜中距離・人気馬○"},
    "北村友一": {"base": 1.10, "factors": {"芝8枠": 0.15, "中長距離戦": 0.15}, "note": "外枠からの差し・中長距離○"},
    "横山典弘": {"base": 1.15, "factors": {"芝内枠": 0.15, "継続騎乗": 0.15, "馬ファースト": 0.15}, "note": "ポツン注意も内枠・継続◎"},
    "和田竜二": {"base": 1.05, "factors": {"タフな泥臭い展開": 0.15, "ズブい馬": 0.15}, "note": "追えるベテラン。タフな消耗戦◎"},
    "古川吉洋": {"base": 1.00, "factors": {"先行": 0.05, "穴馬": 0.10}, "note": "ベテランの巧みなペースメイク"},
    "小沢大仁": {"base": 1.05, "factors": {"ダート": 0.05, "ローカル": 0.05}, "note": "若手の実力派、ローカルで狙い目"},
    "角田大河": {"base": 1.00, "factors": {"減量": 0.05}, "note": "積極的な逃げ・先行に魅力"},
    "今村聖奈": {"base": 1.00, "factors": {"芝の軽量馬": 0.10}, "note": "軽い斤量活かした前残り注意"},
    "永島まなみ": {"base": 1.05, "factors": {"ダート逃げ": 0.15, "ローカル先行": 0.10}, "note": "ダートの逃げ・先行は超強力"},
    "田口貫太": {"base": 1.05, "factors": {"ダートの人気馬": 0.15, "重賞": 0.15, "芝1枠": 0.15}, "note": "乗れてる若手。ダート人気馬◎"},
    "吉村誠之助": {"base": 1.10, "factors": {"イン突き": 0.15, "大型馬": 0.15}, "note": "期待のルーキー。イン差し○"},
    "高杉吏麒": {"base": 1.10, "factors": {"スタート": 0.15, "ダート内枠": 0.15}, "note": "スタート巧者。ダート内枠○"},

    # 美浦（関東）所属・主要
    "戸崎圭太": {"base": 1.20, "factors": {"前走ルメール": 0.15, "ダート外枠": 0.15, "東京1600": 0.15, "重賞": 0.15}, "note": "東京マイル・前走ルメール◎"},
    "横山武史": {"base": 1.20, "factors": {"中山重賞": 0.15, "持久力戦": 0.15, "マイネル": 0.15}, "note": "中山重賞・先行持久力戦◎"},
    "菅原明良": {"base": 1.10, "factors": {"注目馬": 0.15, "中長距離戦": 0.05}, "note": "G1初制覇でノる大器。穴も明ける"},
    "佐々木大輔": {"base": 1.10, "factors": {"芝内枠": 0.15, "馬場読み": 0.15}, "note": "若手屈指の立ち回り。内枠◎"},
    "丹内祐次": {"base": 1.10, "factors": {"ローカル芝": 0.15, "馬場読み": 0.15}, "note": "ローカル（函館・小倉等）の鬼"},
    "田辺裕信": {"base": 1.10, "factors": {"開催後半芝": 0.15, "長距離戦": 0.15}, "note": "人気薄の大胆な逃げ・ポツン差し注意"},
    "横山和生": {"base": 1.15, "factors": {"ダート重賞": 0.15, "長距離戦": 0.05}, "note": "タイトルホルダー等の長距離・ダート重賞○"},
    "津村明秀": {"base": 1.05, "factors": {"直線競馬": 0.15, "小回り": 0.05}, "note": "新潟直線◎。重賞でも一撃あり"},
    "三浦皇成": {"base": 1.05, "factors": {"1番人気": 0.15, "下級条件": 0.15, "重賞": -0.15}, "note": "平場の1番人気は堅実。重賞は割引"},
    "大野拓哉": {"base": 1.05, "factors": {"ダートの外枠": 0.15, "差し＆追い込み": 0.15}, "note": "ダート外枠の追い込み穴馬で激走"},
    "石川裕紀人": {"base": 1.10, "factors": {"芝1枠": 0.15, "積極策": 0.15}, "note": "大舞台での思い切った先行策魅力"},
    "菱田裕二": {"base": 1.05, "factors": {"テーオー": 0.15, "中長距離": 0.15}, "note": "テーオーの馬・中長距離○"},
    "北村宏司": {"base": 1.05, "factors": {"東京芝": 0.10, "イン立ち回り": 0.10}, "note": "ベテランの安定感。イン立ち回り○"},
    "丸山元気": {"base": 1.00, "factors": {"穴馬": 0.10}, "note": "時折見せる鋭い差し込みに警戒"},
    "内田博幸": {"base": 1.05, "factors": {"タフな馬場": 0.10, "逃げ先行": 0.05}, "note": "剛腕健在。ダートや荒れ馬場○"},
    "柴田善臣": {"base": 1.00, "factors": {"ベテランの味": 0.10}, "note": "最年長大ベテラン。無理のない誘導"},
    "木幡巧也": {"base": 1.00, "factors": {"ダート先行": 0.05}, "note": "ダートでの積極策に定評"},
    "石橋脩": {"base": 1.05, "factors": {"堀厩舎": 0.10, "先行": 0.05}, "note": "堀厩舎の人気薄などで不気味さあり"},

    # 外国人・地方・その他
    "J.モレイラ": {"base": 1.35, "factors": {"中長距離": 0.15, "ダート外枠": 0.15}, "note": "マジックマン。乗れば確勝級"},
    "D.レーン": {"base": 1.30, "factors": {"重賞": 0.15, "芝中長距離": 0.15}, "note": "追って伸びる。日本の馬場への適性抜群"},
    "R.キング": {"base": 1.25, "factors": {"スタート": 0.15, "特別戦": 0.15}, "note": "抜群のスタートセンスと好位キープ"},
    "短期免許外国人": {"base": 1.20, "factors": {"重賞": 0.10}, "note": "有力馬配置が多く一律高評価"},
    "地方所属騎手": {"base": 1.05, "factors": {"ダート": 0.10}, "note": "交流重賞やダート戦での地方リーディング級"},
    
    # 手入力・データなし用
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
st.title("🏇 競馬予想・ジョッキー＆コース事典 【完全騎手網羅＋幅広プルダウン版】")

# --- 💾 データ読み込みロジック ---
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
st.write("### 📝 出馬表データ入力（18頭フル対応）")

save_cols = st.columns([2, 2, 8])
with save_cols[0]:
    save_clicked = st.button("📥 入力内容をスマホに一時保存", use_container_width=True)
with save_cols[1]:
    load_clicked = st.button("📤 保存したデータを読み込む", use_container_width=True, type="secondary")

calculated_results = []

# 🔎 プルダウンの文字が切れないよう、カラム幅の比率を調整（横幅を広く確保）
c_widths = [0.8, 1.8, 0.8, 0.8, 1.2, 1.8, 2.5, 1.8, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0]
cols = st.columns(c_widths)
headers = ["馬番", "馬名", "人気", "指数", "前5走3F", "父馬", "騎手（選択）", "手入力(その他時)", "①馬場", "②脚質", "③枠順", "④距離", "⑤プラス", "⑥マイナス", "スコア"]
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
    
    # 騎手名簿のソート
    jock_list = [k for k in JOCKEY_MASTER.keys() if k != "その他（自由手入力）"]
    jock_list = sorted(jock_list) + ["その他（自由手入力）"]
    s_jock = s_row.get("jock", "その他（自由手入力）" if s_row.get("custom_jock") else "(未選択)")
    j_idx = (["(未選択)"] + jock_list).index(s_jock) if s_jock in (["(未選択)"] + jock_list) else 0
    jock = c[6].selectbox(f"jock_{i}", ["(未選択)"] + jock_list, index=j_idx, label_visibility="collapsed")
    
    # ✍️ 「その他」を選んだ場合の自由手入力欄
    custom_jock = ""
    if jock == "その他（自由手入力）":
        custom_jock = c[7].text_input(f"custom_jock_{i}", value=s_row.get("custom_jock", ""), label_visibility="collapsed", placeholder="騎手名を入力")
    else:
        c[7].write("---") # 通常時はスキップ
        
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
                
    p_def = plus_opts.index(s_row.get("sel_plus")) if s_row.get("sel_plus") in plus_opts else 0
    sel_plus = c[12].selectbox(f"p5_{i}", plus_opts, index=p_def, label_visibility="collapsed")
    
    m_def = minus_opts.index(s_row.get("sel_minus")) if s_row.get("sel_minus") in minus_opts else 0
    sel_minus = c[13].selectbox(f"p6_{i}", minus_opts, index=m_def, label_visibility="collapsed")
    
    current_inputs["rows"][str(i)] = {
        "num": num, "name": name, "pop": pop, "idx": idx, "l3f": l3f, "sire": sire, "jock": jock, "custom_jock": custom_jock,
        "sel_track": sel_track, "sel_style": sel_style, "sel_frame": sel_frame,
        "sel_dist": sel_dist, "sel_plus": sel_plus, "sel_minus": sel_minus
    }
    
    # --- スコア計算ロジック ---
    score = 0.0
    if jock != "(未選択)":
        j_data = JOCKEY_MASTER.get(jock, JOCKEY_MASTER["その他（自由手入力）"])
        modifier = j_data["base"]
        factors = j_data["factors"]
        
        for cond in set([sel_track, sel_style, sel_frame, sel_dist, sel_plus, sel_minus]):
            if cond in factors:
                val = factors[cond]
                if val < 0 and l3f <= 33.9: val = 0.0
                modifier += val
                
        # 2024-2026G1バイアスロジック
        if sel_course in ["東京芝2000m", "東京芝2400m", "中山芝2500m"]:
            if sel_frame == "内枠": modifier += 0.10
            elif sel_frame == "外枠" and l3f > 33.9: modifier -= 0.05
        
        # 血統加点
        if sire != "" and any(target in sire for target in good_blood_list):
            modifier += 0.10
            
        # 先行コンボ
        if (sel_style in ["逃げ", "先行"]) and (l3f <= 34.5):
            modifier += 0.15
            
        score = (idx * modifier) - (pop * 0.7)
        
    c[14].write(f"**{score:.2f}**")
    
    display_jock = custom_jock if jock == "その他（自由手入力）" else (jock if jock != "(未選択)" else "")
    calculated_results.append({
        "馬番": num, "馬名": name, "スコア": score, "父馬": sire, "騎手": display_jock, "戦略メモ": j_data.get("note", "")
    })

# --- 保存処理等 ---
if save_clicked:
    json_str = json.dumps(current_inputs, ensure_ascii=False)
    js_save = f"<script>localStorage.setItem('keiba_app_data', `{json_str}`); alert('📥 保存しました！');</script>"
    html(js_save, height=0)

if load_clicked:
    js_load = "<script>var data = localStorage.getItem('keiba_app_data'); if (data) { const url = new URL(window.parent.location.href); url.searchParams.set('loaded_json', data); window.parent.location.href = url.toString(); } else { alert('⚠️ データがありません'); }</script>"
    html(js_load, height=0)

# --- ランキング生成 ---
st.divider()
if st.button("🏆 最終予想ランキングを生成", type="primary", use_container_width=True):
    res_df = pd.DataFrame(calculated_results)
    res_df = res_df[res_df["馬名"] != ""].sort_values(by="スコア", ascending=False)
    
    if not res_df.empty:
        st.balloons()
        st.header(f"🎯 本命推奨馬: {res_df.iloc[0]['馬名']} ({res_df.iloc[0]['騎手']})")
        st.dataframe(res_df[["馬番", "馬名", "父馬", "スコア", "騎手", "戦略メモ"]], use_container_width=True, hide_index=True)
