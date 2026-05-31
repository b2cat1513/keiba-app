import streamlit as st
import pandas as pd
import json
from streamlit.components.v1 import html

# --- [新ジョッキー事典・完全数値化マスターデータ] ---
JOCKEY_MASTER = {
    "C.ルメール": {"base": 1.30, "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "短距離": -0.05, "長距離": 0.05, "東京": 0.15, "芝2400以上": 0.15, "重賞8枠": 0.15, "中山": -0.15, "芝道悪": -0.15}, "note": "芝2400以上・東京・重賞8枠◎。中山・芝道悪×"},
    "川田将雅": {"base": 1.30, "factors": {"芝": -0.05, "先行": -0.05, "長距離": -0.15, "芝1枠": 0.15, "小回り2000": 0.15, "交流重賞": 0.15}, "note": "芝1枠・小回り2000・交流重賞◎。長距離×"},
    "戸崎圭太": {"base": 1.20, "factors": {"内枠": -0.05, "短距離": -0.05, "馬群": -0.15, "前走ルメール": 0.15, "ダート外枠": 0.15, "東京1600": 0.15, "中山1600": 0.15, "東京2500": 0.15, "重賞": 0.15}, "note": "前走ルメール・マイル〜2500重賞◎。馬群×注意"},
    "坂井瑠星": {"base": 1.25, "factors": {"先行": -0.05, "内枠": 0.05, "外枠": -0.05, "ダート重賞": 0.15, "欧州血統": 0.15, "前走古川奈": 0.05}, "note": "ダート重賞・欧州血統◎。内枠○、外枠・先行は少し割引"},
    "横山武史": {"base": 1.20, "factors": {"先行": -0.05, "内枠": 0.05, "外枠": -0.05, "長距離": -0.05, "中山重賞": 0.15, "持久力戦": 0.15, "マイネル": 0.15, "ウイン": 0.15}, "note": "中山重賞・マイネル系◎。内枠○"},
    "松山弘平": {"base": 1.15, "factors": {"先行": -0.05, "差し": -0.05, "短距離": -0.05, "ダート": 0.15, "新馬戦": 0.15, "前哨戦": 0.15, "マイル重賞": 0.05, "堀厩舎": 0.15}, "note": "ダート・新馬・堀厩舎◎。マイル重賞○"},
    "武豊": {"base": 1.20, "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": 0.05, "内枠": -0.05, "外枠": -0.05, "短距離": -0.05, "継続騎乗": 0.15, "人気薄": 0.15, "逃げ": 0.05, "追い込み": 0.05, "距離延長": 0.15, "ダート上級": 0.05}, "note": "継続・人気薄・距離延長◎。極端な脚質○"},
    "岩田望来": {"base": 1.10, "factors": {"芝": -0.05, "ダート": -0.05, "短距離": -0.05, "長距離": -0.05, "マイル以下の差し": 0.15, "乗り替わり": 0.15, "父から乗り替わり": 0.15}, "note": "乗り替わり・マイル以下の差し◎"},
    "西村淳也": {"base": 1.10, "factors": {"芝": 0.05, "ダート": -0.05, "先行": -0.05, "差し": 0.05, "内枠": -0.05, "長距離": -0.05, "京都芝": 0.15, "ロードカナロア産駒": 0.15, "スタートセンス": 0.05}, "note": "京都芝・カナロア産駒◎。差し○"},
    "団野大成": {"base": 1.10, "factors": {"先行": -0.05, "差し": -0.05, "短距離重賞": 0.15, "人気薄乗替": 0.15, "芝の荒れ馬場": 0.15}, "note": "短距離重賞・荒れ馬場・人気薄乗り替わり◎"},
    "菅原明良": {"base": 1.10, "factors": {"芝": 0.05, "ダート 0.05, "先行": 0.05, "差し": -0.05, "長距離": -0.05, "中長距離戦": 0.05, "継続騎乗": 0.05, "注目馬": 0.15}, "note": "注目馬◎。芝ダ先行○"},
    "鮫島克駿": {"base": 1.05, "factors": {"芝": -0.05, "先行": 0.05, "差し": 0.05, "内枠": -0.05, "イン突き": 0.15, "中長距離": 0.15, "ダート外枠": 0.15, "リズム重視": 0.15}, "note": "イン突き・中長距離・ダート外枠◎"},
    "斉藤新": {"base": 1.05, "factors": {"芝": 0.05, "短距離": -0.05, "長距離": -0.05, "外枠": 0.15, "逃げ": 0.15, "芝特別戦": 0.15}, "note": "外枠・逃げ・特別戦◎"},
    "佐々木大輔": {"base": 1.10, "factors": {"芝": 0.05, "先行": 0.05, "長距離": -0.05, "芝内枠": 0.15, "馬場読み": 0.15, "立ち回り": 0.15, "外枠": -0.15}, "note": "芝内枠・立ち回り◎。外枠×"},
    "吉村誠之助": {"base": 1.10, "factors": {"芝": -0.05, "先行": -0.05, "差し": 0.05, "イン突き": 0.15, "大型馬": 0.15, "上級条件": 0.15, "ダート": -0.15}, "note": "イン差し・大型馬・上級条件◎。ダート×"},
    "高杉吏麒": {"base": 1.10, "factors": {"芝": 0.05, "先行": 0.05, "長距離": -0.05, "自在性": 0.15, "スタート": 0.15, "ダート内枠": 0.15, "芝中距離以上": 0.15, "外枠": -0.15}, "note": "スタート・ダート内枠・中距離以上◎。外枠×"},
    "田口貫太": {"base": 1.05, "factors": {"芝": -0.05, "先行": 0.05, "先行型": 0.05, "ダートの人気馬": 0.15, "重賞": 0.15, "芝1枠": 0.15, "ダートの差し": -0.15}, "note": "ダート人気・重賞・芝1枠◎。ダート差し×"},
    "菊沢一樹": {"base": 1.05, "factors": {"芝": -0.05, "先行": 0.05, "内枠": -0.05, "外枠": 0.05, "短距離": -0.05, "頭脳派": 0.15, "差し": 0.15, "直線競馬": 0.15, "特別戦": 0.15}, "note": "頭脳派差し・直線競馬・特別戦◎"},
    "荻野極": {"base": 1.05, "factors": {"芝": -0.05, "ダート": -0.05, "短距離": -0.05, "芝内枠": 0.15, "大型馬": 0.15, "ノースヒルズ": 0.15, "鹿戸厩舎": 0.15, "先行": -0.15}, "note": "内枠大型・ノースヒルズ◎。先行×"},
    "横山典弘": {"base": 1.15, "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "外枠": -0.05, "短距離": -0.05, "重賞": 0.15, "芝内枠": 0.15, "継続騎乗": 0.15, "馬ファースト": 0.15}, "note": "重賞・内枠・継続◎。馬ファースト"},
    "岩田康誠": {"base": 1.15, "factors": {"芝": -0.05, "内枠": -0.05, "外枠": -0.05, "短距離": -0.05, "重賞": 0.15, "継続騎乗": 0.15, "イン突き": 0.15, "自在系": 0.15, "芝1枠": -0.05}, "note": "重賞・継続・イン突き◎"},
    "北村友一": {"base": 1.10, "factors": {"芝": -0.05, "ダート": -0.05, "先行": 0.05, "内枠": 0.05, "短距離": -0.05, "長距離": 0.05, "人薄": 0.05, "芝8枠": 0.15, "差し馬": 0.15, "中長距離戦": 0.15}, "note": "芝8枠・差し・中長距離◎"},
    "田辺裕信": {"base": 1.10, "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": -0.05, "長距離": 0.05, "乗替": 0.05, "開催後半芝": 0.15, "超リズム重視": 0.15, "長距離戦": 0.15, "短距離重賞": -0.05}, "note": "開催後半芝・長距離戦◎"},
    "横山和生": {"base": 1.15, "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "外枠": -0.05, "乗替": 0.05, "ダート重賞": 0.15, "小回り": 0.05, "長距離戦": 0.05}, "note": "ダート重賞◎。小回り・長距離○"},
    "J.モレイラ": {"base": 1.35, "factors": {"芝": -0.05, "ダート": 0.05, "先行": 0.05, "差し": 0.05, "長距離": 0.05, "乗替": 0.05, "注目": 0.05, "中長距離": 0.15, "ダート外枠": 0.15}, "note": "中長距離・ダート外枠◎"},
    "D.レーン": {"base": 1.30, "factors": {"芝": 0.05, "ダート": -0.05, "内枠": -0.05, "外枠": -0.05, "乗替": 0.05, "重賞": 0.15, "芝中長距離": 0.15, "新馬戦": 0.05, "欧州血統": 0.05}, "note": "重賞・芝中長距離◎"},
    "R.キング": {"base": 1.25, "factors": {"芝": -0.05, "外枠": 0.05, "乗替": 0.05, "注目": 0.05, "スタート": 0.15, "妙味": 0.15, "特別戦": 0.15}, "note": "スタート・妙味・特別戦◎"},
    "丹内祐次": {"base": 1.10, "factors": {"芝": -0.05, "ダート": -0.05, "先行": 0.05, "短距離": -0.05, "ローカル芝": 0.15, "馬場読み": 0.15, "固め打ち": 0.15, "頭脳派": 0.15}, "note": "ローカル芝・馬場読み・頭脳派◎"},
    "浜中俊": {"base": 1.05, "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "差し": -0.05, "芝短~中距離": 0.15, "1番人気": 0.15}, "note": "芝短〜中距離・1番人気◎"},
    "藤岡佑介": {"base": 1.10, "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "短距離": -0.05, "長距離": -0.05, "人薄": 0.05, "自在性": 0.15, "妙味": 0.15, "重賞の人気馬": -0.15, "勝負強さ": -0.05}, "note": "自在性・妙味◎。重賞人気馬×"},
    "津村明秀": {"base": 1.05, "factors": {"芝": -0.05, "先行": -0.05, "短距離": -0.05, "長距離": -0.05, "直線競馬": 0.15, "小回り": 0.05, "差し馬マクリ": 0.05, "伸びしろ": -0.05}, "note": "直線競馬◎。小回り・マクリ○"},
    "三浦皇成": {"base": 1.05, "factors": {"芝": -0.05, "先行": -0.05, "内枠": -0.05, "外枠": -0.05, "1番人気": 0.15, "下級条件": 0.15, "重賞": -0.15}, "note": "下級条件・1番人気◎。重賞×"},
    "大野拓哉": {"base": 1.05, "factors": {"芝": -0.05, "先行": 0.05, "外枠": 0.05, "短距離": -0.05, "長距離": -0.05, "人薄": 0.05, "ダートの外枠": 0.15, "差し＆追い込み": 0.15, "人気馬": -0.15}, "note": "ダート外枠・差し追込◎。人気馬×"},
    "石川裕紀人": {"base": 1.10, "factors": {"芝": -0.05, "ダート": -0.05, "先行": 0.05, "短距離": -0.05, "芝1枠": 0.15, "小回り": 0.15, "積極策": 0.15, "マイネル": 0.15}, "note": "芝1枠・小回り・積極策◎"},
    "菱田裕二": {"base": 1.05, "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "差し": -0.05, "テーオー": 0.15, "中長距離": 0.15}, "note": "テーオー・中長距離◎"},
    "池添謙一": {"base": 1.15, "factors": {"芝": 0.05, "ダート": -0.05, "長距離": -0.05, "大舞台＆重賞": 0.15, "差し＆追い込み": 0.15, "下級条件": -0.05}, "note": "大舞台重賞・差し追込◎"},
    "幸英明": {"base": 1.05, "factors": {"芝": -0.05, "先行": -0.05, "ダート": 0.15, "牡馬のタフ条件": 0.15, "数打ちゃ当たる": 0.05}, "note": "ダート・牡馬タフ条件◎"},
    "M.デムーロ": {"base": 1.15, "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "長距離": -0.05, "大舞台＆重賞": 0.15, "マクリ追い込み": 0.15, "外枠": 0.05}, "note": "大舞台重賞・マクリ追込◎"},
    "その他（データなし）": {"base": 1.00, "factors": {}, "note": "特記データのない騎手です。一律基準値1.00で計算します。"}
}

# --- [コース事典・マスタデータ] ---
COURSE_MASTER = {
    "東京芝1600m": {"note": "2月内枠、2月以外外枠。同距離＆距離短縮馬、重賞は差し・追い込み有利。ロードカナロア/エピファネイア/モーリス/ドゥラメンテ/イスラボニータ産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス", "ドゥラメンテ", "イスラボニータ"]},
    "東京芝2000m": {"note": "1枠有利。前走同距離＆距離短縮が好走。エピファネイア/モーリス牡馬/キズナ/キタサンブラック/ロードカナロア牡馬○", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "モーリス", "キズナ", "キタサンブラック", "ロードカナロア"]},
    "東京芝2400m": {"note": "オークスは差し・追い込み○。ジャパンカップはダービー・オークス3着以内の3歳馬○。ドゥラメンテ/ハービンジャー/ルーラーシップ/レイデオロ牡馬/キタサンブラック産駒○", "track": "芝", "dist": "長距離", "good_lineage": ["ドゥラメンテ", "ハービンジャー", "ルーラーシップ", "レイデオロ", "キタサンブラック"]},
    "東京ダート1600m": {"note": "外枠有利。前走同距離＆距離短縮馬。ヘニーヒューズ/ドレフォン（逃げ先行）/ロードカナロア/ドゥラメンテ牡馬○。内枠○、距離短縮、1・2枠、馬体重480kg以上○", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "ロードカナロア", "ドゥラメンテ"]},
    "中山芝2000m": {"note": "皐月賞はマイル〜1800m重賞実績馬○。荒れ馬場は外差し○。エピファネイア牡馬/ハービンジャー/モーリス/キタサンブラック/ドゥラメンテ産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "ハービンジャー", "モーリス", "キタサンブラック", "ドゥラメンテ"]},
    "中山芝2500m": {"note": "高速馬場の有馬記念は東京中距離G1実績馬○。高速馬場は内枠、荒れ馬場は外枠有利。エピファネイア/キズナ/ドゥラメンテ/ゴールドシップ/ジャスタウェイ産駒○", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キズナ", "ドゥラメンテ", "ゴールドシップ", "ジャスタウェイ"]},
    "阪神芝1600m": {"note": "内枠有利。高速馬場は外差し、同距離＆距離短縮馬○。ロードカナロア/エピファネイア/キズナ産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "キズナ"]},
    "阪神芝2000m": {"note": "外枠の先行馬有利。大阪杯は内差し。ドゥラメンテ牡馬/ルーラーシップ/キズナ産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["ドゥラメンテ", "ルーラーシップ", "キズナ"]}
}

st.set_page_config(page_title="競馬予想・ジョッキー＆コース事典完全版", layout="wide")
st.title("🏇 競馬予想・ジョッキー＆コース事典 【スマホ保存対応版】")

# --- 💾 ブラウザ一時保存用の仕組み (Session State & LocalStorage) ---
if "storage_trigger" not in st.session_state:
    st.session_state["storage_trigger"] = ""
if "loaded_data" not in st.session_state:
    st.session_state["loaded_data"] = None

# JavaScriptからデータを受け取る隠しフック
query_params = st.query_params
if "loaded_json" in query_params:
    try:
        st.session_state["loaded_data"] = json.loads(query_params["loaded_json"])
        st.query_params.clear() # URLを綺麗にする
    except:
        pass

# --- 🗺️ コース選択プルダウン ---
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
st.caption(f"現在の自動判定条件 ➔ 馬場: **{auto_track}** | 距離: **{auto_dist}**")

# 保存・読込ボタンの配置
save_cols = st.columns([2, 2, 8])
with save_cols[0]:
    save_clicked = st.button("📥 入力内容をスマホに一時保存", use_container_width=True)
with save_cols[1]:
    load_clicked = st.button("📤 保存したデータを読み込む", use_container_width=True, type="secondary")

calculated_results = []
c_widths = [1, 2.5, 1, 1, 1, 3.5, 1, 1, 1, 1, 2, 1, 1, 1]
cols = st.columns(c_widths)
headers = ["馬番", "馬名", "人気", "指数", "後3F", "騎手選択", "①馬場", "②脚質", "③枠順", "④距離", "⑦血統(産駒)", "⑤他プラス", "⑥他マイナス", "スコア"]
for col, h in zip(cols, headers):
    col.write(f"**{h}**")

current_inputs = {"course": sel_course, "rows": {}}

# 18頭分の入力欄生成
for i in range(1, 19):
    c = st.columns(c_widths)
    
    # セーブデータからの復元処理
    s_row = st.session_state["loaded_data"].get("rows", {}).get(str(i), {}) if st.session_state["loaded_data"] else {}
    
    num = c[0].text_input(f"num_{i}", value=s_row.get("num", str(i)), label_visibility="collapsed")
    name = c[1].text_input(f"name_{i}", value=s_row.get("name", ""), label_visibility="collapsed", placeholder="馬名")
    pop = c[2].number_input(f"pop_{i}", min_value=1, max_value=18, value=int(s_row.get("pop", 10)), label_visibility="collapsed")
    idx = c[3].number_input(f"idx_{i}", value=float(s_row.get("idx", 0.0)), step=0.1, label_visibility="collapsed")
    l3f = c[4].number_input(f"l3f_{i}", value=float(s_row.get("l3f", 35.0)), step=0.1, label_visibility="collapsed")
    
    raw_jock_list = [k for k in JOCKEY_MASTER.keys() if k != "その他（データなし）"]
    jock_list = sorted(raw_jock_list) + ["その他（データなし）"]
    s_jock = s_row.get("jock", "(未選択)")
    j_idx = (["(未選択)"] + jock_list).index(s_jock) if s_jock in (["(未選択)"] + jock_list) else 0
    jock = c[5].selectbox(f"jock_{i}", ["(未選択)"] + jock_list, index=j_idx, label_visibility="collapsed")
    
    t_opts = ["選択なし", "芝", "ダート"]
    t_def = t_opts.index(s_row.get("sel_track")) if s_row.get("sel_track") in t_opts else (t_opts.index(auto_track) if auto_track in t_opts else 0)
    sel_track = c[6].selectbox(f"p1_{i}", t_opts, index=t_def, label_visibility="collapsed")
    
    sty_opts = ["選択なし", "逃げ", "先行", "差し", "追い込み"]
    sty_def = sty_opts.index(s_row.get("sel_style")) if s_row.get("sel_style") in sty_opts else 0
    sel_style = c[7].selectbox(f"p2_{i}", sty_opts, index=sty_def, label_visibility="collapsed")
    
    f_opts = ["選択なし", "内枠", "外枠"]
    f_def = f_opts.index(s_row.get("sel_frame")) if s_row.get("sel_frame") in f_opts else 0
    sel_frame = c[8].selectbox(f"p3_{i}", f_opts, index=f_def, label_visibility="collapsed")
    
    d_opts = ["選択なし", "短距離", "中距離", "長距離"]
    d_def = d_opts.index(s_row.get("sel_dist")) if s_row.get("sel_dist") in d_opts else (d_opts.index(auto_dist) if auto_dist in d_opts else 0)
    sel_dist = c[9].selectbox(f"p4_{i}", d_opts, index=d_def, label_visibility="collapsed")
    
    blood_options = ["その他・データなし"] + good_blood_list + ["サンデーサイレンス系", "キングカメハメハ系", "ノーザンダンサー系"]
    b_def = blood_options.index(s_row.get("sel_blood")) if s_row.get("sel_blood") in blood_options else 0
    sel_blood = c[10].selectbox(f"p7_{i}", blood_options, index=b_def, label_visibility="collapsed")
    
    plus_opts, minus_opts = ["選択なし"], ["選択なし"]
    if jock in JOCKEY_MASTER:
        for k, v in JOCKEY_MASTER[jock]["factors"].items():
            if k not in ["芝", "ダート", "逃げ", "先行", "差し", "追い込み", "内枠", "外枠", "短距離", "中距離", "長距離"]:
                if v > 0: plus_opts.append(k)
                elif v < 0: minus_opts.append(k)
                
    p_def = plus_opts.index(s_row.get("sel_plus")) if s_row.get("sel_plus") in plus_opts else 0
    sel_plus = c[11].selectbox(f"p5_{i}", plus_opts, index=p_def, label_visibility="collapsed")
    
    m_def = minus_opts.index(s_row.get("sel_minus")) if s_row.get("sel_minus") in minus_opts else 0
    sel_minus = c[12].selectbox(f"p6_{i}", minus_opts, index=m_def, label_visibility="collapsed")
    
    # 現在の入力を保存用辞書にキープ
    current_inputs["rows"][str(i)] = {
        "num": num, "name": name, "pop": pop, "idx": idx, "l3f": l3f, "jock": jock,
        "sel_track": sel_track, "sel_style": sel_style, "sel_frame": sel_frame,
        "sel_dist": sel_dist, "sel_blood": sel_blood, "sel_plus": sel_plus, "sel_minus": sel_minus
    }
    
    # スコア計算
    score = 0.0
    if jock in JOCKEY_MASTER:
        j_data = JOCKEY_MASTER[jock]
        modifier = j_data["base"]
        factors = j_data["factors"]
        
        for cond in set([sel_track, sel_style, sel_frame, sel_dist, sel_plus, sel_minus]):
            if cond in factors: modifier += factors[cond]
        if sel_blood in good_blood_list: modifier += 0.10
        if l3f <= 34.5 and "差し" in factors: modifier += 0.05
        if l3f >= 36.5 and "先行" in factors: modifier += 0.05
        
        score = (idx * modifier) - (pop * 0.7)
        
    c[13].write(f"**{score:.2f}**")
    calculated_results.append({"馬番": num, "馬名": name, "スコア": score, "騎手": jock if jock != "(未選択)" else "", "戦略メモ": JOCKEY_MASTER.get(jock, {}).get("note", "")})

# --- JavaScriptを駆使したローカルストレージ保存・読込処理 ---
if save_clicked:
    json_str = json.dumps(current_inputs, ensure_ascii=False)
    js_save = f"""
    <script>
        localStorage.setItem('keiba_app_data', `{json_str}`);
        alert('📥 スマホ（ブラウザ）へ一時保存しました！次回開いた際に「データを読み込む」を押すと復元します。');
    </script>
    """
    html(js_save, height=0)

if load_clicked:
    js_load = """
    <script>
        var data = localStorage.getItem('keiba_app_data');
        if (data) {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('loaded_json', data);
            window.parent.location.href = url.toString();
        } else {
            alert('⚠️ 保存されたデータが見つかりませんでした。');
        }
    </script>
    """
    html(js_load, height=0)

# --- ランキング生成 ---
st.divider()
if st.button("🏆 全事典ロジックに基づき、最終予想ランキングを生成", type="primary", use_container_width=True):
    res_df = pd.DataFrame(calculated_results)
    res_df = res_df[res_df["馬名"] != ""].sort_values(by="スコア", ascending=False)
    
    if not res_df.empty:
        st.balloons()
        st.header(f"🎯 本命推奨馬: {res_df.iloc[0]['馬名']} ({res_df.iloc[0]['騎手']})")
        st.write("### 📊 最終予想スコアボード")
        st.dataframe(res_df[["馬番", "馬名", "スコア", "騎手", "戦略メモ"]], use_container_width=True, hide_index=True)
    else:
        st.warning("出馬表に馬名が入力されていません。値を入力してからボタンを押してください。")
