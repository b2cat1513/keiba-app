import streamlit as st
import pandas as pd
import json
import urllib.parse
import base64
import re
import math
import sqlite3
import uuid
import io
import difflib
import shutil
from datetime import datetime, date
from pathlib import Path
from streamlit.components.v1 import html

try:
    from PIL import Image, ImageOps, ImageFilter
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# ==========================================
# ⚙️ アプリ初期設定 & レイアウト
# ==========================================
st.set_page_config(page_title="ジェニーAI予想ver1.18.14", layout="wide", initial_sidebar_state="collapsed")
st.title("🏆 ジェニーAI予想ver1.18.14（コード整理・軽量化版）")

st.markdown("""
<style>
/* 共通 */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    min-height: 42px;
}

/* スマホ */
@media (max-width: 768px) {
    .block-container {
        padding-top: 0.8rem !important;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
        max-width: 100% !important;
    }
    h1 { font-size: 1.45rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.15rem !important; }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.45rem !important;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        font-size: 16px !important;
        min-height: 46px !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 46px !important;
        font-size: 16px !important;
    }
    div.stButton > button,
    div[data-testid="stDownloadButton"] > button {
        min-height: 48px !important;
        font-size: 1rem !important;
    }
    div[data-testid="stExpander"] details summary {
        min-height: 48px !important;
        align-items: center !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 🛠️ スマホ向け：データを極限まで縮小・Base64圧縮する関数
def encode_for_mobile(data_dict):
    """JSONデータをスマホで扱いやすい短い英数字(Base64)に変換"""
    try:
        json_str = json.dumps(data_dict, ensure_ascii=False)
        b_data = json_str.encode('utf-8')
        base64_str = base64.b64encode(b_data).decode('utf-8')
        return base64_str
    except Exception:
        return ""

def decode_for_mobile(encoded_str):
    """圧縮された文字列を元のデータ(辞書型)に復元（破損補正・従来形式との互換付き）"""
    if not encoded_str: return {}
    encoded_str = encoded_str.strip()
    
    if "data=" in encoded_str:
        encoded_str = encoded_str.split("data=")[-1].split("&")[0]
        
    missing_padding = len(encoded_str) % 4
    if missing_padding:
        encoded_str += '=' * (4 - missing_padding)
        
    try:
        b_data = base64.b64decode(encoded_str)
        json_str = b_data.decode('utf-8')
        return json.loads(json_str)
    except Exception:
        try:
            decoded_url = urllib.parse.unquote(encoded_str)
            if not decoded_url.endswith("}"):
                if decoded_url.count('"') % 2 != 0: decoded_url += '"'
                if decoded_url.count('{') > decoded_url.count('}'): decoded_url += "}"
            return json.loads(decoded_url)
        except Exception as e:
            st.error(f"❌ データの解析に失敗しました。コピーが不完全な可能性があります: {e}")
            return {}

# 🌟 URLパラメータからの自動ロードロジック
if "loaded_data" not in st.session_state:
    st.session_state["loaded_data"] = {}

query_params = st.query_params
if "data" in query_params and not st.session_state["loaded_data"]:
    st.session_state["loaded_data"] = decode_for_mobile(query_params["data"])
    if st.session_state["loaded_data"]:
        st.toast("📥 過去の入力データをURLから正常にロードしました！")

if "history_log" not in st.session_state:
    st.session_state["history_log"] = []

# ==========================================
# 🧩 サイドバー：スマホ専用かんたんロード
# ==========================================
with st.sidebar:
    st.header("⚙️ システム復元メニュー")
    with st.expander("🔄 スマホ専用復元メニュー", expanded=True):
        st.write("保存したセーブコード（またはURL）をコピーした状態で下のボタンを押すか、テキストボックスに直接貼り付けてください。")
        
        html("""
        <script>
        function doLoad() {
            if (!navigator.clipboard) {
                alert('お使いのブラウザは自動読み込みに対応していません。下の入力欄に直接貼り付けてください。');
                return;
            }
            navigator.clipboard.readText().then(text => {
                if(!text) {
                    alert('クリップボードが空か、読み取り許可が得られませんでした。');
                    return;
                }
                const inputs = window.parent.document.getElementsByTagName('input');
                let found = false;
                for (let i = 0; i < inputs.length; i++) {
                    if (inputs[i].getAttribute('aria-label') === 'hidden_mobile_paste') {
                        inputs[i].value = text;
                        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                        found = true;
                        break;
                    }
                }
                if(found) {
                    alert('📋 クリップボードの内容を検出しました！「データを反映して復元」ボタンを押してください。');
                }
            }).catch(err => {
                alert('ブラウザのセキュリティ制限により自動取得できませんでした。下の入力欄に長押しで貼り付けてください。');
            });
        }
        </script>
        """, height=0)
        
        hidden_paste = st.text_input(
            "hidden_mobile_paste", 
            label_visibility="collapsed", 
            key="mobile_bridge", 
            placeholder="ここにコードを貼り付け（長押しペースト）"
        )
        
        if st.button("📋 クリップボードから読み込む", use_container_width=True):
            html("<script>doLoad();</script>", height=0)
            
        if st.button("📥 データを反映して復元", type="primary", use_container_width=True):
            if hidden_paste:
                parsed_data = decode_for_mobile(hidden_paste)
                if parsed_data:
                    st.session_state["loaded_data"] = parsed_data
                    st.success("📥 データを正常に復元しました！")
                    st.rerun()
                else:
                    st.error("❌ データの解析に失敗しました。コードが正しいか確認してください。")
            else:
                st.warning("⚠️ 貼り付け欄にコードを入力するか、上の読み込みボタンをもう一度試してください。")

# ==========================================
# 🏇 1. ジョッキー事典マスターデータ
# ==========================================

# ==========================================
# 🧩 Ver1.18.14 モジュール化
# ==========================================
from keiba_modules.core import *
from keiba_modules.ocr import *

def apply_specialized_image_records(records, auto_track_value):
    st.session_state["loaded_data"].setdefault("rows", {})
    for rec in records:
        gate = int(rec["馬番"])
        key = str(gate)
        prev = st.session_state["loaded_data"]["rows"].get(key, {})
        trainer = rec.get("厩舎", "(未選択)")
        owner = rec.get("馬主", "(未選択)")
        if trainer not in {"", "(未選択)"} and trainer not in TRAINER_OPTIONS:
            TRAINER_OPTIONS.insert(-1, trainer)
        if owner not in {"", "(未選択)"} and owner not in OWNER_OPTIONS:
            OWNER_OPTIONS.insert(-1, owner)
        st.session_state["loaded_data"]["rows"][key] = {
            **prev,
            "num": str(gate),
            "name": rec.get("馬名") or prev.get("name", ""),
            "idx": float(rec.get("U指数") if rec.get("U指数") is not None else prev.get("idx", 0.0)),
            "wgt": float(rec.get("斤量") if rec.get("斤量") is not None else prev.get("wgt", 56.0)),
            "jock": rec.get("今回騎手") if rec.get("今回騎手") in JOCKEY_MASTER else prev.get("jock", "(未選択)"),
            "sire": rec.get("父馬") or prev.get("sire", ""),
            "trainer": trainer if trainer in TRAINER_OPTIONS else prev.get("trainer", "(未選択)"),
            "owner": owner if owner in OWNER_OPTIONS else prev.get("owner", "(未選択)"),
            "l3f": float(rec.get("上がり3F平均") if rec.get("上がり3F平均") is not None else prev.get("l3f", 35.0)),
            "sel_style": rec.get("脚質") if rec.get("脚質") in {"逃げ", "先行", "差し", "追い込み"} else prev.get("sel_style", "選択なし"),
            "wgh": int(prev.get("wgh", 480)),
            "pop": int(prev.get("pop", 10)),
            "win_odds": float(rec.get("単勝") if rec.get("単勝") is not None else prev.get("win_odds", 0.0)),
            "heavy_record": prev.get("heavy_record", False),
            "previous_jockey": rec.get("前走騎手") if rec.get("前走騎手") in JOCKEY_MASTER else prev.get("previous_jockey", "(未選択)"),
            "custom_note": prev.get("custom_note", ""),
            "sel_track": prev.get("sel_track", auto_track_value if auto_track_value in ["芝", "ダート"] else "選択なし"),
            "sel_frame": prev.get("sel_frame", calculate_frame_position(gate)),
            "sel_dist_change": prev.get("sel_dist_change", "同距離"),
        }




# --- 🛰️ 当日環境設定エリア ---
st.header("🛰️ 当日のレース環境")
env_cols = st.columns(6)
with env_cols[0]:
    saved_course = st.session_state["loaded_data"].get("course", "(未選択)")
    sel_course = st.selectbox("🗺️ レースコースを選択:", ["(未選択)"] + list(COURSE_MASTER.keys()), index=(["(未選択)"] + list(COURSE_MASTER.keys())).index(saved_course) if saved_course in COURSE_MASTER else 0)
with env_cols[1]:
    saved_condition = st.session_state["loaded_data"].get("track_condition", "良")
    track_condition = st.selectbox("🌧️ 馬場状態:", ["良", "稍重", "重・不良"], index=["良", "稍重", "重・不良"].index(saved_condition))
with env_cols[2]:
    saved_race_class = st.session_state["loaded_data"].get("race_class", "3勝クラス以下")
    race_class = st.selectbox("🏆 レース格（クラス）:", ["G1", "G2/G3", "オープン/L", "3勝クラス以下"], index=["G1", "G2/G3", "オープン/L", "3勝クラス以下"].index(saved_race_class))
with env_cols[3]:
    track_bias = st.selectbox("🧭 当日の馬場バイアス:", ["フラット", "内・前有利", "外・差し有利"])
with env_cols[4]:
    race_month = st.selectbox("📅 開催月:", list(range(1, 13)), index=date.today().month - 1)

    with st.expander("📈 単勝オッズ統合設定", expanded=False):
        market_weight = st.slider(
            "市場（単勝オッズ）の比率",
            min_value=0.0, max_value=0.50, value=0.30, step=0.05,
            help="的中率重視では0.25〜0.35が目安。上げすぎると人気順に近づきます。",
        )
        ai_weight = round(1.0 - market_weight, 2)
        probability_temperature = st.slider(
            "AI勝率変換の温度",
            min_value=5.0, max_value=20.0, value=10.0, step=0.5,
            help="小さいほど能力上位へ勝率が集中し、大きいほど均等になります。",
        )
        market_smoothing = st.slider(
            "市場確率の平滑化",
            min_value=0.0, max_value=0.30, value=0.15, step=0.05,
            help="過剰人気の影響を弱めます。",
        )
        st.caption(f"現在の統合比率：AI {ai_weight:.0%} ／ 市場 {market_weight:.0%}")
with env_cols[5]:
    total_budget = st.number_input("💰 このレースの想定軍資金 (円):", min_value=100, max_value=100000, value=5000, step=100)

auto_track, auto_dist, good_blood_list, course_note = "選択なし", "選択なし", [], ""
if sel_course != "(未選択)":
    c_info = COURSE_MASTER[sel_course]
    course_note = c_info["note"]
    st.info(f"**【{sel_course} の特徴・有力血統】**\n\n{course_note}")
    auto_track, auto_dist, good_blood_list = c_info["track"], c_info["dist"], c_info["good_lineage"]

st.divider()

# ==========================================
# 📋 コピペ自動入力エリア (タブ切り替えUI)
# ==========================================
st.subheader("📋 一括自動入力エリア")

tab_nk, tab_um, tab_img = st.tabs(["📋 Netkeiba一括入力", "🐎 ウマニティ (Ｕ指数) 一括入力", "📷 画像から自動入力"])

with tab_nk:
    copied_text_nk = st.text_area(
        "Netkeibaの出馬表テキストを貼り付けてください（複数行でも解析します）",
        height=180,
        placeholder="1\nランフォーヴァウ\n牝4\n石川裕紀人\n54.0\n480(+4)",
        key="nk_text"
    )

    if st.button("🚀 Netkeibaデータを解析して展開", use_container_width=True):
        if not copied_text_nk.strip():
            st.warning("テキストエリアが空欄です。")
        else:
            parsed_result = parse_netkeiba_multi_line(copied_text_nk)
            if not parsed_result:
                st.error("馬データが見つかりませんでした。馬番・馬名・性齢・騎手・斤量を含む範囲をコピーしてください。")
            else:
                st.session_state["loaded_data"].setdefault("rows", {})
                imported_gates = []
                unregistered_jockeys = []

                for horse in parsed_result:
                    gate = int(horse["gate"])
                    row_key = str(gate)
                    imported_gates.append(gate)
                    prev_row = st.session_state["loaded_data"]["rows"].get(row_key, {})

                    jockey_name = horse.get("jockey", "").strip()
                    jockey_registered = jockey_name in JOCKEY_MASTER
                    note_parts = [
                        horse.get("sex_age", ""),
                        f"体重増減:{horse.get('change', 0):+d}",
                    ]
                    if jockey_name and not jockey_registered:
                        note_parts.append(f"騎手:{jockey_name}")
                        unregistered_jockeys.append(f"{gate}番 {horse.get('name', '')}: {jockey_name}")

                    st.session_state["loaded_data"]["rows"][row_key] = {
                        "num": str(gate),
                        "name": horse.get("name", ""),
                        "wgt": float(horse.get("jockey_weight", 56.0)),
                        "wgh": int(horse.get("weight", 480)),
                        "jock": jockey_name if jockey_registered else "その他（自由手入力）",
                        "sel_frame": horse.get("frame", calculate_frame_position(gate)),
                        "pop": prev_row.get("pop", 10),
                        "idx": prev_row.get("idx", 0.0),
                        "l3f": prev_row.get("l3f", 35.0),
                        "sire": prev_row.get("sire", ""),
                        "heavy_record": prev_row.get("heavy_record", False),
                        "custom_note": " / ".join(x for x in note_parts if x),
                        "sel_track": prev_row.get(
                            "sel_track",
                            auto_track if auto_track in ["芝", "ダート"] else "選択なし"
                        ),
                        "sel_style": prev_row.get("sel_style", "選択なし"),
                        "sel_dist_change": prev_row.get("sel_dist_change", "同距離"),
                        "previous_jockey": prev_row.get("previous_jockey", "(未選択)"),
                        "trainer": prev_row.get("trainer", "(未選択)"),
                        "owner": prev_row.get("owner", "(未選択)"),
                    }

                st.success(
                    f"🎯 Netkeiba解析成功：{len(parsed_result)}頭を反映しました。"
                    f" 馬番: {', '.join(map(str, sorted(imported_gates)))}"
                )
                if unregistered_jockeys:
                    with st.expander(f"⚠️ 騎手マスター未登録：{len(unregistered_jockeys)}件"):
                        for message in unregistered_jockeys:
                            st.write(message)
                st.rerun()

with tab_um:
    copied_text_um = st.text_area(
        "ウマニティの出馬表・Ｕ指数ページからコピーしたテキストを貼り付けてください",
        height=180,
        placeholder="1 ランフォーヴァウ 88.5\n2 サトノカルナバ 92.1",
        key="um_text"
    )

    if st.button("🚀 ウマニティ Ｕ指数を解析して注入", use_container_width=True):
        if not copied_text_um.strip():
            st.warning("テキストエリアが空欄です。")
        else:
            parsed_um = parse_umanity_multi_line(copied_text_um)
            if not parsed_um:
                st.error("Ｕ指数データが見つかりませんでした。馬番・馬名・Ｕ指数を含む範囲をコピーしてください。")
            else:
                st.session_state["loaded_data"].setdefault("rows", {})
                updated_count = 0
                created_count = 0
                mismatch_messages = []

                for item in parsed_um:
                    gate = int(item["gate"])
                    row_key = str(gate)
                    u_index = float(item["u_index"])
                    umanity_name = normalize_horse_name(item.get("name", ""))
                    existing_row = st.session_state["loaded_data"]["rows"].get(row_key)

                    if existing_row:
                        existing_name = normalize_horse_name(existing_row.get("name", ""))
                        if existing_name and umanity_name and existing_name != umanity_name:
                            mismatch_messages.append(
                                f"{gate}番：Netkeiba『{existing_name}』 / ウマニティ『{umanity_name}』"
                            )
                            continue

                        existing_row["idx"] = u_index
                        if not existing_row.get("name") and umanity_name:
                            existing_row["name"] = umanity_name
                        updated_count += 1
                    else:
                        st.session_state["loaded_data"]["rows"][row_key] = {
                            "num": str(gate),
                            "name": umanity_name,
                            "wgt": 56.0,
                            "wgh": 480,
                            "jock": "その他（自由手入力）",
                            "sel_frame": calculate_frame_position(gate),
                            "pop": 10,
                            "win_odds": 0.0,
                            "idx": u_index,
                            "l3f": 35.0,
                            "sire": "",
                            "heavy_record": False,
                            "custom_note": "ウマニティＵ指数取込",
                            "sel_track": auto_track if auto_track in ["芝", "ダート"] else "選択なし",
                            "sel_style": "選択なし",
                            "sel_dist_change": "同距離",
                            "previous_jockey": "(未選択)",
                            "trainer": "(未選択)",
                            "owner": "(未選択)",
                        }
                        created_count += 1

                st.success(f"🎯 ウマニティＵ指数を反映しました。更新:{updated_count}頭 / 新規:{created_count}頭")
                if mismatch_messages:
                    st.warning(f"馬名不一致のため、{len(mismatch_messages)}頭は更新しませんでした。")
                    with st.expander("馬名不一致の詳細"):
                        for message in mismatch_messages:
                            st.write(message)
                st.rerun()

with tab_img:
    st.write("### 📷 画像から自動入力")
    st.caption("Ver1.18.12：①ウマニティを高速化。先頭馬番を指定した画像では、不要な馬番OCR・厩舎OCR・騎手の多重OCRを省きます。②③はVer1.18.11の安定ロジックを維持します。")

    ocr_status = get_ocr_environment_status()
    with st.expander("🩺 OCR環境診断", expanded=not OCR_AVAILABLE):
        st.write(f"Pillow: {'✅' if ocr_status['pillow_import'] else '❌'}")
        st.write(f"pytesseract: {'✅' if ocr_status['pytesseract_import'] else '❌'}")
        st.write(f"Tesseract本体: {'✅ ' + ocr_status['tesseract_command'] if ocr_status['tesseract_command'] else '❌ 未検出'}")
        langs = ocr_status.get("languages", [])
        st.write(f"日本語データ(jpn): {'✅' if 'jpn' in langs else '❌'}")

    def _ocr_ready():
        return bool(
            OCR_AVAILABLE
            and ocr_status.get("tesseract_command")
            and "jpn" in ocr_status.get("languages", [])
        )

    def _dedupe_gate(records):
        out = {}
        for r in records:
            try:
                g = int(r.get("馬番"))
            except Exception:
                continue
            out[g] = r
        return [out[k] for k in sorted(out)]

    def _dedupe_horse(records):
        out = {}
        for r in records:
            name = normalize_horse_name(r.get("馬名", ""))
            if name:
                out[name] = r
        return list(out.values())

    for key in [
        "v187_umanity_records", "v187_profile_records", "v187_history_records",
        "v187_raw_texts", "v187_diagnostics"
    ]:
        if key not in st.session_state:
            st.session_state[key] = [] if key != "v187_raw_texts" else []

    mobile_ocr_mode = st.session_state.get("input_screen_mode", "📱 スマホ") == "📱 スマホ"
    upload_mode = st.radio(
        "画像の選び方",
        ["📱 スマホ：1枚ずつ", "🖥️ PC：複数枚まとめて"],
        index=0 if mobile_ocr_mode else 1,
        horizontal=True,
        key="ocr_upload_mode_v187",
    )

    # --------------------------------------------------
    # ① ウマニティ
    # --------------------------------------------------
    st.markdown("#### ① ウマニティ")
    st.caption("取得：馬番・馬名・単勝・U指数・斤量・今回騎手。Ver1.18.12では先頭馬番指定時に高速OCRを使い、処理回数を大幅に削減します。")

    if upload_mode == "📱 スマホ：1枚ずつ":
        u_one = st.file_uploader(
            "ウマニティ画像",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="uploader_u_v187_mobile",
        )
        u_files = [u_one] if u_one else []
    else:
        u_files = st.file_uploader(
            "ウマニティ画像",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="uploader_u_v187_pc",
        ) or []

    u_start_map = {}
    for idx, f in enumerate(u_files):
        c1, c2 = st.columns([2.6, 1])
        c1.write(f"📷 {f.name}")
        u_start_map[f.name] = c2.selectbox(
            "先頭馬番",
            list(range(1, 19)),
            index=min(idx * 8, 17) if upload_mode == "🖥️ PC：複数枚まとめて" else 0,
            key=f"u_start_v187_{idx}_{f.name}",
            label_visibility="collapsed",
        )

    if st.button("① ウマニティだけ解析", use_container_width=True, disabled=not u_files):
        if not _ocr_ready():
            st.error("OCR環境を確認してください。Tesseract本体と日本語データ(jpn)が必要です。")
        else:
            new_records, new_raw, diagnostics, errors = [], [], [], []
            with st.spinner("ウマニティ画像を解析しています…"):
                for f in u_files:
                    try:
                        raw = extract_text_from_screenshot(f)
                        recs = parse_umanity_screenshot_image(
                            f, raw, forced_start_gate=int(u_start_map[f.name])
                        )
                        new_records.extend(recs)
                        new_raw.append((f"ウマニティ:{f.name}", raw))
                        diagnostics.append({
                            "画像": f.name, "種類": "ウマニティ",
                            "指定": f"先頭 {u_start_map[f.name]}番",
                            "抽出頭数": len(recs),
                            "抽出馬": " / ".join(f"{r.get('馬番')} {r.get('馬名')}" for r in recs),
                        })
                    except Exception as exc:
                        errors.append(f"{f.name}: {exc}")

            # 今回指定された馬番範囲は新結果で置換
            old = {int(r["馬番"]): r for r in st.session_state["v187_umanity_records"] if r.get("馬番")}
            for f in u_files:
                sg = int(u_start_map[f.name])
                for g in range(sg, min(19, sg + 8)):
                    old.pop(g, None)
            for r in new_records:
                if r.get("馬番"):
                    old[int(r["馬番"])] = r
            st.session_state["v187_umanity_records"] = [old[k] for k in sorted(old)]
            st.session_state["v187_raw_texts"].extend(new_raw)
            st.session_state["v187_diagnostics"].extend(diagnostics)
            if errors:
                st.warning("一部の画像でエラーがありました。")
                for e in errors:
                    st.code(e)
            st.success(f"① ウマニティ：{len(new_records)}頭を解析しました。")

    u_records = st.session_state["v187_umanity_records"]
    gate_horse_map = {
        int(r["馬番"]): normalize_horse_name(r.get("馬名", ""))
        for r in u_records if r.get("馬番") and r.get("馬名")
    }
    horse_gate_map = {name: gate for gate, name in gate_horse_map.items() if name}

    if u_records:
        st.dataframe(
            pd.DataFrame(u_records)[[c for c in ["馬番","馬名","U指数","今回騎手","単勝","斤量"] if c in pd.DataFrame(u_records).columns]],
            use_container_width=True, hide_index=True,
        )

    # --------------------------------------------------
    # ② 競馬ラボ・プロフィール
    # --------------------------------------------------
    st.markdown("#### ② 競馬ラボ・プロフィール")
    st.caption("取得：父馬・厩舎・馬主。画像ごとの対象馬番を必ず指定し、その馬へ直接結合します。")

    if upload_mode == "📱 スマホ：1枚ずつ":
        p_one = st.file_uploader(
            "プロフィール画像",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="uploader_p_v187_mobile",
        )
        p_files = [p_one] if p_one else []
    else:
        p_files = st.file_uploader(
            "プロフィール画像",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="uploader_p_v187_pc",
        ) or []

    p_gate_map = {}
    gate_choices = sorted(gate_horse_map.keys()) if gate_horse_map else list(range(1,19))
    for idx, f in enumerate(p_files):
        c1, c2 = st.columns([2.6, 1])
        c1.write(f"📷 {f.name}")
        default_index = min(idx, len(gate_choices)-1) if gate_choices else 0
        p_gate_map[f.name] = c2.selectbox(
            "対象馬番", gate_choices,
            index=default_index,
            key=f"p_gate_v187_{idx}_{f.name}",
            label_visibility="collapsed",
        )

    if st.button("② プロフィールだけ解析", use_container_width=True, disabled=not p_files):
        if not u_records:
            st.error("先に①ウマニティを解析してください。")
        elif not _ocr_ready():
            st.error("OCR環境を確認してください。")
        else:
            new_records, new_raw, diagnostics, errors = [], [], [], []
            with st.spinner("競馬ラボ・プロフィールを解析しています…"):
                for f in p_files:
                    try:
                        gate = int(p_gate_map[f.name])
                        target_horse = gate_horse_map.get(gate)
                        if not target_horse:
                            errors.append(f"{f.name}: {gate}番の馬名がウマニティ側にありません")
                            continue
                        raw = extract_text_from_screenshot(f)
                        recs = parse_keibalab_profile_screenshot_image(
                            f, horse_gate_map, fallback_horse=target_horse
                        )
                        # 指定馬番を最終的に強制
                        for r in recs:
                            r["馬番"] = gate
                            r["馬名"] = target_horse
                        new_records.extend(recs)
                        new_raw.append((f"競馬ラボ・プロフィール:{f.name}", raw))
                        diagnostics.append({
                            "画像": f.name, "種類": "競馬ラボ・プロフィール",
                            "指定": f"{gate} {target_horse}",
                            "抽出頭数": len(recs),
                            "抽出馬": f"{gate} {target_horse}" if recs else "項目取得失敗",
                        })
                    except Exception as exc:
                        errors.append(f"{f.name}: {exc}")

            old = {int(r["馬番"]): r for r in st.session_state["v187_profile_records"] if r.get("馬番")}
            for r in new_records:
                old[int(r["馬番"])] = r
            st.session_state["v187_profile_records"] = [old[k] for k in sorted(old)]
            st.session_state["v187_raw_texts"].extend(new_raw)
            st.session_state["v187_diagnostics"].extend(diagnostics)
            if errors:
                st.warning("一部のプロフィール画像で取得できませんでした。")
                for e in errors:
                    st.code(e)
            st.success(f"② プロフィール：{len(new_records)}頭分を解析しました。")

    # --------------------------------------------------
    # ③ 競馬ラボ・過去5走
    # --------------------------------------------------
    st.markdown("#### ③ 競馬ラボ・過去5走")
    st.info("🛡️ Ver1.18.11では、Ver1.18.10で0件になった行分割OCRを主判定から外し、Ver1.18.9で取れていた前走騎手・上がり3F方式を復元しています。")
    st.caption("取得：前走騎手・上がり3F平均。全文OCRを複数方式で照合し、同じ馬の複数画像は境界重複を除きながら最大5走まで補完します。")

    if upload_mode == "📱 スマホ：1枚ずつ":
        h_one = st.file_uploader(
            "過去5走画像",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="uploader_h_v187_mobile",
        )
        h_files = [h_one] if h_one else []
    else:
        h_files = st.file_uploader(
            "過去5走画像",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="uploader_h_v187_pc",
        ) or []

    h_gate_map = {}
    for idx, f in enumerate(h_files):
        c1, c2 = st.columns([2.6, 1])
        c1.write(f"📷 {f.name}")
        default_index = min(idx // 2, len(gate_choices)-1) if gate_choices else 0
        h_gate_map[f.name] = c2.selectbox(
            "対象馬番", gate_choices,
            index=default_index,
            key=f"h_gate_v187_{idx}_{f.name}",
            label_visibility="collapsed",
        )

    if st.button("③ 過去5走だけ解析", use_container_width=True, disabled=not h_files):
        if not u_records:
            st.error("先に①ウマニティを解析してください。")
        elif not _ocr_ready():
            st.error("OCR環境を確認してください。")
        else:
            # 同じ馬に複数画像がある場合、画像単位の結果を後で統合
            by_gate = {}
            new_raw, diagnostics, errors = [], [], []
            with st.spinner("競馬ラボ・過去5走を解析しています…"):
                for f in h_files:
                    try:
                        gate = int(h_gate_map[f.name])
                        target_horse = gate_horse_map.get(gate)
                        if not target_horse:
                            errors.append(f"{f.name}: {gate}番の馬名がウマニティ側にありません")
                            continue
                        raw = extract_text_from_screenshot(f)
                        recs = parse_keibalab_history_screenshot_image(
                            f, horse_gate_map, fallback_horse=target_horse
                        )
                        rec = recs[0] if recs else {
                            "馬番": gate, "馬名": target_horse,
                            "前走騎手": "(未選択)", "上がり3F平均": None,
                            "上がり取得数": 0, "取得元": "競馬ラボ・過去5走画像"
                        }
                        rec["馬番"] = gate
                        rec["馬名"] = target_horse
                        by_gate.setdefault(gate, []).append(rec)
                        new_raw.append((f"競馬ラボ・過去5走:{f.name}", raw))
                        diagnostics.append({
                            "画像": f.name, "種類": "競馬ラボ・過去5走",
                            "指定": f"{gate} {target_horse}",
                            "抽出頭数": 1 if recs else 0,
                            "抽出馬": f"{gate} {target_horse}",
                        })
                    except Exception as exc:
                        errors.append(f"{f.name}: {exc}")

            def _parse_breakdown(rec):
                vals = []
                for token in str(rec.get("上がり3F内訳", "") or "").split("/"):
                    token = token.strip()
                    try:
                        v = round(float(token), 1)
                    except Exception:
                        continue
                    if 30.0 <= v <= 42.9:
                        vals.append(v)
                return vals

            def _append_with_overlap(base, seq):
                """連続スクショの重複を吸収して結合。
                完全な並び一致に加えて、境界の同一値1個も重複とみなす。
                """
                if not base:
                    return list(seq)
                if not seq:
                    return base
                max_overlap = min(len(base), len(seq))
                overlap = 0
                for k in range(max_overlap, 0, -1):
                    if base[-k:] == seq[:k]:
                        overlap = k
                        break
                if overlap == 0 and base[-1] == seq[0]:
                    overlap = 1
                return base + seq[overlap:]

            new_records = []
            for gate, recs in sorted(by_gate.items()):
                target_horse = gate_horse_map.get(gate, "")

                # 前走騎手は最初の画像を優先。未取得なら後続画像から補完。
                jockey = next(
                    (r.get("前走騎手") for r in recs
                     if r.get("前走騎手") not in {None, "", "(未選択)"}),
                    "(未選択)"
                )

                # 同じ馬に2枚以上ある場合は「最良画像1枚」ではなく、
                # アップロード順に上がり値列を連結して最大5走にする。
                combined = []
                for r in recs:
                    seq = _parse_breakdown(r)
                    combined = _append_with_overlap(combined, seq)
                    if len(combined) >= 5:
                        break

                combined = combined[:5]
                avg = round(sum(combined) / len(combined), 2) if combined else None

                new_records.append({
                    "馬番": gate, "馬名": target_horse,
                    "前走騎手": jockey,
                    "上がり3F平均": avg,
                    "上がり取得数": len(combined),
                    "上がり3F内訳": " / ".join(f"{v:.1f}" for v in combined),
                    "取得元": "競馬ラボ・過去5走画像",
                })

            old = {int(r["馬番"]): r for r in st.session_state["v187_history_records"] if r.get("馬番")}
            for r in new_records:
                old[int(r["馬番"])] = r
            st.session_state["v187_history_records"] = [old[k] for k in sorted(old)]
            st.session_state["v187_raw_texts"].extend(new_raw)
            st.session_state["v187_diagnostics"].extend(diagnostics)
            if errors:
                st.warning("一部の過去5走画像で取得できませんでした。")
                for e in errors:
                    st.code(e)
            st.success(f"③ 過去5走：{len(new_records)}頭分を解析しました。")

    # --------------------------------------------------
    # 統合確認
    # --------------------------------------------------
    merged = merge_source_records(
        st.session_state["v187_umanity_records"],
        st.session_state["v187_profile_records"],
        st.session_state["v187_history_records"],
    )
    if merged:
        st.markdown("#### ✅ 統合確認表")
        preview_df = pd.DataFrame(merged)
        edited_df = st.data_editor(
            preview_df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "馬番": st.column_config.NumberColumn(min_value=1, max_value=18, step=1),
                "単勝": st.column_config.NumberColumn(format="%.1f"),
                "U指数": st.column_config.NumberColumn(format="%.2f"),
                "斤量": st.column_config.NumberColumn(format="%.1f"),
                "上がり3F平均": st.column_config.NumberColumn(format="%.2f"),
                "上がり取得数": st.column_config.NumberColumn(min_value=0, max_value=5, step=1),
            },
            key="ocr_preview_editor_v187",
        )

        c1, c2 = st.columns(2)
        if c1.button("✅ 確認した内容を出馬表へ反映", type="primary", use_container_width=True):
            apply_specialized_image_records(edited_df.to_dict("records"), auto_track)
            st.success("出馬表へ反映しました。")
            st.rerun()

        if c2.button("🗑️ OCR結果を全部クリア", use_container_width=True):
            for key in [
                "v187_umanity_records", "v187_profile_records", "v187_history_records",
                "v187_raw_texts", "v187_diagnostics"
            ]:
                st.session_state[key] = []
            st.rerun()

    if st.session_state.get("v187_diagnostics"):
        with st.expander("🧪 画像ごとの抽出診断", expanded=False):
            st.dataframe(
                pd.DataFrame(st.session_state["v187_diagnostics"]),
                use_container_width=True, hide_index=True
            )

    if st.session_state.get("v187_raw_texts"):
        with st.expander("OCR原文を確認（読み取り調整用）"):
            for filename, raw in st.session_state["v187_raw_texts"][-50:]:
                st.markdown(f"**{filename}**")
                st.code(raw[:10000])

st.divider()

class _NullScoreCell:
    """スマホで非表示の馬用。score_cell.write() を安全に無視する。"""
    def write(self, *args, **kwargs):
        return None

_NULL_SCORE_CELL = _NullScoreCell()

# ==========================================
# 📋 出馬表入力エリア
# ==========================================
st.write("### 📝 出馬表データ入力")

if "input_screen_mode" not in st.session_state:
    st.session_state["input_screen_mode"] = "📱 スマホ"

screen_mode = st.radio(
    "入力画面",
    ["📱 スマホ", "🖥️ PC"],
    key="input_screen_mode",
    horizontal=True,
)
mobile_mode = (screen_mode == "📱 スマホ")

current_inputs = {"course": sel_course, "track_condition": track_condition, "race_class": race_class, "rows": {}}
style_counts = {"逃げ": 0, "先行": 0, "差し": 0, "追い込み": 0}
row_tmp_data = []

jock_list = sorted([k for k in JOCKEY_MASTER.keys() if k != "その他（自由手入力）"]) + ["その他（自由手入力）"]
jockey_options = ["(未選択)"] + jock_list
track_options = ["選択なし", "芝", "ダート"]
style_options = ["選択なし", "逃げ", "先行", "差し", "追い込み"]
frame_options = ["選択なし", "内枠", "外枠"]
distance_options = ["同距離", "距離短縮", "距離延長"]

def _safe_select_index(options, value, fallback=0):
    try:
        return options.index(value)
    except ValueError:
        return fallback

if not mobile_mode:
    c_widths = [0.55, 1.20, 0.52, 0.65, 0.60, 0.58, 0.63, 0.58, 1.10, 0.52, 1.00, 1.00, 0.95, 0.95, 1.05, 0.68, 0.72, 0.72, 0.78, 0.72]
    cols = st.columns(c_widths)
    headers = ["馬番", "馬名", "人気", "単勝", "指数", "斤量", "馬体重", "前3F", "父馬", "道悪", "今回騎手", "前走騎手", "厩舎", "馬主", "手入力メモ", "馬場", "脚質", "枠有利", "前走距離", "能力値"]
    for col, h in zip(cols, headers):
        col.write(f"**{h}**")

    for i in range(1, 19):
        c = st.columns(c_widths)
        s_row = st.session_state["loaded_data"].get("rows", {}).get(str(i), {})

        num = c[0].text_input(f"num_{i}", value=s_row.get("num", str(i)), label_visibility="collapsed")
        name = c[1].text_input(f"name_{i}", value=s_row.get("name", ""), label_visibility="collapsed")
        pop = c[2].number_input(f"pop_{i}", min_value=1, max_value=18, value=int(s_row.get("pop", 10)), label_visibility="collapsed")
        win_odds = c[3].number_input(f"win_odds_{i}", min_value=0.0, max_value=999.9, value=float(s_row.get("win_odds", 0.0) or 0.0), step=0.1, label_visibility="collapsed", help="未入力は0.0")
        idx = c[4].number_input(f"idx_{i}", value=float(s_row.get("idx", 0.0)), step=0.1, label_visibility="collapsed")
        wgt = c[5].number_input(f"wgt_{i}", min_value=48.0, max_value=62.0, value=float(s_row.get("wgt", 56.0)), step=0.5, label_visibility="collapsed")
        wgh = c[6].number_input(f"wgh_{i}", min_value=350, max_value=600, value=int(s_row.get("wgh", 480)), step=2, label_visibility="collapsed")
        l3f = c[7].number_input(f"l3f_{i}", value=float(s_row.get("l3f", 35.0)), step=0.1, label_visibility="collapsed")
        sire = c[8].text_input(f"sire_{i}", value=s_row.get("sire", ""), label_visibility="collapsed", placeholder="父馬")
        has_heavy_record = c[9].checkbox(f"rec_{i}", value=s_row.get("heavy_record", False), label_visibility="collapsed")

        saved_jockey = normalize_jockey_name(s_row.get("jock", "(未選択)"))
        jock = c[10].selectbox(f"jock_{i}", jockey_options, index=_safe_select_index(jockey_options, saved_jockey), label_visibility="collapsed")
        saved_previous = normalize_jockey_name(s_row.get("previous_jockey", "(未選択)"))
        previous_jockey = c[11].selectbox(f"previous_jockey_{i}", jockey_options, index=_safe_select_index(jockey_options, saved_previous), label_visibility="collapsed")
        trainer = c[12].selectbox(f"trainer_{i}", TRAINER_OPTIONS, index=_safe_select_index(TRAINER_OPTIONS, s_row.get("trainer", "(未選択)")), label_visibility="collapsed")
        owner = c[13].selectbox(f"owner_{i}", OWNER_OPTIONS, index=_safe_select_index(OWNER_OPTIONS, s_row.get("owner", "(未選択)")), label_visibility="collapsed")
        custom_note = c[14].text_input(f"custom_note_{i}", value=s_row.get("custom_note", ""), label_visibility="collapsed", placeholder="性齢・特徴メモ")

        default_track = s_row.get("sel_track", auto_track if auto_track in ["芝", "ダート"] else "選択なし")
        sel_track = c[15].selectbox(f"track_{i}", track_options, index=_safe_select_index(track_options, default_track), label_visibility="collapsed")
        sel_style = c[16].selectbox(f"style_{i}", style_options, index=_safe_select_index(style_options, s_row.get("sel_style", "選択なし")), label_visibility="collapsed")

        num_int = safe_int_convert(num, i)
        f_def_idx = 1 if num_int <= 8 else (2 if num_int >= 13 else 0)
        sel_frame = c[17].selectbox(f"frame_{i}", frame_options, index=_safe_select_index(frame_options, s_row.get("sel_frame", frame_options[f_def_idx])), label_visibility="collapsed")
        sel_dist_change = c[18].selectbox(f"dist_change_{i}", distance_options, index=_safe_select_index(distance_options, s_row.get("sel_dist_change", "同距離")), label_visibility="collapsed")
        score_cell = c[19]

        if name and sel_style in style_counts:
            style_counts[sel_style] += 1

        current_inputs["rows"][str(i)] = {
            "num": num, "name": name, "pop": pop, "win_odds": win_odds, "idx": idx, "wgt": wgt, "wgh": wgh, "l3f": l3f, "sire": sire, "heavy_record": has_heavy_record,
            "jock": jock, "previous_jockey": previous_jockey, "trainer": trainer, "owner": owner,
            "custom_note": custom_note, "sel_track": sel_track, "sel_style": sel_style,
            "sel_frame": sel_frame, "sel_dist_change": sel_dist_change
        }
        row_tmp_data.append((num, name, pop, win_odds, idx, wgt, wgh, l3f, sire, has_heavy_record, jock, previous_jockey, trainer, owner, custom_note, sel_track, sel_style, sel_frame, sel_dist_change, score_cell))

else:
    st.success("📱 スマホ入力：1頭ずつ編集します。入力値はその場で保持されます。")

    # Which horse to edit
    if "mobile_horse_no" not in st.session_state:
        st.session_state["mobile_horse_no"] = 1

    horse_no = st.select_slider(
        "編集する馬番",
        options=list(range(1, 19)),
        value=int(st.session_state["mobile_horse_no"]),
        key="mobile_horse_selector",
    )
    st.session_state["mobile_horse_no"] = int(horse_no)

    # All 18 rows must still be present in current_inputs for save/prediction.
    # The selected horse gets real widgets; the others are carried from session/loaded data.
    for i in range(1, 19):
        s_row = st.session_state["loaded_data"].get("rows", {}).get(str(i), {})

        if i != horse_no:
            row = {
                "num": st.session_state.get(f"num_{i}", s_row.get("num", str(i))),
                "name": st.session_state.get(f"name_{i}", s_row.get("name", "")),
                "pop": st.session_state.get(f"pop_{i}", int(s_row.get("pop", 10))),
                "win_odds": st.session_state.get(f"win_odds_{i}", float(s_row.get("win_odds", 0.0) or 0.0)),
                "idx": st.session_state.get(f"idx_{i}", float(s_row.get("idx", 0.0))),
                "wgt": st.session_state.get(f"wgt_{i}", float(s_row.get("wgt", 56.0))),
                "wgh": st.session_state.get(f"wgh_{i}", int(s_row.get("wgh", 480))),
                "l3f": st.session_state.get(f"l3f_{i}", float(s_row.get("l3f", 35.0))),
                "sire": st.session_state.get(f"sire_{i}", s_row.get("sire", "")),
                "heavy_record": st.session_state.get(f"rec_{i}", s_row.get("heavy_record", False)),
                "jock": st.session_state.get(f"jock_{i}", normalize_jockey_name(s_row.get("jock", "(未選択)"))),
                "previous_jockey": st.session_state.get(f"previous_jockey_{i}", normalize_jockey_name(s_row.get("previous_jockey", "(未選択)"))),
                "trainer": st.session_state.get(f"trainer_{i}", s_row.get("trainer", "(未選択)")),
                "owner": st.session_state.get(f"owner_{i}", s_row.get("owner", "(未選択)")),
                "custom_note": st.session_state.get(f"custom_note_{i}", s_row.get("custom_note", "")),
                "sel_track": st.session_state.get(f"track_{i}", s_row.get("sel_track", auto_track if auto_track in ["芝", "ダート"] else "選択なし")),
                "sel_style": st.session_state.get(f"style_{i}", s_row.get("sel_style", "選択なし")),
                "sel_frame": st.session_state.get(f"frame_{i}", s_row.get("sel_frame", "選択なし")),
                "sel_dist_change": st.session_state.get(f"dist_change_{i}", s_row.get("sel_dist_change", "同距離")),
            }
            current_inputs["rows"][str(i)] = row
            if row["name"] and row["sel_style"] in style_counts:
                style_counts[row["sel_style"]] += 1
            # placeholder keeps downstream tuple structure compatible
            row_tmp_data.append((
                row["num"], row["name"], row["pop"], row["win_odds"], row["idx"], row["wgt"], row["wgh"], row["l3f"],
                row["sire"], row["heavy_record"], row["jock"], row["previous_jockey"], row["trainer"], row["owner"],
                row["custom_note"], row["sel_track"], row["sel_style"], row["sel_frame"], row["sel_dist_change"], _NULL_SCORE_CELL
            ))
            continue

        st.markdown(f"## 🐎 {i}番の入力")
        st.caption("OCRで取得できた項目は自動入力されます。必要な所だけ修正してください。")

        num = st.text_input("馬番", value=s_row.get("num", str(i)), key=f"num_{i}")
        name = st.text_input("馬名", value=s_row.get("name", ""), key=f"name_{i}", placeholder="馬名")

        c1, c2 = st.columns(2)
        pop = c1.number_input("人気", min_value=1, max_value=18, value=int(s_row.get("pop", 10)), key=f"pop_{i}")
        win_odds = c2.number_input("単勝", min_value=0.0, max_value=999.9, value=float(s_row.get("win_odds", 0.0) or 0.0), step=0.1, key=f"win_odds_{i}")

        c1, c2 = st.columns(2)
        idx = c1.number_input("U指数", value=float(s_row.get("idx", 0.0)), step=0.1, key=f"idx_{i}")
        wgt = c2.number_input("斤量", min_value=48.0, max_value=62.0, value=float(s_row.get("wgt", 56.0)), step=0.5, key=f"wgt_{i}")

        c1, c2 = st.columns(2)
        wgh = c1.number_input("馬体重", min_value=350, max_value=600, value=int(s_row.get("wgh", 480)), step=2, key=f"wgh_{i}")
        l3f = c2.number_input("上がり3F平均", value=float(s_row.get("l3f", 35.0)), step=0.1, key=f"l3f_{i}")

        sire = st.text_input("父馬", value=s_row.get("sire", ""), key=f"sire_{i}")

        c1, c2 = st.columns(2)
        saved_jockey = normalize_jockey_name(s_row.get("jock", "(未選択)"))
        jock = c1.selectbox("今回騎手", jockey_options, index=_safe_select_index(jockey_options, saved_jockey), key=f"jock_{i}")
        saved_previous = normalize_jockey_name(s_row.get("previous_jockey", "(未選択)"))
        previous_jockey = c2.selectbox("前走騎手", jockey_options, index=_safe_select_index(jockey_options, saved_previous), key=f"previous_jockey_{i}")

        c1, c2 = st.columns(2)
        trainer = c1.selectbox("厩舎", TRAINER_OPTIONS, index=_safe_select_index(TRAINER_OPTIONS, s_row.get("trainer", "(未選択)")), key=f"trainer_{i}")
        owner = c2.selectbox("馬主", OWNER_OPTIONS, index=_safe_select_index(OWNER_OPTIONS, s_row.get("owner", "(未選択)")), key=f"owner_{i}")

        custom_note = st.text_input("手入力メモ", value=s_row.get("custom_note", ""), key=f"custom_note_{i}")

        c1, c2 = st.columns(2)
        default_track = s_row.get("sel_track", auto_track if auto_track in ["芝", "ダート"] else "選択なし")
        sel_track = c1.selectbox("馬場", track_options, index=_safe_select_index(track_options, default_track), key=f"track_{i}")
        sel_style = c2.selectbox("脚質", style_options, index=_safe_select_index(style_options, s_row.get("sel_style", "選択なし")), key=f"style_{i}")

        c1, c2 = st.columns(2)
        num_int = safe_int_convert(num, i)
        f_def_idx = 1 if num_int <= 8 else (2 if num_int >= 13 else 0)
        sel_frame = c1.selectbox("枠有利", frame_options, index=_safe_select_index(frame_options, s_row.get("sel_frame", frame_options[f_def_idx])), key=f"frame_{i}")
        sel_dist_change = c2.selectbox("前走距離", distance_options, index=_safe_select_index(distance_options, s_row.get("sel_dist_change", "同距離")), key=f"dist_change_{i}")

        has_heavy_record = st.checkbox("道悪実績あり", value=s_row.get("heavy_record", False), key=f"rec_{i}")
        score_cell = st.empty()

        row = {
            "num": num, "name": name, "pop": pop, "win_odds": win_odds, "idx": idx, "wgt": wgt, "wgh": wgh, "l3f": l3f,
            "sire": sire, "heavy_record": has_heavy_record, "jock": jock, "previous_jockey": previous_jockey,
            "trainer": trainer, "owner": owner, "custom_note": custom_note, "sel_track": sel_track,
            "sel_style": sel_style, "sel_frame": sel_frame, "sel_dist_change": sel_dist_change
        }
        current_inputs["rows"][str(i)] = row
        if name and sel_style in style_counts:
            style_counts[sel_style] += 1

        row_tmp_data.append((
            num, name, pop, win_odds, idx, wgt, wgh, l3f, sire, has_heavy_record, jock, previous_jockey,
            trainer, owner, custom_note, sel_track, sel_style, sel_frame, sel_dist_change, score_cell
        ))

    # Put tuples back into horse-number order because downstream scoring expects 1..18.
    row_tmp_data = sorted(
        row_tmp_data,
        key=lambda x: safe_int_convert(x[0], 999)
    )

    st.divider()
    left, middle, right = st.columns([1, 1, 1])

    if left.button("◀ 前の馬", use_container_width=True, disabled=(horse_no <= 1)):
        st.session_state["mobile_horse_no"] = max(1, horse_no - 1)
        st.session_state["mobile_horse_selector"] = max(1, horse_no - 1)
        st.rerun()

    if middle.button("💾 入力を保存", type="primary", use_container_width=True):
        st.session_state["loaded_data"]["rows"][str(horse_no)] = current_inputs["rows"][str(horse_no)]
        st.success(f"{horse_no}番を保存しました。")

    if right.button("次の馬 ▶", use_container_width=True, disabled=(horse_no >= 18)):
        st.session_state["loaded_data"]["rows"][str(horse_no)] = current_inputs["rows"][str(horse_no)]
        st.session_state["mobile_horse_no"] = min(18, horse_no + 1)
        st.session_state["mobile_horse_selector"] = min(18, horse_no + 1)
        st.rerun()


# ==========================================
# 🏁 4. 展開（ペース）AI自動予測
# ==========================================
st.write("### 🏁 展開（ペース）AI自動予測結果")
pace_status = "ミドルペース（フラット）"
pace_bonus = {"逃げ": 0.0, "先行": 0.0, "差し": 0.0, "追い込み": 0.0}

total_active_horses = sum(style_counts.values())
if total_active_horses >= 3:
    front_runner_ratio = (style_counts["逃げ"] + style_counts["先行"]) / total_active_horses
    if style_counts["逃げ"] >= 3 or front_runner_ratio >= 0.55:
        pace_status = "🔥 ハイペース（前崩れ・差し追い込み超有利）"
        pace_bonus = {"逃げ": -4.0, "先行": -2.0, "差し": 3.0, "追い込み": 5.0}
    elif style_counts["逃げ"] == 0 and front_runner_ratio <= 0.25:
        pace_status = "🐌 スローペース（超前残り・逃げ先行絶対有利）"
        pace_bonus = {"逃げ": 5.0, "先行": 3.0, "差し": -2.0, "追い込み": -4.0}

st.info(f"**現在の登録馬から算出された展開:** {pace_status} (逃げ:{style_counts['逃げ']}頭, 先行:{style_counts['先行']}頭, 差し:{style_counts['差し']}頭, 追込:{style_counts['追い込み']}頭)")

# ==========================================
# 🧠 Ver1.07 学習結果による配点自動調整
# ==========================================
LEARNING_DB_PATH = Path(__file__).with_name("keiba_learning.db")
LEARNING_FACTORS = [
    "指数", "斤量", "馬体重", "格・斤量価値", "馬番・枠",
    "血統・コース", "脚質・距離", "騎手補正", "騎手条件", "人気補正",
    "展開補正", "道悪補正"
]
MIN_LEARNING_SAMPLES = 10
MIN_TOTAL_RECORDS = 15
MIN_WEIGHT = 0.85
MAX_WEIGHT = 1.15
LEARNING_STRENGTH = 0.40


def init_auto_weight_tables():
    """自動調整用テーブルと設定を先に準備する。"""
    with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_weights (
                factor TEXT PRIMARY KEY,
                multiplier REAL NOT NULL DEFAULT 1.0,
                sample_count INTEGER NOT NULL DEFAULT 0,
                total_records INTEGER NOT NULL DEFAULT 0,
                lift REAL NOT NULL DEFAULT 0.0,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        """)
        conn.execute(
            "INSERT OR IGNORE INTO learning_settings(setting_key, setting_value) VALUES ('auto_adjust_enabled', '1')"
        )
        now = datetime.now().isoformat(timespec="seconds")
        for factor in LEARNING_FACTORS:
            conn.execute("""
                INSERT OR IGNORE INTO learning_weights(
                    factor, multiplier, sample_count, total_records, lift, updated_at
                ) VALUES (?, 1.0, 0, 0, 0.0, ?)
            """, (factor, now))
        conn.commit()


def is_auto_adjust_enabled():
    try:
        with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
            row = conn.execute(
                "SELECT setting_value FROM learning_settings WHERE setting_key = 'auto_adjust_enabled'"
            ).fetchone()
        return bool(row and row[0] == "1")
    except sqlite3.Error:
        return False


def set_auto_adjust_enabled(enabled):
    with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
        conn.execute("""
            INSERT INTO learning_settings(setting_key, setting_value) VALUES ('auto_adjust_enabled', ?)
            ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value
        """, ("1" if enabled else "0",))
        conn.commit()


def recalculate_learning_weights():
    """結果登録済み履歴から、安全幅内で項目倍率を再計算する。"""
    init_auto_weight_tables()
    records = {factor: [] for factor in LEARNING_FACTORS}

    try:
        with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT p.breakdown_json, r.actual_rank
                FROM predictions p
                INNER JOIN race_results r ON p.prediction_id = r.prediction_id
                WHERE r.actual_rank IS NOT NULL
            """).fetchall()
    except sqlite3.Error:
        rows = []

    for row in rows:
        try:
            breakdown = json.loads(row["breakdown_json"] or "{}")
        except (TypeError, json.JSONDecodeError):
            continue
        placed = 1 if int(row["actual_rank"]) <= 3 else 0
        for factor in LEARNING_FACTORS:
            try:
                value = float(breakdown.get(factor, 0.0))
            except (TypeError, ValueError):
                value = 0.0
            records[factor].append((value, placed))

    now = datetime.now().isoformat(timespec="seconds")
    calculated = {}
    with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
        for factor, values in records.items():
            total_records = len(values)
            positives = [placed for value, placed in values if value > 0]
            all_places = [placed for _, placed in values]
            sample_count = len(positives)

            if sample_count >= MIN_LEARNING_SAMPLES and total_records >= MIN_TOTAL_RECORDS:
                positive_rate = sum(positives) / sample_count
                overall_rate = sum(all_places) / total_records if total_records else 0.0
                lift = (positive_rate - overall_rate) * 100.0
                raw_multiplier = 1.0 + (lift / 100.0) * LEARNING_STRENGTH
                multiplier = max(MIN_WEIGHT, min(MAX_WEIGHT, raw_multiplier))
            else:
                lift = 0.0
                multiplier = 1.0

            multiplier = round(multiplier, 3)
            lift = round(lift, 2)
            conn.execute("""
                INSERT INTO learning_weights(
                    factor, multiplier, sample_count, total_records, lift, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(factor) DO UPDATE SET
                    multiplier = excluded.multiplier,
                    sample_count = excluded.sample_count,
                    total_records = excluded.total_records,
                    lift = excluded.lift,
                    updated_at = excluded.updated_at
            """, (factor, multiplier, sample_count, total_records, lift, now))
            calculated[factor] = multiplier
        conn.commit()
    return calculated


def load_learning_weights():
    init_auto_weight_tables()
    # 新しい結果が登録されていれば、毎回安全に再集計する。
    recalculate_learning_weights()
    with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
        rows = conn.execute(
            "SELECT factor, multiplier FROM learning_weights"
        ).fetchall()
    weights = {factor: 1.0 for factor in LEARNING_FACTORS}
    weights.update({str(factor): float(multiplier) for factor, multiplier in rows})
    return weights


def load_learning_weight_details():
    init_auto_weight_tables()
    with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT factor, multiplier, sample_count, total_records, lift, updated_at
            FROM learning_weights
            ORDER BY factor
        """).fetchall()
    return [dict(row) for row in rows]


def reset_learning_weights():
    now = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(LEARNING_DB_PATH, timeout=10) as conn:
        conn.execute("""
            UPDATE learning_weights
            SET multiplier = 1.0, sample_count = 0, total_records = 0, lift = 0.0, updated_at = ?
        """, (now,))
        conn.commit()


def apply_learning_adjustment(base_score, breakdown, reasons):
    """項目別の学習倍率を最終スコアへ反映する。"""
    if not AUTO_ADJUST_ENABLED:
        return base_score, 0.0, {}

    adjustment = 0.0
    applied = {}
    for factor in LEARNING_FACTORS:
        value = float(breakdown.get(factor, 0.0) or 0.0)
        multiplier = float(ACTIVE_LEARNING_WEIGHTS.get(factor, 1.0))
        delta = value * (multiplier - 1.0)
        adjustment += delta
        if abs(multiplier - 1.0) >= 0.005 and abs(value) > 0:
            applied[factor] = multiplier

    adjustment = round(adjustment, 2)
    if abs(adjustment) >= 0.05:
        reasons.append(f"過去成績による学習補正 {adjustment:+.2f}")
    return base_score + adjustment, adjustment, applied


init_auto_weight_tables()
AUTO_ADJUST_ENABLED = is_auto_adjust_enabled()
ACTIVE_LEARNING_WEIGHTS = load_learning_weights()

# ==========================================
# 📊 スコア計算ロジック
# ==========================================
calculated_results = []
for item in row_tmp_data:
    num, name, pop, win_odds, idx, wgt, wgh, l3f, sire, has_heavy_record, jock, previous_jockey, trainer, owner, custom_note, sel_track, sel_style, sel_frame, sel_dist_change, score_cell = item
    sex_age, sex, age, body_change = extract_sex_age_and_change(custom_note)
    
    score = 0.0
    final_apt = "C"
    score_breakdown = {
        "指数": 0.0, "斤量": 0.0, "馬体重": 0.0, "格・斤量価値": 0.0,
        "馬番・枠": 0.0, "血統・コース": 0.0, "脚質・距離": 0.0,
        "騎手補正": 0.0, "騎手条件": 0.0, "人気補正": 0.0, "展開補正": 0.0, "道悪補正": 0.0, "馬場バイアス": 0.0, "性齢・馬体増減": 0.0
    }
    evaluation_reasons = []
    learning_adjustment = 0.0
    applied_weights = {}
    j_data = JOCKEY_MASTER.get(jock, JOCKEY_MASTER["その他（自由手入力）"])
    jockey_auto = {"ability": 0.0, "value": 0.0, "ride_status": "不明", "reasons": []}
    
    if name.strip() != "" and jock != "(未選択)":
        j_data = JOCKEY_MASTER.get(jock, JOCKEY_MASTER["その他（自由手入力）"])
        jockey_modifier = 0.0
        
        chosen_conditions = [sel_track, sel_style, sel_frame, sel_dist_change, sel_course]
        for cond in chosen_conditions:
            if cond in j_data.get("factors", {}):
                jockey_modifier += j_data["factors"][cond]
            elif cond and cond.endswith("m") and cond[:-1] in j_data.get("factors", {}):
                jockey_modifier += j_data["factors"][cond[:-1]]
                
        # 特記事項1・2の手入力は廃止。入力済み情報からジョッキー条件を自動判定する。
        jockey_auto = calculate_jockey_auto_conditions(
            jockey=jock, previous_jockey=previous_jockey, trainer=trainer, owner=owner,
            popularity=pop, race_class=race_class, course=sel_course, track=sel_track,
            style=sel_style, frame=sel_frame, distance_change=sel_dist_change,
            sex=sex, body_weight=wgh
        )

        if jockey_modifier < 0 and l3f <= 33.9: jockey_modifier = 0.0  
        final_jockey_rate = j_data["base"] + max(min(jockey_modifier, 0.20), -0.20)
        
        # 🌟 指数ベース補正 (ウマニティ Ｕ指数 基準化スケーリング)
        # Ｕ指数(80〜100等)が入力された場合の倍率調整
        if idx > 70.0:
            scaled_index_score = (idx - 50.0) * 0.8
        else:
            scaled_index_score = idx

        if idx < 45.0:
            mitigated_jockey_rate = 1.0 + (final_jockey_rate - 1.0) * 0.40
        else:
            mitigated_jockey_rate = 1.0 + (final_jockey_rate - 1.0) * 0.70
        
        horse_base_score = scaled_index_score
        score_breakdown["指数"] = round(scaled_index_score, 2)
        if idx > 0:
            evaluation_reasons.append(f"U指数・基礎指数 {idx:.1f}を反映")
        
        # 斤量補正
        weight_diff = 56.0 - wgt
        weight_adjustment = weight_diff * 1.5
        horse_base_score += weight_adjustment
        score_breakdown["斤量"] += weight_adjustment
        if weight_adjustment >= 1.5:
            evaluation_reasons.append(f"軽斤量{wgt:.1f}kgで +{weight_adjustment:.1f}")
        elif weight_adjustment <= -1.5:
            evaluation_reasons.append(f"斤量{wgt:.1f}kgで {weight_adjustment:.1f}")
        
        # 馬体重負担率ロジック & ダート大型馬パワー加点
        if wgh > 0:
            burden_rate = wgt / wgh
            if burden_rate > 0.125:
                if auto_dist == "長距離" or track_condition in ["稍重", "重・不良"]:
                    horse_base_score -= 3.0
                    score_breakdown["馬体重"] -= 3.0
                    evaluation_reasons.append("馬体重に対する斤量負担が大きく -3.0")
                else:
                    horse_base_score -= 1.0
                    score_breakdown["馬体重"] -= 1.0
            elif burden_rate < 0.112:
                horse_base_score += 1.5
                score_breakdown["馬体重"] += 1.5
                evaluation_reasons.append("斤量負担率が良好で +1.5")
                
            # ダート戦大型馬パワーロジック（Ｕ指数との親和性抜群）
            if sel_track == "ダート" and wgh >= 480:
                horse_base_score += 2.0
                score_breakdown["馬体重"] += 2.0
                evaluation_reasons.append("ダートの大型馬パワー条件で +2.0")
                
        # レース格による斤量価値
        is_upper_class_race = race_class in ["G1", "G2/G3", "オープン/L"]
        if is_upper_class_race and wgt >= 57.5:
            horse_base_score += 2.5
            score_breakdown["格・斤量価値"] += 2.5
            evaluation_reasons.append("上級条件で重斤量実績を評価 +2.5")
        elif race_class == "3勝クラス以下" and wgt <= 51.0:
            horse_base_score += 1.0
            score_breakdown["格・斤量価値"] += 1.0
            evaluation_reasons.append("下級条件の軽斤量で +1.0")
        
        # 特注ラッキーゲート馬番
        if str(num).strip() == "7":
            horse_base_score += 2.0
            score_breakdown["馬番・枠"] += 2.0
            evaluation_reasons.append("特注馬番7で +2.0")
        elif str(num).strip() in ["9", "13"]:
            horse_base_score += 1.0
            score_breakdown["馬番・枠"] += 1.0
            evaluation_reasons.append(f"特注馬番{num}で +1.0")
            
        horse_num_int = safe_int_convert(num, 0)
        if horse_num_int % 2 != 0 and str(num).strip() not in ["7", "9", "13"]:
            horse_base_score += 0.5
            score_breakdown["馬番・枠"] += 0.5
        if horse_num_int >= 15:
            horse_base_score -= 1.5
            score_breakdown["馬番・枠"] -= 1.5
            evaluation_reasons.append("大外寄りの馬番で -1.5")
            
        # コース特異的馬番枠補正
        if sel_course == "東京芝1600m":
            if 5 <= horse_num_int <= 12:
                horse_base_score += 2.0
                score_breakdown["馬番・枠"] += 2.0
                evaluation_reasons.append("東京芝1600mの中枠で +2.0")
            elif 13 <= horse_num_int <= 17:
                horse_base_score += 2.5
                score_breakdown["馬番・枠"] += 2.5
                evaluation_reasons.append("東京芝1600mの外寄り枠で +2.5")
            elif 1 <= horse_num_int <= 2:
                horse_base_score -= 2.0
                score_breakdown["馬番・枠"] -= 2.0
                evaluation_reasons.append("東京芝1600mの最内寄りで -2.0")
        elif sel_course and "京都芝" in sel_course:
            if horse_num_int >= 10:
                horse_base_score += 2.0
                score_breakdown["馬番・枠"] += 2.0
                evaluation_reasons.append("京都芝の外寄り馬番で +2.0")
        elif sel_course in ["中京ダート1800m", "東京ダート1600m"]:
            if 1 <= horse_num_int <= 9:
                horse_base_score += 2.0
                score_breakdown["馬番・枠"] += 2.0
                evaluation_reasons.append("ダート対象コースの内～中枠で +2.0")
            elif horse_num_int >= 14:
                horse_base_score -= 2.0
                score_breakdown["馬番・枠"] -= 2.0
                evaluation_reasons.append("ダート対象コースの大外寄りで -2.0")

        # コース事典との連動補正
        if sel_course != "(未選択)":
            # コース事典2に未収録のコースだけ、従来の汎用血統判定を使用する。
            # 収録コースは後段の厳格ルールで判定し、二重加点を防止する。
            if sel_course not in COURSE_LINEAGE_RULES:
                detected_lineages = auto_detect_lineage(sire)
                lineage_matched = any(
                    lineage_matches_course_target(sire, target)
                    for target in good_blood_list
                )
                if lineage_matched:
                    horse_base_score += 5.0
                    score_breakdown["血統・コース"] += 5.0
                    evaluation_reasons.append("コース好相性血統で +5.0")

                if sire and (sire in course_note):
                    horse_base_score += 3.0
                    score_breakdown["血統・コース"] += 3.0
                    evaluation_reasons.append("コース注記に父馬が該当して +3.0")

            fav_style = COURSE_MASTER[sel_course].get("fav_style", "")
            if sel_style in fav_style and sel_style != "選択なし":
                horse_base_score += 3.0
                score_breakdown["脚質・距離"] += 3.0
                evaluation_reasons.append(f"コース有利脚質（{sel_style}）で +3.0")
                
            if "内枠有利" in course_note or "1枠有利" in course_note:
                if sel_frame == "内枠":
                    horse_base_score += 2.0
                    score_breakdown["馬番・枠"] += 2.0
                    evaluation_reasons.append("内枠有利コースで +2.0")
            if "外枠有利" in course_note:
                if sel_frame == "外枠":
                    horse_base_score += 2.0
                    score_breakdown["馬番・枠"] += 2.0
                    evaluation_reasons.append("外枠有利コースで +2.0")
                
            if "距離短縮" in course_note and sel_dist_change == "距離短縮":
                horse_base_score += 3.0
                score_breakdown["脚質・距離"] += 3.0
                evaluation_reasons.append("距離短縮条件に合致して +3.0")
            if "同距離" in course_note and sel_dist_change == "同距離":
                horse_base_score += 3.0
                score_breakdown["脚質・距離"] += 3.0
                evaluation_reasons.append("同距離条件に合致して +3.0")
            if "距離延長" in course_note and sel_dist_change == "距離延長":
                horse_base_score += 3.0
                score_breakdown["脚質・距離"] += 3.0
                evaluation_reasons.append("距離延長条件に合致して +3.0")
                
            if is_upper_class_race:
                if idx >= 65.0 or idx >= 88.0:
                    horse_base_score += 2.0
                    score_breakdown["血統・コース"] += 2.0
                    evaluation_reasons.append("上級条件で指数水準を評価 +2.0")

        if (sel_style in ["逃げ", "先行"]) and (l3f <= 34.5):
            horse_base_score += 3.0
            score_breakdown["脚質・距離"] += 3.0
            evaluation_reasons.append("先行力と前半3Fを評価して +3.0") 
        
        # 性別・年齢・馬体重増減の厳格補正
        sex_body_adjustment, sex_body_reasons = calculate_sex_age_body_adjustment(
            sex, age, body_change, race_month, race_class
        )
        horse_base_score += sex_body_adjustment
        score_breakdown["性齢・馬体増減"] += sex_body_adjustment
        evaluation_reasons.extend(sex_body_reasons)

        # コース事典2.xlsxの厳格血統判定
        # Excel収録コースはこの判定を正本とし、父・性別・馬体重・馬番・脚質・馬場を照合する。
        detailed_lineage_adjustment, detailed_lineage_reasons = calculate_detailed_lineage_adjustment(
            sel_course, sire, sex, wgh, num, sel_style, track_condition
        )
        horse_base_score += detailed_lineage_adjustment
        score_breakdown["血統・コース"] += detailed_lineage_adjustment
        evaluation_reasons.extend(detailed_lineage_reasons)

        # 当日のリアルタイム馬場バイアス
        bias_adjustment, bias_reasons = calculate_track_bias_adjustment(
            track_bias, sel_frame, sel_style
        )
        horse_base_score += bias_adjustment
        score_breakdown["馬場バイアス"] += bias_adjustment
        evaluation_reasons.extend(bias_reasons)

        # 人気は能力スコアから完全に除外。人気補正は妙味スコア専用とする。
        jockey_effect = horse_base_score * (mitigated_jockey_rate - 1.0)
        popularity_effect = 0.0
        score_breakdown["騎手補正"] = round(jockey_effect, 2)
        score_breakdown["人気補正"] = 0.0
        if jockey_effect >= 1.0:
            evaluation_reasons.append(f"騎手適性で +{jockey_effect:.1f}")
        elif jockey_effect <= -1.0:
            evaluation_reasons.append(f"騎手適性で {jockey_effect:.1f}")
        score = horse_base_score * mitigated_jockey_rate

        # 前走騎手・厩舎・馬主など、ジョッキー事典の特記事項を自動反映。
        score += jockey_auto["ability"]
        score_breakdown["騎手条件"] = jockey_auto["ability"]
        evaluation_reasons.extend(jockey_auto["reasons"])
        
        if sel_style in pace_bonus:
            score += pace_bonus[sel_style]
            score_breakdown["展開補正"] += pace_bonus[sel_style]
            if pace_bonus[sel_style] != 0:
                evaluation_reasons.append(f"想定展開と脚質で {pace_bonus[sel_style]:+.1f}")
        
        final_apt = determine_final_aptitude(sire, has_heavy_record)
        if track_condition == "稍重":
            if final_apt == "A":
                score += 2.0
                score_breakdown["道悪補正"] += 2.0
                evaluation_reasons.append("稍重適性Aで +2.0")
            elif final_apt == "D":
                score -= 3.0
                score_breakdown["道悪補正"] -= 3.0
                evaluation_reasons.append("稍重適性Dで -3.0")
        elif track_condition == "重・不良":
            if final_apt == "A":
                score += 5.0
                score_breakdown["道悪補正"] += 5.0
                evaluation_reasons.append("重・不良適性Aで +5.0")
            elif final_apt == "B":
                score += 2.0
                score_breakdown["道悪補正"] += 2.0
                evaluation_reasons.append("重・不良適性Bで +2.0")
            elif final_apt == "C":
                score -= 4.0
                score_breakdown["道悪補正"] -= 4.0
                evaluation_reasons.append("重・不良適性Cで -4.0")
            elif final_apt == "D":
                score -= 10.0
                score_breakdown["道悪補正"] -= 10.0
                evaluation_reasons.append("重・不良適性Dで -10.0")

        # 過去成績から算出した項目別倍率を、既存ロジックの最後に安全に反映する。
        score, learning_adjustment, applied_weights = apply_learning_adjustment(
            score, score_breakdown, evaluation_reasons
        )
            
    # 妙味スコアは能力値とは別軸。人気薄ほど上げるが能力順位には影響させない。
    value_score = (score + max(0, pop - 1) * 0.8 + (jockey_auto["value"] if name.strip() and jock != "(未選択)" else 0.0)) if name.strip() else 0.0

    if name.strip() != "":
        score_cell.write(f"**{score:.2f}**") if score_cell is not None else None
        calculated_results.append({
            "馬番": num, "馬名": name, "能力スコア": score, "妙味スコア": value_score, "最終スコア": score, "人気": pop, "単勝オッズ": win_odds, "斤量": wgt, "馬体重": wgh,
            "父馬": sire,
            "父系統": " / ".join([x for x in auto_detect_lineage(sire) if x != normalize_sire_name(sire)]) or "個別判定",
            "性齢": sex_age, "馬体重増減": body_change, "重道悪適性": final_apt, "騎手": jock,
            "前走騎手": previous_jockey, "継続・乗替": jockey_auto["ride_status"] if jock != "(未選択)" else "不明",
            "厩舎": trainer, "馬主": owner,
            "戦略メモ": j_data.get("note", "") if jock != "(未選択)" else "",
            "評価理由": evaluation_reasons,
            "得点内訳": score_breakdown,
            "学習補正": learning_adjustment if name.strip() and jock != "(未選択)" else 0.0,
            "適用学習倍率": applied_weights if name.strip() and jock != "(未選択)" else {}
        })
    else:
        score_cell.write("") if score_cell is not None else None

# ==========================================
# 🤖 AI総合評価エンジン Ver1.05
# ==========================================
def get_ai_rank(ai_score):
    """0～100点のAI点をランク・星表示へ変換する。"""
    if ai_score >= 97:
        return "S+", "★★★★★"
    if ai_score >= 94:
        return "S", "★★★★★"
    if ai_score >= 90:
        return "A+", "★★★★☆"
    if ai_score >= 85:
        return "A", "★★★★☆"
    if ai_score >= 80:
        return "B+", "★★★☆☆"
    if ai_score >= 75:
        return "B", "★★★☆☆"
    if ai_score >= 70:
        return "C+", "★★☆☆☆"
    if ai_score >= 65:
        return "C", "★★☆☆☆"
    return "D", "★☆☆☆☆"


def add_ai_overall_evaluation(result_df):
    """
    最終スコアをレース内で0～1へ正規化し、AI総合点・ランク・星・信頼度を追加する。

    AI点は勝率そのものではなく、そのレース内での相対的な総合評価。
    全馬が同点に近い場合は過大評価を避け、75点前後へ寄せる。
    """
    df = result_df.copy()
    if df.empty:
        return df

    scores = pd.to_numeric(df["最終スコア"], errors="coerce").fillna(0.0)
    score_min = float(scores.min())
    score_max = float(scores.max())
    score_range = score_max - score_min

    if score_range < 1e-9:
        relative = pd.Series([0.5] * len(df), index=df.index, dtype=float)
    else:
        relative = (scores - score_min) / score_range

    # 最下位55点～最上位95点。極端なS評価は今後の学習機能用に温存する。
    ai_points = (55.0 + relative * 40.0).round(1).clip(0, 100)
    df["AI点"] = ai_points

    rank_and_stars = df["AI点"].apply(get_ai_rank)
    df["AI評価"] = rank_and_stars.apply(lambda value: value[0])
    df["星評価"] = rank_and_stars.apply(lambda value: value[1])

    sorted_scores = scores.sort_values(ascending=False).tolist()
    leader_score = sorted_scores[0] if sorted_scores else 0.0
    second_score = sorted_scores[1] if len(sorted_scores) >= 2 else leader_score
    leader_margin = max(0.0, leader_score - second_score)

    confidences = []
    for raw_score, ai_point in zip(scores, df["AI点"]):
        # 基本信頼度はAI点から算出。首位だけ2位との差を最大5ポイント加味。
        confidence = 45.0 + (float(ai_point) - 55.0) * 0.9
        if raw_score == leader_score:
            confidence += min(5.0, leader_margin * 0.8)
        confidences.append(int(round(max(40.0, min(99.0, confidence)))))

    df["信頼度"] = confidences
    return df

# ==========================================
# 💬 AIコメント自動生成エンジン Ver1.08
# ==========================================
def _format_factor_comment(factor, value):
    """得点内訳の1項目を自然な日本語コメントへ変換する。"""
    value = float(value or 0.0)
    strength_text = {
        "指数": "基礎指数・U指数",
        "斤量": "斤量条件",
        "馬体重": "馬体重と斤量負担率",
        "格・斤量価値": "格と斤量価値",
        "馬番・枠": "馬番・枠順",
        "血統・コース": "血統とコース適性",
        "脚質・距離": "脚質と距離条件",
        "騎手補正": "騎手適性",
        "人気補正": "人気とのバランス",
        "展開補正": "想定展開",
        "道悪補正": "道悪適性",
    }.get(factor, factor)

    if value >= 6:
        return f"{strength_text}が大きな強みで、評価を{value:+.1f}点押し上げています。"
    if value >= 2:
        return f"{strength_text}はプラス材料で、{value:+.1f}点の後押しがあります。"
    if value <= -6:
        return f"{strength_text}は大きな不安材料で、{value:+.1f}点の減点です。"
    if value <= -2:
        return f"{strength_text}には注意が必要で、{value:+.1f}点のマイナスです。"
    return ""


def generate_ai_comment(row):
    """AI評価・得点内訳・学習補正から説明可能な総合コメントを生成する。"""
    horse = str(row.get("馬名", "対象馬"))
    ai_rank = str(row.get("AI評価", "C"))
    ai_score = float(row.get("AI点", 0.0) or 0.0)
    confidence = int(row.get("信頼度", 0) or 0)
    breakdown = row.get("得点内訳", {})
    if not isinstance(breakdown, dict):
        breakdown = {}

    factors = []
    for factor, value in breakdown.items():
        try:
            factors.append((factor, float(value or 0.0)))
        except (TypeError, ValueError):
            continue

    positives = sorted([item for item in factors if item[1] >= 1.5], key=lambda x: x[1], reverse=True)
    negatives = sorted([item for item in factors if item[1] <= -1.5], key=lambda x: x[1])

    if ai_rank in ("S+", "S", "A+"):
        verdict = "勝ち負けまで期待できる有力候補です"
    elif ai_rank in ("A", "B+"):
        verdict = "上位争いを期待できる相手候補です"
    elif ai_rank in ("B", "C+"):
        verdict = "条件がかみ合えば馬券圏内を狙える候補です"
    else:
        verdict = "現状では強調材料が少なく、押さえまでの評価です"

    opening = f"{horse}はAI総合評価{ai_rank}、{ai_score:.1f}点、信頼度{confidence}%で、{verdict}。"

    detail_parts = []
    for factor, value in positives[:3]:
        comment = _format_factor_comment(factor, value)
        if comment:
            detail_parts.append(comment)
    for factor, value in negatives[:2]:
        comment = _format_factor_comment(factor, value)
        if comment:
            detail_parts.append(comment)

    learning_adjustment = float(row.get("学習補正", 0.0) or 0.0)
    if learning_adjustment >= 0.5:
        detail_parts.append(f"過去の学習結果も{learning_adjustment:+.2f}点のプラス補正を示しています。")
    elif learning_adjustment <= -0.5:
        detail_parts.append(f"過去の学習結果では{learning_adjustment:+.2f}点の慎重な補正が入っています。")

    if not detail_parts:
        detail_parts.append("各評価項目の差が小さく、突出した強みと弱みが少ないバランス型の評価です。")

    if negatives:
        closing = "プラス材料はありますが、減点項目も確認したうえで相手関係とオッズを見て判断したいところです。"
    elif ai_rank in ("S+", "S", "A+"):
        closing = "大きな減点が少なく、軸候補として比較的扱いやすい評価です。"
    else:
        closing = "過信は避け、他馬との点差や当日の気配も合わせて判断するのが安全です。"

    return opening + " " + " ".join(detail_parts) + " " + closing


def add_ai_comments(result_df):
    """全出走馬へAIコメントを追加する。"""
    df = result_df.copy()
    if df.empty:
        df["AIコメント"] = []
        return df
    df["AIコメント"] = df.apply(generate_ai_comment, axis=1)
    return df

# ==========================================
# 🧠 Ver1.06 過去予想保存・学習分析エンジン
# ==========================================
DB_PATH = Path(__file__).with_name("keiba_learning.db")


def get_db_connection():
    """SQLite接続を作成する。"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_learning_db():
    """予想履歴・結果テーブルを初期化する。"""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                course TEXT,
                top_horse TEXT NOT NULL,
                ai_score REAL,
                ai_rank TEXT,
                confidence INTEGER,
                final_score REAL,
                budget INTEGER,
                breakdown_json TEXT NOT NULL,
                reasons_json TEXT NOT NULL,
                race_snapshot_json TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS race_results (
                prediction_id TEXT PRIMARY KEY,
                recorded_at TEXT NOT NULL,
                actual_rank INTEGER NOT NULL,
                return_amount INTEGER NOT NULL DEFAULT 0,
                hit_win INTEGER NOT NULL DEFAULT 0,
                hit_place INTEGER NOT NULL DEFAULT 0,
                profit INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(prediction_id) REFERENCES predictions(prediction_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_weights (
                factor TEXT PRIMARY KEY, multiplier REAL NOT NULL DEFAULT 1.0,
                sample_count INTEGER NOT NULL DEFAULT 0, total_records INTEGER NOT NULL DEFAULT 0,
                lift REAL NOT NULL DEFAULT 0.0, updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_settings (
                setting_key TEXT PRIMARY KEY, setting_value TEXT NOT NULL
            )
        """)
        conn.commit()


def save_prediction_record(res_df, course, budget):
    """今回の予想と全出走馬スナップショットをSQLiteへ保存する。"""
    if res_df is None or res_df.empty:
        return None

    top = res_df.iloc[0]
    prediction_id = uuid.uuid4().hex
    snapshot_columns = [
        col for col in [
            "馬番", "馬名", "AI評価", "AI点", "信頼度", "人気", "斤量",
            "馬体重", "馬体重増減", "性齢", "父馬", "父系統", "能力スコア", "妙味スコア", "騎手", "重道悪適性",
            "評価理由", "得点内訳", "学習補正", "適用学習倍率"
        ] if col in res_df.columns
    ]
    snapshot = res_df[snapshot_columns].to_dict(orient="records")

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO predictions (
                prediction_id, created_at, course, top_horse, ai_score,
                ai_rank, confidence, final_score, budget, breakdown_json,
                reasons_json, race_snapshot_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction_id,
            datetime.now().isoformat(timespec="seconds"),
            str(course),
            str(top.get("馬名", "")),
            float(top.get("AI点", 0)),
            str(top.get("AI評価", "")),
            int(top.get("信頼度", 0)),
            float(top.get("最終スコア", 0)),
            int(budget),
            json.dumps(top.get("得点内訳", {}), ensure_ascii=False),
            json.dumps(top.get("評価理由", []), ensure_ascii=False),
            json.dumps(snapshot, ensure_ascii=False, default=str),
        ))
        conn.commit()
    return prediction_id


def save_race_result(prediction_id, actual_rank, return_amount):
    """保存済み予想へ実際の着順と払戻を登録する。"""
    with get_db_connection() as conn:
        prediction = conn.execute(
            "SELECT budget FROM predictions WHERE prediction_id = ?",
            (prediction_id,),
        ).fetchone()
        if prediction is None:
            raise ValueError("対象の予想履歴が見つかりません。")

        budget = int(prediction["budget"] or 0)
        rank = int(actual_rank)
        return_amount = int(return_amount)
        conn.execute("""
            INSERT INTO race_results (
                prediction_id, recorded_at, actual_rank, return_amount,
                hit_win, hit_place, profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(prediction_id) DO UPDATE SET
                recorded_at = excluded.recorded_at,
                actual_rank = excluded.actual_rank,
                return_amount = excluded.return_amount,
                hit_win = excluded.hit_win,
                hit_place = excluded.hit_place,
                profit = excluded.profit
        """, (
            prediction_id,
            datetime.now().isoformat(timespec="seconds"),
            rank,
            return_amount,
            1 if rank == 1 else 0,
            1 if rank <= 3 else 0,
            return_amount - budget,
        ))
        conn.commit()


def load_prediction_history(include_pending=True):
    """予想履歴と結果を読み込む。"""
    where = "" if include_pending else "WHERE r.prediction_id IS NOT NULL"
    with get_db_connection() as conn:
        rows = conn.execute(f"""
            SELECT
                p.prediction_id, p.created_at, p.course, p.top_horse,
                p.ai_score, p.ai_rank, p.confidence, p.final_score,
                p.budget, p.breakdown_json, p.reasons_json,
                r.actual_rank, r.return_amount, r.hit_win, r.hit_place,
                r.profit, r.recorded_at
            FROM predictions p
            LEFT JOIN race_results r ON p.prediction_id = r.prediction_id
            {where}
            ORDER BY p.created_at DESC
        """).fetchall()
    return [dict(row) for row in rows]


def build_factor_learning(history_rows):
    """本命馬の得点内訳と実着順から項目別の成績を集計する。"""
    records = []
    for row in history_rows:
        if row.get("actual_rank") is None:
            continue
        try:
            breakdown = json.loads(row.get("breakdown_json") or "{}")
        except (TypeError, json.JSONDecodeError):
            breakdown = {}

        for factor, value in breakdown.items():
            if factor == "学習補正":
                continue
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue
            records.append({
                "評価項目": factor,
                "加減点": numeric_value,
                "1着": int(row.get("actual_rank") == 1),
                "3着内": int(row.get("actual_rank") <= 3),
            })

    if not records:
        return pd.DataFrame()

    detail = pd.DataFrame(records)
    rows = []
    for factor, group in detail.groupby("評価項目"):
        positive = group[group["加減点"] > 0]
        negative = group[group["加減点"] < 0]
        positive_place = positive["3着内"].mean() * 100 if not positive.empty else 0.0
        overall_place = group["3着内"].mean() * 100
        lift = positive_place - overall_place if not positive.empty else 0.0

        if len(positive) < 5:
            suggestion = "データ不足"
        elif lift >= 10:
            suggestion = "重みを少し強める候補"
        elif lift <= -10:
            suggestion = "重みを弱める候補"
        else:
            suggestion = "現状維持候補"

        rows.append({
            "評価項目": factor,
            "記録数": len(group),
            "プラス評価数": len(positive),
            "プラス時1着率": positive["1着"].mean() * 100 if not positive.empty else 0.0,
            "プラス時3着内率": positive_place,
            "全体3着内率": overall_place,
            "効果差": lift,
            "学習判断": suggestion,
            "マイナス評価数": len(negative),
        })

    return pd.DataFrame(rows).sort_values(["効果差", "プラス評価数"], ascending=[False, False])


init_learning_db()

# ==========================================
# 💾 スマホ専用セーブデータ生成エリア
# ==========================================
st.divider()
st.write("### 💾 スマホ用セーブデータ生成")

mobile_code = encode_for_mobile(current_inputs)
generated_url = f"/?data={mobile_code}"

save_cols = st.columns(2)
with save_cols[0]:
    st.write("▼ 【推奨】コードだけをコピー（メモ帳保存用）")
    if st.button("📋 セーブコードをコピー", use_container_width=True):
        html(f"""<script>
            if (navigator.clipboard) {{
                navigator.clipboard.writeText('{mobile_code}').then(function() {{
                    alert('📥 短いセーブコードをクリップボードにコピーしました！スマホのメモ帳等に貼り付けて保存してください。');
                }}).catch(function(e) {{
                    alert('コピーに失敗しました。下の入力欄から手動で選択してコピーしてください。');
                }});
            }} else {{
                alert('お使いのブラウザは自動コピーに対応していません。下の入力欄からコピーしてください。');
            }}
            </script>""", height=0)
    st.text_area("（手動コピー・確認用）セーブコード全文:", value=mobile_code, height=70, label_visibility="collapsed")

with save_cols[1]:
    st.write("▼ URLパラメータをコピー（復元用）")
    if st.button("🔗 復元パラメータをコピー", use_container_width=True):
        html(f"""<script>
            if (navigator.clipboard) {{
                navigator.clipboard.writeText('{generated_url}').then(function() {{
                    alert('🔗 復元用のURLパラメータ（{generated_url}）をコピーしました！現在のアプリURLの末尾に付け足してお使いください。');
                }}).catch(function(e) {{
                    alert('コピーに失敗しました。手動で選択してください： ' + '{generated_url}');
                }});
            }} else {{
                alert('お使いのブラウザは自動コピーに対応していません。');
            }}
            </script>""", height=0)
    st.caption("※アプリをWebに公開した後は、その公開サイトのURLの直後に `?data=...` を付与することでお気に入りから直接復元できます。")

# ==========================================
# 📈 Ver1.13 単勝オッズ・市場確率統合
# ==========================================
def _softmax_probability(values, temperature=10.0):
    series = pd.to_numeric(values, errors="coerce").fillna(0.0).astype(float)
    if series.empty:
        return series
    temperature = max(float(temperature), 0.1)
    max_value = float(series.max())
    exp_values = series.map(lambda value: math.exp((float(value) - max_value) / temperature))
    total = float(exp_values.sum())
    if total <= 0 or not math.isfinite(total):
        return pd.Series([1.0 / len(series)] * len(series), index=series.index)
    return exp_values / total


def _market_probability(odds_values, smoothing=0.15):
    odds = pd.to_numeric(odds_values, errors="coerce")
    valid = odds.notna() & (odds > 1.0)
    inverse = pd.Series(0.0, index=odds.index, dtype=float)
    inverse.loc[valid] = 1.0 / odds.loc[valid]
    total = float(inverse.sum())
    if total <= 0:
        return None
    probability = inverse / total
    smoothing = min(max(float(smoothing), 0.0), 0.50)
    uniform = 1.0 / len(probability)
    return probability * (1.0 - smoothing) + uniform * smoothing


def add_odds_blended_probability(result_df, ai_weight=0.70, market_weight=0.30, temperature=10.0, smoothing=0.15):
    """能力値と単勝市場を確率化し、的中率重視の統合勝率を作る。"""
    df = result_df.copy()
    ai_prob = _softmax_probability(df["能力スコア"], temperature)
    market_prob = _market_probability(df.get("単勝オッズ", pd.Series(index=df.index, dtype=float)), smoothing)

    if market_prob is None:
        blended = ai_prob
        used_market_weight = 0.0
    else:
        ai_weight = max(float(ai_weight), 0.0)
        market_weight = max(float(market_weight), 0.0)
        total_weight = ai_weight + market_weight
        if total_weight <= 0:
            ai_weight, market_weight, total_weight = 1.0, 0.0, 1.0
        ai_weight /= total_weight
        market_weight /= total_weight
        blended = ai_prob * ai_weight + market_prob * market_weight
        blended = blended / blended.sum()
        used_market_weight = market_weight

    odds = pd.to_numeric(df.get("単勝オッズ"), errors="coerce")
    df["AI勝率"] = (ai_prob * 100.0).round(1)
    df["市場勝率"] = ((market_prob * 100.0).round(1) if market_prob is not None else 0.0)
    df["統合勝率"] = (blended * 100.0).round(1)
    df["期待値指数"] = (blended * odds.where(odds > 1.0, 0.0)).round(2)
    df["オッズ反映率"] = round(used_market_weight * 100.0)
    df["能力順位"] = df["能力スコア"].rank(method="min", ascending=False).astype(int)
    df["妙味判定"] = df["期待値指数"].apply(
        lambda value: "狙い目" if value >= 1.10 else ("適正" if value >= 0.90 else "割高")
    )
    return df.sort_values(["統合勝率", "能力スコア"], ascending=[False, False]).reset_index(drop=True)

# ==========================================
# 🏆 ランキング生成 & 買い目自動生成
# ==========================================
if st.button("🏆 最終予想 ＆ 資金配分AI買い目生成", type="primary", use_container_width=True):
    if calculated_results:
        res_df = pd.DataFrame(calculated_results)
        res_df = res_df[res_df["馬名"] != ""].sort_values(by="能力スコア", ascending=False)
        res_df = add_ai_overall_evaluation(res_df)
        res_df = add_odds_blended_probability(
            res_df,
            ai_weight=ai_weight, market_weight=market_weight,
            temperature=probability_temperature, smoothing=market_smoothing,
        )
        res_df = add_ai_comments(res_df)
        
        if not res_df.empty:
            st.balloons()
            
            symbols = ["◎", "○", "▲", "△", "⭐︎"]
            res_df["印"] = [symbols[idx] if idx < len(symbols) else " " for idx in range(len(res_df))]
            
            top_result = res_df.iloc[0]
            st.header(f"🎯 本命馬: {top_result['印']} {top_result['馬名']} ({top_result['騎手']})")

            eval_cols = st.columns(6)
            eval_cols[0].metric("AI総合評価", top_result["AI評価"])
            eval_cols[1].metric("AI点", f"{top_result['AI点']:.1f}点")
            eval_cols[2].metric("統合勝率", f"{top_result['統合勝率']:.1f}%")
            eval_cols[3].metric("AI勝率", f"{top_result['AI勝率']:.1f}%")
            eval_cols[4].metric("市場勝率", f"{top_result['市場勝率']:.1f}%")
            eval_cols[5].metric("期待値指数", f"{top_result['期待値指数']:.2f}")
            st.caption("※能力スコアは人気・オッズを使いません。本命順位のみAI勝率と市場勝率を統合し、期待値指数は回収率候補の参考として分離表示します。")

            # Ver1.08 AIコメント自動生成
            st.subheader("💬 AI総合コメント")
            st.info(top_result.get("AIコメント", "コメントを生成できませんでした。"))

            # Ver1.05.1 評価理由・得点内訳
            st.subheader("🧠 本命馬の評価理由")
            top_reasons = top_result.get("評価理由", [])
            if isinstance(top_reasons, list) and top_reasons:
                for reason in top_reasons[:8]:
                    st.write(f"✓ {reason}")
            else:
                st.write("評価理由を生成できませんでした。")

            top_breakdown = top_result.get("得点内訳", {})
            if isinstance(top_breakdown, dict) and top_breakdown:
                breakdown_df = pd.DataFrame([
                    {"評価項目": key, "加減点": value}
                    for key, value in top_breakdown.items()
                ])
                breakdown_df = breakdown_df[breakdown_df["加減点"].abs() > 0.001]
                breakdown_df = breakdown_df.sort_values("加減点", ascending=False)
                st.subheader("📊 本命馬の得点内訳")
                st.dataframe(
                    breakdown_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={"加減点": st.column_config.NumberColumn(format="%+.2f点")},
                )

            with st.expander("🐴 全出走馬の評価理由・得点内訳"):
                selected_horse = st.selectbox(
                    "確認する馬",
                    res_df["馬名"].tolist(),
                    key="ai_reason_horse_selector",
                )
                selected_row = res_df[res_df["馬名"] == selected_horse].iloc[0]
                st.markdown("#### 💬 AIコメント")
                st.write(selected_row.get("AIコメント", "コメントを生成できませんでした。"))
                reasons = selected_row.get("評価理由", [])
                for reason in reasons[:10]:
                    st.write(f"✓ {reason}")
                breakdown = selected_row.get("得点内訳", {})
                if isinstance(breakdown, dict):
                    selected_breakdown_df = pd.DataFrame([
                        {"評価項目": key, "加減点": value}
                        for key, value in breakdown.items()
                    ])
                    selected_breakdown_df = selected_breakdown_df[selected_breakdown_df["加減点"].abs() > 0.001]
                    selected_breakdown_df = selected_breakdown_df.sort_values("加減点", ascending=False)
                    st.dataframe(
                        selected_breakdown_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={"加減点": st.column_config.NumberColumn(format="%+.2f点")},
                    )

            st.dataframe(
                res_df[["印", "馬番", "馬名", "能力順位", "AI評価", "AI点", "統合勝率", "AI勝率", "市場勝率", "単勝オッズ", "期待値指数", "妙味判定", "人気", "斤量", "馬体重", "馬体重増減", "性齢", "父馬", "父系統", "能力スコア", "妙味スコア", "騎手", "重道悪適性"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "AI点": st.column_config.NumberColumn(format="%.1f点"),
                    "信頼度": st.column_config.NumberColumn(format="%d%%"),
                    "統合勝率": st.column_config.NumberColumn(format="%.1f%%"),
                    "AI勝率": st.column_config.NumberColumn(format="%.1f%%"),
                    "市場勝率": st.column_config.NumberColumn(format="%.1f%%"),
                    "単勝オッズ": st.column_config.NumberColumn(format="%.1f倍"),
                    "期待値指数": st.column_config.NumberColumn(format="%.2f"),
                    "能力スコア": st.column_config.NumberColumn(format="%.2f"),
                    "妙味スコア": st.column_config.NumberColumn(format="%.2f"),
                },
            )
            
            st.subheader("💰 AI最適化推奨買い目 ＆ 資金配分シミュレーター")
            top_horses = res_df.head(5).to_dict(orient="records")
            
            if len(top_horses) >= 3:
                h_maru = top_horses[0]["馬番"]
                h_fuku = top_horses[1]["馬番"]
                h_ana = top_horses[2]["馬番"]
                h_sa = [h["馬番"] for h in top_horses[3:5]]
                
                pool_maruren = total_budget * 0.40
                pool_sanrenpuku = total_budget * 0.40
                pool_sanrentan = total_budget * 0.20
                
                tickets = []
                maruren_targets = [h_fuku, h_ana] + h_sa
                weights = [0.4, 0.3, 0.15, 0.15]
                for target, w in zip(maruren_targets, weights):
                    amt = max(100, int((pool_maruren * w) // 100) * 100)
                    tickets.append({"券種": "馬連", "買い目": f"{h_maru} ➔ {target}", "推奨投資額": f"{amt}円", "狙い": "軸堅実プラン"})
                    
                sanren_combos = [
                    f"{h_maru} - {h_fuku} - {h_ana}",
                    f"{h_maru} - {h_fuku} - {h_sa[0]}",
                    f"{h_maru} - {h_fuku} - {h_sa[1]}",
                    f"{h_maru} - {h_ana} - {h_sa[0]}",
                    f"{h_maru} - {h_ana} - {h_sa[1]}",
                ]
                each_sanren = max(100, int((pool_sanrenpuku / len(sanren_combos)) // 100) * 100)
                for combo in sanren_combos:
                    tickets.append({"券種": "3連複", "買い目": combo, "推奨投資額": f"{each_sanren}円", "狙い": "高回収リターン"})
                    
                tickets.append({"券種": "3連単", "買い目": f"{h_maru} ➔ {h_fuku} ➔ {h_ana}", "推奨投資額": f"{int((pool_sanrentan * 0.6) // 100) * 100}円", "狙い": "一撃必殺・本線"})
                tickets.append({"券種": "3連単", "買い目": f"{h_maru} ➔ {h_fuku} ➔ {h_sa[0]}", "推奨投資額": f"{int((pool_sanrentan * 0.4) // 100) * 100}円", "狙い": "一撃必殺・押さえ"})
                
                st.dataframe(pd.DataFrame(tickets), use_container_width=True, hide_index=True)
                
                st.session_state["last_predict_horse"] = top_horses[0]["馬名"]
                st.session_state["last_predict_course"] = sel_course

                prediction_id = save_prediction_record(res_df, sel_course, total_budget)
                st.session_state["last_prediction_id"] = prediction_id
                st.success("🧠 今回の予想を学習データベースへ保存しました。レース後に下の結果入力欄から着順を登録してください。")
    else:
        st.error("出馬表データが入力されていません。")

# ==========================================
# 📊 5. 過去予想の保存・結果登録・学習分析
# ==========================================
st.divider()
st.header("🧠 過去予想の保存・結果登録・学習分析")
st.caption("予想時点のAI点・評価理由・得点内訳をSQLiteへ保存し、レース結果から各評価項目の有効性を集計します。")

all_history = load_prediction_history(include_pending=True)
pending_history = [row for row in all_history if row.get("actual_rank") is None]
completed_history = [row for row in all_history if row.get("actual_rank") is not None]

with st.expander("📝 保存済み予想へレース結果を登録する", expanded=bool(pending_history)):
    if pending_history:
        option_map = {
            f"{row['created_at']}｜{row['course']}｜本命 {row['top_horse']}｜AI {row['ai_rank']} {row['ai_score']:.1f}点": row["prediction_id"]
            for row in pending_history
        }
        selected_label = st.selectbox("結果を登録する予想", list(option_map.keys()))
        result_cols = st.columns(2)
        with result_cols[0]:
            actual_rank = st.number_input("本命馬の実際の着順", min_value=1, max_value=18, value=1, step=1)
        with result_cols[1]:
            return_amount = st.number_input("このレースの払戻金額（円）", min_value=0, max_value=10000000, value=0, step=100)

        if st.button("💾 レース結果を保存して学習へ反映", type="primary"):
            try:
                save_race_result(option_map[selected_label], actual_rank, return_amount)
                st.success("結果を保存しました。学習集計へ反映されます。")
                st.rerun()
            except (ValueError, sqlite3.Error) as exc:
                st.error(f"結果を保存できませんでした: {exc}")
    else:
        st.info("結果未登録の予想はありません。新しい予想を実行すると、ここに表示されます。")

if completed_history:
    history_df = pd.DataFrame(completed_history)
    history_df["予想日時"] = history_df["created_at"]
    history_df["コース"] = history_df["course"]
    history_df["本命馬"] = history_df["top_horse"]
    history_df["AI評価"] = history_df["ai_rank"]
    history_df["AI点"] = history_df["ai_score"]
    history_df["着順"] = history_df["actual_rank"].astype(int)
    history_df["投資額"] = history_df["budget"].astype(int)
    history_df["回収額"] = history_df["return_amount"].fillna(0).astype(int)
    history_df["収支"] = history_df["profit"].fillna(0).astype(int)
    history_df["1着的中"] = history_df["hit_win"].fillna(0).astype(int).map({1: "○", 0: "－"})
    history_df["3着内"] = history_df["hit_place"].fillna(0).astype(int).map({1: "○", 0: "－"})

    total_races = len(history_df)
    win_rate = (history_df["着順"] == 1).mean() * 100
    place_rate = (history_df["着順"] <= 3).mean() * 100
    total_invest = history_df["投資額"].sum()
    total_return = history_df["回収額"].sum()
    recovery_rate = total_return / total_invest * 100 if total_invest else 0.0

    metric_cols = st.columns(5)
    metric_cols[0].metric("学習済みレース", f"{total_races}件")
    metric_cols[1].metric("本命1着率", f"{win_rate:.1f}%")
    metric_cols[2].metric("本命3着内率", f"{place_rate:.1f}%")
    metric_cols[3].metric("累計回収率", f"{recovery_rate:.1f}%")
    metric_cols[4].metric("累計収支", f"{int(total_return-total_invest):,}円")

    with st.expander("📚 過去の予想・結果一覧"):
        st.dataframe(
            history_df[[
                "予想日時", "コース", "本命馬", "AI評価", "AI点", "着順",
                "1着的中", "3着内", "投資額", "回収額", "収支"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "AI点": st.column_config.NumberColumn(format="%.1f点"),
                "投資額": st.column_config.NumberColumn(format="%d円"),
                "回収額": st.column_config.NumberColumn(format="%d円"),
                "収支": st.column_config.NumberColumn(format="%+d円"),
            },
        )

    st.subheader("🔬 評価項目別の学習結果")
    factor_df = build_factor_learning(completed_history)
    if factor_df.empty:
        st.info("評価項目別のデータをまだ集計できません。")
    else:
        st.dataframe(
            factor_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "プラス時1着率": st.column_config.NumberColumn(format="%.1f%%"),
                "プラス時3着内率": st.column_config.NumberColumn(format="%.1f%%"),
                "全体3着内率": st.column_config.NumberColumn(format="%.1f%%"),
                "効果差": st.column_config.NumberColumn(format="%+.1fポイント"),
            },
        )
        st.caption("効果差は、その項目がプラス評価だった場合の3着内率と、同項目の全記録における3着内率との差です。5件未満はデータ不足として扱います。")

    csv_data = history_df[[
        "予想日時", "コース", "本命馬", "AI評価", "AI点", "着順",
        "投資額", "回収額", "収支"
    ]].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 学習履歴をCSVで保存",
        data=csv_data,
        file_name="keiba_learning_history.csv",
        mime="text/csv",
    )
else:
    st.info("まだ結果登録済みのレースがありません。予想を実行し、レース後に着順を登録すると学習が始まります。")

st.divider()
st.subheader("⚙️ 配点の自動調整設定")
st.caption(
    "結果登録済み履歴から項目別の3着内効果を計算し、元の加減点へ0.85～1.15倍の範囲で反映します。"
    "プラス評価10件・全記録15件未満の項目は1.00倍のままです。"
)

current_auto_enabled = is_auto_adjust_enabled()
selected_auto_enabled = st.toggle(
    "学習結果を次回予想の配点へ自動反映する",
    value=current_auto_enabled,
    help="オフにすると履歴と分析結果は残したまま、予想スコアへの反映だけ停止します。",
)
if selected_auto_enabled != current_auto_enabled:
    set_auto_adjust_enabled(selected_auto_enabled)
    st.success("自動調整設定を更新しました。")
    st.rerun()

control_cols = st.columns(2)
with control_cols[0]:
    if st.button("🔄 学習倍率を再計算", use_container_width=True):
        recalculate_learning_weights()
        st.success("最新の結果から学習倍率を再計算しました。")
        st.rerun()
with control_cols[1]:
    if st.button("↩️ 学習倍率を1.00へ戻す", use_container_width=True):
        reset_learning_weights()
        st.success("全項目の倍率を1.00へ戻しました。履歴データは削除していません。")
        st.rerun()

weight_details = load_learning_weight_details()
if weight_details:
    weight_df = pd.DataFrame(weight_details).rename(columns={
        "factor": "評価項目",
        "multiplier": "現在倍率",
        "sample_count": "プラス評価数",
        "total_records": "全記録数",
        "lift": "効果差",
        "updated_at": "更新日時",
    })
    weight_df["配点変化"] = (weight_df["現在倍率"] - 1.0) * 100
    st.dataframe(
        weight_df[["評価項目", "現在倍率", "配点変化", "プラス評価数", "全記録数", "効果差", "更新日時"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "現在倍率": st.column_config.NumberColumn(format="%.3f倍"),
            "配点変化": st.column_config.NumberColumn(format="%+.1f%%"),
            "効果差": st.column_config.NumberColumn(format="%+.1fポイント"),
        },
    )

if is_auto_adjust_enabled():
    active_count = sum(
        1 for row in weight_details if abs(float(row.get("multiplier", 1.0)) - 1.0) >= 0.005
    )
    if active_count:
        st.success(f"自動調整は有効です。現在 {active_count} 項目の学習倍率を予想へ反映しています。")
    else:
        st.info("自動調整は有効ですが、必要件数に達した項目がまだないため、現在の倍率はすべて1.00です。")
else:
    st.warning("自動調整は停止中です。履歴の保存と学習分析は継続されます。")

st.info(
    "安全設計：倍率は0.85～1.15に制限し、既存ロジックを直接書き換えません。"
    "各馬の基本スコア計算後に差分だけを加えるため、設定をオフにすれば元の予想へ戻せます。"
)
