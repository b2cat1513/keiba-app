import streamlit as st
import pandas as pd
import json
import urllib.parse
import base64
from streamlit.components.v1 import html

# ==========================================
# ⚙️ アプリ初期設定 & レイアウト
# ==========================================
st.set_page_config(page_title="ジェニーAI予想ver1.03", layout="wide")
st.title("🏆 ジェニーAI予想ver1.03 (スマホ特化・斤量馬体重＆レース格ロジック完全統合版)")

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
    
    # URL丸ごと貼り付けられた場合の救済
    if "data=" in encoded_str:
        encoded_str = encoded_str.split("data=")[-1].split("&")[0]
        
    # スマホのコピペミスで末尾のパディング（=）が消えた場合の自動補正
    missing_padding = len(encoded_str) % 4
    if missing_padding:
        encoded_str += '=' * (4 - missing_padding)
        
    try:
        b_data = base64.b64decode(encoded_str)
        json_str = b_data.decode('utf-8')
        return json.loads(json_str)
    except Exception:
        # 従来のURLエンコード形式（ver1.00仕様）だった場合の互換性ケア
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

# 初回起動時にURLパラメータに「data」があればロード
query_params = st.query_params
if "data" in query_params and not st.session_state["loaded_data"]:
    parsed = decode_for_mobile(query_params["data"])
    if parsed:
        st.session_state["loaded_data"] = parsed
        st.toast("📥 過去の入力データをURLから正常にロードしました！")

if "history_log" not in st.session_state:
    st.session_state["history_log"] = []

# ==========================================
# 🧩 サイドバー：スマホ専用かんたんロード（安全網）
# ==========================================
with st.sidebar:
    st.header("⚙️ システム復元メニュー")
    with st.expander("🔄 スマホ専用ワンタップ復元", expanded=True):
        st.write("保存したセーブデータコード（またはURL）をスマホのクリップボードに**コピーした状態**で、下のボタンを押してください。")
        
        # スマホの長押し貼り付けをスキップするJavaScriptボタン
        html("""
        <script>
        function doLoad() {
            navigator.clipboard.readText().then(text => {
                const inputs = window.parent.document.getElementsByTagName('input');
                for (let i = 0; i < inputs.length; i++) {
                    if (inputs[i].getAttribute('aria-label') === 'hidden_mobile_paste') {
                        inputs[i].value = text;
                        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                        break;
                    }
                }
            }).catch(err => {
                alert('ブラウザのセキュリティ設定により自動取得が制限されました。下の手動欄をお使いください。');
            });
        }
        </script>
        """, height=0)
        
        # 隠しテキスト入力（JSからのデータ受け取り用）
        hidden_paste = st.text_input("hidden_mobile_paste", label_visibility="collapsed", key="mobile_bridge", placeholder="手動貼り付け用スペース（予備）")
        
        if st.button("📋 クリップボードから1発ロード", type="primary", use_container_width=True):
            if hidden_paste:
                parsed_data = decode_for_mobile(hidden_paste)
                if parsed_data:
                    st.session_state["loaded_data"] = parsed_data
                    st.success("📥 データを正常に復元しました！")
                    st.rerun()
            else:
                html("<script>doLoad();</script>", height=0)
                st.info("再度ボタンを押すと、クリップボードから読み込まれたデータが反映されます。")

# ==========================================
# 🏇 1. ジョッキー事典マスターデータ
# ==========================================
JOCKEY_MASTER = {
    "C.ルメール": {
        "base": 1.30,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "短距離": -0.05, "長距離": 0.05, "東京芝1600": 0.15, "東京芝2000": 0.15, "東京芝2400": 0.15, "京都芝1600": 0.15, "京都芝2400": 0.15, "中山芝2500": -0.10},
        "note": "東京・京都外回り・長距離◎。芝2400以上◯、中山より東京◯、重賞8枠◯、芝道悪✕"
    },
    "川田将雅": {
        "base": 1.30,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "短距離": 0.05, "芝1枠": 0.15, "小回り": 0.15, "交流重賞": 0.15, "長距離": -0.05, "阪神芝2000": 0.15, "中京ダ1800": 0.15, "中山芝2000": 0.15, "ローカル芝": -0.05},
        "note": "確勝級での信頼度抜群。芝1枠◯、小回り2000◯、交流重賞◎、長距離✕"
    },
    "戸崎圭太": {
        "base": 1.25,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.10, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "長距離": -0.05, "前走ルメール": 0.10, "東京芝1600": 0.15, "東京ダ1600": 0.15, "中山ダ1800": 0.10, "重賞": 0.10},
        "note": "東京マイル・ダート外枠◯。前走ルメール◎、馬群✕、東京2500◯、東京中山1600重賞◯"
    },
    "坂井瑠星": {
        "base": 1.25,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.10, "差し": -0.05, "内枠": 0.05, "外枠": -0.05, "短距離": 0.05, "ダート重賞": 0.15, "東京ダ1600": 0.15, "中京ダ1800": 0.15},
        "note": "逃げ先行・大舞台での積極策。内枠◎、ダート重賞◎、欧州血統◎、前走古川奈◯"
    },
    "横山武史": {
        "base": 1.25,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "外枠": -0.05, "短距離": 0.05, "長距離": -0.05, "中山芝2000": 0.15, "中山芝2500": 0.15, "持久力戦": 0.15, "東京芝2400": 0.10},
        "note": "関東のエース。内枠◎、中山重賞◯、ダート◯、ビックレッドＦ◯、マイネル・ウイン◯"
    },
    "松山弘平": {
        "base": 1.15,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "外枠": -0.05, "短距離": 0.05, "ダート": 0.15, "新馬戦": 0.15, "前哨戦": 0.15, "中山ダ1800": 0.15, "京都ダ1800": 0.15},
        "note": "非常に堅実でダート◎。新馬戦&前哨戦◎、マイル以下の重賞◯、堀厩舎◯"
    },
    "武豊": {
        "base": 1.20,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.05, "差し": 0.05, "内枠": -0.05, "外枠": -0.05, "短距離": -0.05, "長距離": 0.05, "継続騎乗": 0.15, "人気薄": 0.15, "距離延長": 0.15, "京都芝2000": 0.15, "京都芝2200": 0.15, "東京芝2400": 0.15},
        "note": "大舞台のレジェンド。距離延長◎、逃げ&追い込み◯、ダートの上級条件◯"
    },
    "岩田望来": {
        "base": 1.10,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": -0.05, "差し": 0.05, "内枠": 0.05, "外枠": -0.05, "短距離": -0.05, "長距離": 0.05, "マイル以下の差し": 0.15, "乗り替わり": 0.15, "中京芝1600": 0.10, "阪神芝1600": 0.10},
        "note": "平場・特別戦の安定感。マイル以下の差し◯、乗り替わり◎、スロー逃げ◯、父からの乗り替わり◯"
    },
    "西村淳也": {
        "base": 1.10,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "外枠": -0.05, "短距離": 0.05, "長距離": -0.05, "京都芝": 0.15, "京都芝1600": 0.15, "阪神芝1400": 0.15},
        "note": "度胸と勝負強さあり。京都芝◯、ロードカナロア産駒◯、スタートセンス◯"
    },
    "団野大成": {
        "base": 1.10,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.05, "差し": 0.05, "内枠": -0.05, "外枠": -0.05, "短距離": 0.05, "短距離重賞": 0.15, "荒れ馬場": 0.15, "京都芝1200": 0.15, "阪神芝1600": 0.10},
        "note": "思い切りの良さが魅力。短距離重賞◯、芝の荒れ馬場◯、斉藤崇厩舎◯"
    },
    "菅原明良": {
        "base": 1.15,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": 0.05, "内枠": 0.05, "短距離": -0.05, "長距離": 0.05, "東京芝1600": 0.10, "新潟直線1000": 0.15},
        "note": "信頼度急上昇の若手。中長距離戦◯、上級条件の差し馬◯、関西遠征◎"
    },
    "鮫島克駿": {
        "base": 1.10,
        "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": 0.05, "外枠": -0.05, "長距離": 0.05, "イン突き": 0.15, "中長距離": 0.15, "ダート外枠": 0.15, "中京芝2000": 0.10},
        "note": "ロスを抑える立ち回り。中長距離◯、差し馬◯、ダートは外枠◯"
    },
    "斎藤新": {
        "base": 1.05,
        "factors": {"芝": 0.05, "先行": 0.05, "差し": 0.05, "外枠": 0.05, "短距離": -0.05, "長距離": -0.05},
        "special_factors": {"外枠◎": 0.10, "逃げ◎": 0.10, "芝特別戦◯": 0.05},
        "note": "外枠◎、逃げ◎、芝特別戦◯"
    },
    "佐々木大輔": {
        "base": 1.15,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.05, "内枠": 0.05, "短距離": 0.05, "長距離": -0.05, "ローカル芝": 0.15, "中山芝1200": 0.10},
        "note": "北海道・ローカル開催の鬼。芝内枠◯、短距離◯、ダート◯"
    },
    "吉村誠之助": {
        "base": 1.00,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "短距離": 0.05, "ローカルダート": 0.10},
        "note": "期待のルーキー。差し◯、大型馬◯、上級条件◎"
    },
    "高杉吏麒": {
        "base": 1.05,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": 0.05, "差し": 0.05, "内枠": 0.05, "外枠": 0.05, "短距離": 0.05, "長距離": -0.05, "減量活かした先行": 0.15, "ローカル芝": 0.10, "ローカルダート": 0.10},
        "note": "急成長中の積極策。スタート◎、ダート内枠◎、芝中距離以上◯"
    },
    "田口貫太": {
        "base": 1.05,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "短距離": 0.05, "ローカルダート": 0.15, "芝1枠": 0.15, "中京芝1200": 0.10},
        "note": "減量を活かしたイン戦得意。ダートの人気馬◯、重賞△、芝1枠◯"
    },
    "菊沢一樹": {
        "base": 1.00,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": -0.05, "差し": 0.05, "内枠": 0.05, "外枠": -0.05, "短距離": 0.05, "長距離": -0.05},
        "special_factors": {"差し◎": 0.10, "直線競馬◎": 0.10, "特別戦◯": 0.05},
        "note": "差し◎、直線競馬◎、特別戦◯"
    },
    "荻野極": {
        "base": 1.00,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": -0.05, "内枠": 0.05, "短距離": -0.05},
        "special_factors": {"芝内枠◯": 0.05, "大型馬◯": 0.05, "ノースヒルズ系◯": 0.05, "鹿戸厩舎◯": 0.05},
        "note": "芝内枠◯、大型馬◯、ノースヒルズ系◯、鹿戸厩舎◯"
    },
    "横山典弘": {
        "base": 1.15,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": 0.05, "内枠": 0.05, "外枠": -0.05, "短距離": -0.05, "長距離": 0.05, "芝内枠": 0.15, "継続騎乗": 0.15, "東京芝2400": 0.10},
        "note": "独自の「馬ファースト」一発。重賞◎、芝内枠◎、継続騎乗◯"
    },
    "岩田康誠": {
        "base": 1.15,
        "factors": {"芝": 0.05, "ダート": 0.05, "先行": -0.05, "差し": 0.05, "内枠": 0.15, "外枠": -0.05, "長距離": 0.05, "重賞": 0.15, "阪神芝2000": 0.15},
        "note": "ベテランの強烈イン突き。重賞◎、継続騎乗◯"
    },
    "北村友一": {
        "base": 1.10,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": -0.05, "差し": 0.05, "外枠": 0.05, "短距離": -0.05, "長距離": 0.05},
        "special_factors": {"芝8枠◯": 0.05, "差し馬◯": 0.05, "中長距離戦◎": 0.10},
        "note": "芝8枠◯、差し馬◯、中長距離戦◎"
    },
    "田辺裕信": {
        "base": 1.10,
        "factors": {"芝": 0.05, "先行": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "長距離": 0.05, "長距離戦": 0.15, "逃げ": 0.10, "東京ダ1400": 0.10},
        "note": "大胆な奇策や大胆逃げ。長距離戦◎、開催後半芝◯、短距離重賞△"
    },
    "横山和生": {
        "base": 1.10,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "短距離": -0.05, "長距離": 0.05, "東京芝2400": 0.10, "中山芝2500": 0.10, "ダート重賞": 0.15},
        "note": "長距離先行・ダート重賞巧者。ダート重賞◯、小回り◯、長距離戦◯"
    },
    "J.モレイラ": {
        "base": 1.30,
        "factors": {"芝": 0.05, "ダート": 0.10, "先行": 0.05, "差し": 0.05, "内枠": 0.05, "外枠": 0.05, "短距離": 0.05, "長距離": 0.05, "中長距離": 0.15, "東京芝2400": 0.15, "阪神芝1600": 0.10},
        "note": "異次元のマジックマン。中長距離◎、ダート外枠◎、妙味◎"
    },
    "D.レーン": {
        "base": 1.25,
        "factors": {"芝": 0.10, "ダート": -0.05, "先行": 0.05, "差し": 0.05, "内枠": 0.05, "外枠": -0.05, "短距離": -0.05, "長距離": 0.05, "重賞": 0.15, "東京芝2400": 0.10, "東京芝1600": 0.15},
        "note": "G1大舞台での絶大な信頼。重賞◎、芝中長距離◯、新馬戦◯、欧州血統◯"
    },
    "R.キング": {
        "base": 1.15,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.15, "差し": 0.05, "内枠": 0.10, "外枠": 0.05, "短距離": 0.05, "長距離": 0.05, "東京芝1600": 0.10},
        "note": "抜群のスタートから前残り。スタート◎、妙味◎、特別戦◎"
    },
    "丹内祐次": {
        "base": 1.10,
        "factors": {"芝": 0.05, "ダート": -0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "短距離": -0.05, "長距離": 0.05, "ローカル芝": 0.15, "ローカルダート": 0.15},
        "note": "ローカルの帝王。ローカル芝◯、荒馬場◎"
    },
    "浜中俊": {
        "base": 1.10,
        "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "差し": -0.05, "内枠": -0.05, "外枠": -0.05, "短距離": 0.05},
        "special_factors": {"芝短〜中距離◯": 0.05, "1番人気◎": 0.10, "伸びしろ△": -0.05},
        "note": "芝短〜中距離◯、1番人気◎、伸びしろ△"
    },
    "藤岡佑介": {
        "base": 1.10,
        "factors": {"芝": -0.05, "ダート": -0.05, "先行": -0.05, "差し": 0.05, "短距離": -0.05, "長距離": -0.05, "自在性": 0.15, "重賞の人気馬": -0.15},
        "note": "優れた展開読み。自在性◎、重賞の人気馬✕、妙味◎、勝負強さ△"
    },
    "津村明秀": {
        "base": 1.05,
        "factors": {"芝": -0.05, "ダート": -0.05, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "短距離": -0.05, "長距離": -0.05, "新潟直線1000": 0.15, "東京芝1600": 0.10, "京都芝1600": 0.10},
        "note": "本格化したマイル勝負強さ。直線競馬◎、小回り◎、差し馬マクリ◯"
    },
    "三浦皇成": {
        "base": 1.05,
        "factors": {"ダート": 0.05, "先行": -0.05, "内枠": -0.05, "外枠": -0.05, "短距離": -0.05, "1番人気": 0.15, "重賞": -0.15, "東京ダ1600": 0.10},
        "note": "平場・条件戦の1番人気堅実。1番人気◎、下級条件◯、重賞✕"
    },
    "大野拓弥": {
        "base": 1.05,
        "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "外枠": 0.05, "短距離": -0.05, "長距離": -0.05, "東京ダ1600": 0.15, "追い込み": 0.15, "中山芝1200": 0.10},
        "note": "外枠追い込みでの穴激走。ダートの外枠◯、差し追込◯、人気馬◎"
    },
    "石川裕紀人": {
        "base": 1.10,
        "factors": {"芝": -0.05, "ダート": -0.05, "先行": 0.05, "内枠": 0.05, "短距離": -0.05, "芝1枠": 0.15, "積極策": 0.10, "東京芝2000": 0.10},
        "note": "思い切った先行イン突き。小回り◎、マイネル系◎、芝1枠◯"
    },
    "菱田裕二": {
        "base": 1.05,
        "factors": {"芝": -0.05, "ダート": 0.05, "先行": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": -0.05, "長距離": 0.05},
        "special_factors": {"差し馬&マクリ◯": 0.05, "石坂厩舎◎": 0.10, "荒れ馬場◎": 0.10},
        "note": "差し馬&マクリ◯、石坂厩舎◎、荒れ馬場◎"
    },
    "池添謙一": {
        "base": 1.15,
        "factors": {"芝": 0.05, "先行": -0.05, "差し": 0.05, "外枠": 0.05, "短距離": -0.05, "長距離": 0.05, "大舞台＆重賞": 0.15, "差し＆追い込み": 0.15, "中山芝2500": 0.15},
        "note": "グランプリなど大舞台無類の強さ。芝中長距離◯、差し追い込み◯、重賞◎"
    },
    "幸英明": {
        "base": 1.05,
        "factors": {"芝": -0.05, "ダート": 0.15, "先行": 0.05, "差し": -0.05, "内枠": 0.05, "外枠": -0.05, "短距離": 0.05, "牡馬のタフ条件": 0.15, "阪神ダ1800": 0.10},
        "note": "タフなダート消耗戦◎。ダート重賞◯、非根幹距離◯、タフな馬場◎"
    },
    "M.デムーロ": {
        "base": 1.15,
        "factors": {"芝": -0.05, "先行": -0.05, "差し": -0.05, "外枠": 0.05, "短距離": -0.05, "大舞台＆重賞": 0.15, "追い込み": 0.15, "東京芝2000": 0.10},
        "note": "大舞台の豪快マクリ。芝8枠◎、急坂コース◎、芝2200◯、中山重賞◯"
    },
    "小沢大仁": {"base": 1.00, "factors": {"小倉芝中長距離": 0.05}, "note": "小倉芝中長距離◯"},
    "横山流人": {"base": 1.00, "factors": {}, "note": "人薄◯、注目◯"},
    "小林美駒": {"base": 1.00, "factors": {"逃げ": 0.05, "先行": 0.05, "短距離": 0.05}, "note": "乗替◯、逃げ先行◯、短距離◯"},
    "丸山元気": {"base": 1.00, "factors": {}, "special_factors": {"東京✕": -0.05, "中山◯": 0.05}, "note": "東京✕、中山◯"},
    "古川吉洋": {"base": 1.00, "factors": {"短距離": 0.05, "差し": 0.05}, "special_factors": {"おかわり穴◯": 0.05}, "note": "継騎◯、人薄◯、短距離の差し◯、おかわり穴◯"},
    "原優介": {"base": 1.05, "factors": {"ダート": 0.10, "逃げ": 0.05, "追い込み": 0.05}, "note": "人薄◯、ダート◎、逃げ&追い込み◯"},
    "西塚洸二": {"base": 1.00, "factors": {}, "special_factors": {"藤原英厩舎◎": 0.10}, "note": "藤原英厩舎◎"},
    "木幡巧也": {"base": 1.00, "factors": {"ダート": 0.10}, "note": "人薄◯、ダート◎"},
    "石橋脩": {"base": 1.05, "factors": {"先行": 0.10, "中山芝1600": 0.10}, "special_factors": {"逃げ追い込み◯": 0.05, "重賞の穴◯": 0.05}, "note": "タフな中山先行◯。逃げ追い込み◯、重賞の穴◯"},
    "松本大輝": {"base": 1.00, "factors": {"芝": 0.05, "長距離": 0.05, "差し": 0.05}, "note": "差し◯、芝中長距離◯"},
    "武藤雅": {"base": 1.00, "factors": {}, "special_factors": {"人気馬✕": -0.05, "武藤厩舎◯": 0.05}, "note": "人気馬✕、武藤厩舎◯"},
    "北村宏司": {"base": 1.05, "factors": {"東京芝1600": 0.10, "内枠": 0.10, "東京芝2400": 0.10}, "note": "ベテランのイン立ち回り。芝内枠◯、上級条件◯、前走ルメール◯"},
    "和田竜二": {"base": 1.05, "factors": {"荒れ馬場": 0.15, "先行": 0.05, "京都ダ1800": 0.10}, "note": "追えるベテラン。マイネルウイン◯、ダート◯、小回り◯"},
    "吉田豊": {"base": 1.00, "factors": {}, "special_factors": {"逃げ追い込み◯": 0.05, "竹内厩舎◯": 0.05}, "note": "東の仕事人。逃げ追い込み◯、竹内厩舎◯"},
    "丸田恭介": {"base": 1.00, "factors": {"差し": 0.05, "追い込み": 0.05}, "note": "差し追い込み◯"},
    "内田博幸": {"base": 1.05, "factors": {"ダート": 0.05}, "note": "パワフルな追い。ダート＆牡馬◯"},
    "国分恭介": {"base": 1.00, "factors": {"差し": 0.05, "追い込み": 0.05}, "special_factors": {"牧浦厩舎◯": 0.05}, "note": "差し追い込み◯、牧浦厩舎◯"},
    "杉原誠人": {"base": 1.00, "factors": {}, "special_factors": {"直線競馬◯": 0.05}, "note": "直線競馬◯"},
    "今村聖奈": {"base": 1.00, "factors": {"外枠": 0.05, "長距離": 0.05}, "note": "外枠◯、中長距離◯"},
    "松岡正海": {"base": 1.00, "factors": {}, "special_factors": {"ウイン◯": 0.05}, "note": "マイネル・ウイン系主力"},
    "小崎綾也": {"base": 1.00, "factors": {}, "note": "リスト外騎手"},
    "松若風馬": {"base": 1.05, "factors": {"逃げ": 0.15, "ダート": 0.05, "短距離": 0.05}, "note": "積極果敢な逃げ。大型ダート馬◯、短距離◯"},
    "酒井学": {"base": 1.00, "factors": {}, "special_factors": {"牝馬◯": 0.05, "ハンデ戦◯": 0.05}, "note": "牝馬◯、ハンデ戦◯"},
    "吉田隼人": {"base": 1.10, "factors": {"内枠": 0.05, "差し": 0.05}, "note": "好位差し◯、内枠◯"},
    "藤懸貴志": {"base": 1.00, "factors": {}, "special_factors": {"ハンデ戦◯": 0.05}, "note": "ハンデ戦◯"},
    "富田暁": {"base": 1.00, "factors": {}, "special_factors": {"武英厩舎◯": 0.05}, "note": "武英厩舎◯"},
    "川又賢治": {"base": 1.00, "factors": {}, "special_factors": {"荒馬場◯": 0.05}, "note": "荒馬場◯"},
    "柴田大知": {"base": 1.00, "factors": {"長距離": 0.05}, "note": "芝中長距離◯"},
    "柴田善臣": {"base": 1.00, "factors": {"人気薄": 0.10}, "special_factors": {"ダート外枠差し◯": 0.05}, "note": "最年長レジェンド。ダート外枠差し◯"},
    "A.シュタルケ": {"base": 1.05, "factors": {"長距離": 0.05}, "special_factors": {"馬群◯": 0.05}, "note": "中長距離◯、馬群◯"},
    "T.マーカンド": {"base": 1.20, "factors": {"ダート": 0.15, "荒れ馬場": 0.10, "中山ダ1800": 0.15}, "note": "剛腕。大型馬◯"},
    "H.ドイル": {"base": 1.15, "factors": {"先行": 0.10, "芝": 0.05}, "special_factors": {"東京より中山◯": 0.05, "1200M戦◎": 0.10}, "note": "東京より中山◯、1200M戦◎"},
    "C.デムーロ": {"base": 1.25, "factors": {}, "special_factors": {"外枠◎": 0.10, "芝特別戦◯": 0.05}, "note": "外枠◎、芝特別戦◯"},
    "R.ムーア": {"base": 1.30, "factors": {}, "special_factors": {"中山◎": 0.10}, "note": "世界最高峰。中山◎"},
    "短期免許外国人": {"base": 1.20, "factors": {"重賞": 0.10}, "note": "有力馬配置多め評価"},
    "地方所属騎手": {"base": 1.05, "factors": {"ダート": 0.15, "東京ダ1600": 0.10}, "note": "地方リーディング級"},
    "その他（自由手入力）": {"base": 1.00, "factors": {}, "note": "リスト外の騎手。"}
}

# ==========================================
# 🗺️ 2. コース事典マスターデータ
# ==========================================
COURSE_MASTER = {
    "東京芝1600m": {"note": "2月内枠、2月以外外枠。同距離＆距離短縮馬、重賞は差し・追い込み有利。ロードカナロア/エピファネイア/モーリス/キズナ/ハーツクライ。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ系", "ロードカナロア"], "fav_style": "差し"},
    "東京芝2000m": {"note": "1枠有利. 前走同距離＆距離短縮が好走。エピファネイア/モーリス牡馬/キズナ/ハーツクライ/ロードカナロア。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "モーリス", "キズナ", "ハーツクライ系"], "fav_style": "先行・差し"},
    "東京芝2400m": {"note": "オークスは差し・追い込み。ジャパンカップはダービー・オークス3着以内の3歳馬有利。インをロスなく回れる内〜中枠有利。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ドゥラメンテ", "ディープインパクト系"], "fav_style": "差し"},
    "東京ダート1600m": {"note": "外枠有利。前走同距離＆距離短縮馬。ヘニーヒューズ/ドレフォン(逃げ先行有利)。マイル以上のスタミナとパワー必須。", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "シニスターミニスター"], "fav_style": "先行"},
    "中山芝1200m": {"note": "ファインニードル産駒○、アメリカンペイトリオット産駒○。スピードの持続力と最後の急坂を耐えるパワーが必要。内枠有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ファインニードル", "アメリカンペイトリオット", "ロードカナロア"], "fav_style": "逃げ"},
    "中山芝2000m": {"note": "皐月賞はマイル〜1800m重賞実績馬○。荒れ馬場は外差し○。エピファネイア/キズナ/ドゥラメンテ/モーリス/ロードカナロア。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "キズナ", "ドゥラメンテ", "モーリス"], "fav_style": "先行"},
    "中山芝2500m": {"note": "高速馬場の有馬記念は東京中距離G1実績馬○。高速馬場は内枠、荒れ馬場は外枠有利.エピファネイア/キズナ/ゴールドシップ。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キズナ", "ゴールドシップ"], "fav_style": "先行"},
    "中京芝1200m": {"note": "内枠、距離短縮馬の内枠、内枠の逃げ先行馬○。ロードカナロア/ビッグアーサー/ミッキーアイル/ダイワメジャー。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー", "ミッキーアイル", "ダイワメジャー"], "fav_style": "逃げ先行"},
    "中京ダート1800m": {"note": "内をロスなく立ち回れる逃げ先行馬○。時計がかかると外差し○。チャンピオンズCなど内枠有利。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_style": "逃げ先行"},
    "京都芝1600m(外)": {"note": "同距離＆距離短縮馬。高速馬場は上がり時計重視○。荒れ馬場は外枠有利(キズナ/エピファネイア/ロードカナロア)。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "エピファネイア", "ロードカナロア"], "fav_style": "差し"},
    "京都芝2000m": {"note": "上級条件は差し馬○。秋華賞は差し馬・オークス出走馬が狙い目。キズナ/キタサンブラック/エピファネイア/ドゥラメンテ。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "キタサンブラック", "エピファネイア", "ドゥラメンテ"], "fav_style": "差し"},
    "京都芝2200m": {"note": "馬場良好なら内枠○。エリザベス女王杯も内枠有利。キズナ牝馬/サトノダイヤモンド/モーリス。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "サトノダイヤモンド", "モーリス"], "fav_style": "先行・差し"},
    "京都芝3000m": {"note": "外枠有利. 父または母父ステイゴールド系○。小柄なエピファネイア/ゴールドシップ/キタサンブラック。", "track": "芝", "dist": "長距離", "good_lineage": ["ステイゴールド系", "ゴールドシップ", "キタサンブラック"], "fav_style": "先行・差し"},
    "京都芝3200m": {"note": "人気馬○。または母父ステイゴールド系。前走阪神大賞典で上がり最速の馬○。スタミナ絶対条件。", "track": "芝", "dist": "長距離", "good_lineage": ["ステイゴールド系", "メジロマックイーン"], "fav_style": "先行・差し"},
    "阪神芝1600m": {"note": "内枠有利。高速馬場は外差し、同距離＆距離短縮馬○。ロードカナロア/エピファネイア/モーリス/キズナ/ハーツクライ。", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス", "キズナ", "ハーツクライ系"], "fav_style": "差し"},
    "阪神芝2000m": {"note": "外枠の先行馬有利。大阪杯は内差し。ドゥラメンテ牝馬/ルーラーシップ/キズナ/エピファネイア/ハーツクライ。", "track": "芝", "dist": "中距離", "good_lineage": ["ドゥラメンテ", "ルーラーシップ", "キズナ", "エピファネイア", "ハーツクライ系"], "fav_style": "先行"},
    "阪神芝2200m": {"note": "先行〜中団差し馬○。キズナ/ルーラーシップ/イスラボニータ/キタサンブラック.宝塚記念はタフな馬場適性重視。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "ルーラーシップ", "イスラボニータ", "キタサンブラック"], "fav_style": "先行・差し"},
    "札幌芝1200m": {"note": "Aコースは逃げ・先行馬有利。Cコースは外枠有利。距離短縮馬有利。ロードカナロア/ファインニードル/タワーオブロンドン/ミッキーアイル牝馬特注。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ファインニードル", "タワーオブロンドン", "ミッキーアイル"], "fav_style": "逃げ・先行"},
    "札幌芝1500m": {"note": "Aコースは内枠有利、先行馬有利. Cコースは外枠有利。前走東京芝1400m組○。モーリス/エピファネイア/キズナ牝馬特注。", "track": "芝", "dist": "短距離", "good_lineage": ["モーリス", "エピファネイア", "キズナ"], "fav_style": "先行"},
    "札幌芝1800m": {"note": "逃げ・先行馬有利、差し捲りも可能。Cコースは外枠有利.ドゥラメンテ/ハービンジャー/ロードカナロア/スワーヴリチャード/リオンディーズ/キタサンブラック/ゴールドシップ/母父ハーツクライ特注。", "track": "芝", "dist": "中距離", "good_lineage": ["ドゥラメンテ", "ハービンジャー", "ロードカナロア", "スワーヴリチャード", "リオンディーズ", "キタサンブラック", "ゴールドシップ"], "fav_style": "逃げ・先行"},
    "札幌芝2000m": {"note": "逃げ・先行馬有利、差し捲り馬も活躍。前走函館芝2000mの2,3着馬○。ゴールドシップ/オルフェーヴル/ドゥラメンテ/キズナ/モーリス/ハービンジャー/ジャスタウェイ/母父ハーツクライ特注。", "track": "芝", "dist": "中距離", "good_lineage": ["ゴールドシップ", "オルフェーヴル", "ドゥラメンテ", "キズナ", "モーリス", "ハービンジャー", "ジャスタウェイ"], "fav_style": "逃げ・先行"},
    "札幌芝2600m": {"note": "内枠有利、先行馬有利。前走函館芝2600mで上がり最速または前走東京芝2400mで2～5着馬特注。ドゥラメンテ/キズナ/オルフェーヴル/サトノクラウン/エピファネイア480kg未満/レイデオロ牡セン特注。", "track": "芝", "dist": "長距離", "good_lineage": ["ドゥラメンテ", "キズナ", "オルフェーヴル", "サトノクラウン", "エピファネイア", "レイデオロ"], "fav_style": "先行"},
    "札幌ダート1000m": {"note": "逃げ・先行馬有利、外枠有利。シニスターミニスター/ヘニーヒューズ/アジアエクスプレス/リオンディーズ/ロードカナロア/マジェスティックウォリアー4〜8枠特注。", "track": "ダート", "dist": "短距離", "good_lineage": ["シニスターミニスター", "ヘニーヒューズ", "アジアエクスプレス", "リオンディーズ", "ロードカナロア", "マジェスティックウォリアー"], "fav_style": "逃げ・先行"},
    "札幌ダート1700m": {"note": "良馬場は外枠有利・差し捲り。道悪は距離延長×前走上がり3位以内特注。ヘニーヒューズ/ドレフォン/キズナ/シニスターミニスター牡/パイロ牡/リオンディーズ牡/マジェスティックウォリアー5〜8枠特注。", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "キズナ", "シニスターミニスター", "パイロ", "リオンディーズ", "マジェスティックウォリアー"], "fav_style": "差し・追い込み"},
    "函館芝1200m": {"note": "下級条件は逃げ・先行有利。高速馬場は内枠有利。距離短縮馬有利. ロードカナロア/モーリス/ビッグアーサー/キンシャサノキセキ/ミッキーアイル牝/キタサンブラック牝特注。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "モーリス", "ビッグアーサー", "キンシャサノキセキ", "ミッキーアイル", "キタサンブラック"], "fav_style": "逃げ・先行"},
    "函館芝1800m": {"note": "逃げ・先行馬有利、内枠有利。前走同等距離(1600~2000)特注。キズナ/キタサンブラック/ダノンバラード/サトノダイヤモンド/ハービンジャー(逃げ先行)/ロードカナロア特注。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "キタサンブラック", "ダノンバラード", "サトノダイヤモンド", "ハービンジャー", "ロードカナロア"], "fav_style": "逃げ・先行"},
    "函館芝2000m": {"note": "下級条件は逃げ・先行有利、上級条件は先行・差し有利。同距離・距離短縮馬有利。ハービンジャー/キズナ/キタサンブラック/ダノンバラード/エピファネイア特注。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "キズナ", "キタサンブラック", "ダノンバラード", "エピファネイア"], "fav_style": "先行・差し"},
    "函館ダート1000m": {"note": "逃げ・先行馬有利、内枠有利、距離短縮ローテ特注。ヘニーヒューズ/シニスターミニスター/サウスヴィグラス/アジアエクスプレス/ドレフォン/キンシャサノキセキ牝馬特注。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "シニスターミニスター", "サウスヴィグラス", "アジアエクスプレス", "ドレフォン", "キンシャサノキセキ"], "fav_style": "逃げ・先行"},
    "函館ダート1700m": {"note": "良馬場は逃げ・先行馬有利、内枠有利。道悪は外枠有利。距離短縮×内枠は特注補正。前走中京ダート1800m組○。シニスターミニスター/ヘニーヒューズ/ドレフォン/ルーラーシップ/ロードカナロア/ホッコータルマエ牡セン/マジェスティックウォリアー牡セン/エスポワールシチー牡セン特注。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ヘニーヒューズ", "ドレフォン", "ルーラーシップ", "ロードカナロア", "ホッコータルマエ", "マジェスティックウォリアー", "エスポワールシチー"], "fav_style": "逃げ・先行"}
}

# ==========================================
# 🧬 3. 血統の系統自動判定マスター
# ==========================================
BLOOD_LINEAGE_MAP = {
    "ディープインパクト系": ["ディープインパクト", "キズナ", "コントレイル", "サトノダイヤモンド", "リアルインパクト", "ミッキーアイル", "ワールドエース"],
    "ハーツクライ系": ["ハーツクライ", "ジャスタウェイ", "スワーヴリチャード", "サリオス", "シュヴァルグラン"],
    "ステイゴールド系": ["ステイゴールド", "オルフェーヴル", "ゴールドシップ", "インディチャンプ", "ウインバリアシオン"],
    "キングカメハメハ系": ["キングカメハメハ", "ロードカナロア", "ドゥラメンテ", "ルーラーシップ", "レイデオロ", "ホッコータルマエ"],
    "エピファネイア": ["エピファネイア"],
    "モーリス": ["モーリス"],
    "キタサンブラック": ["キタサンブラック"],
    "ヘニーヒューズ": ["ヘニーヒューズ"],
    "ドレフォン": ["ドレフォン"],
    "シニスターミニスター": ["シニスターミニスター"]
}

def auto_detect_lineage(sire_name):
    if not sire_name: return []
    detected = []
    for system_name, match_list in BLOOD_LINEAGE_MAP.items():
        for target in match_list:
            if target in sire_name:
                detected.append(system_name)
                break
    return detected

SIRE_TRACK_APTITUDE = {
    "キズナ": "A", "オルフェーヴル": "A", "ゴールドシップ": "A", "ハービンジャー": "A", "クロフネ": "A", "シニスターミニスター": "A",
    "ドゥラメンテ": "B", "エピファネイア": "B", "モーリス": "B", "ルーラーシップ": "B", "キングカメハメハ": "B", "キタサンブラック": "B",
    "ロードカナロア": "C", "ハーツクライ": "C", "ディープインパクト": "D"
}

def determine_final_aptitude(sire_name, has_past_record):
    base_apt = "C"
    for sire, apt in SIRE_TRACK_APTITUDE.items():
        if sire in sire_name:
            base_apt = apt
            break
    if has_past_record:
        if base_apt in ["C", "D"]: return "B"
        elif base_apt == "B": return "A"
    return base_apt

# --- 🛰️ 当日環境設定エリア ---
st.header("🛰️ 当日のレース環境")
env_cols = st.columns(4)
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
    total_budget = st.number_input("💰 このレースの想定軍資金 (円):", min_value=100, max_value=100000, value=5000, step=100)

auto_track, auto_dist, good_blood_list, course_note = "選択なし", "選択なし", [], ""
if sel_course != "(未選択)":
    c_info = COURSE_MASTER[sel_course]
    course_note = c_info["note"]
    st.info(f"**【{sel_course} の特徴・有力血統】**\n\n{course_note}")
    auto_track, auto_dist, good_blood_list = c_info["track"], c_info["dist"], c_info["good_lineage"]

st.divider()

# ==========================================
# 📋 出馬表入力エリア
# ==========================================
st.write("### 📝 出馬表データ入力")

c_widths = [0.6, 1.4, 0.6, 0.6, 0.6, 0.7, 0.6, 1.3, 0.6, 1.3, 1.0, 0.8, 0.8, 0.8, 0.8, 1.2, 1.2, 0.8]
cols = st.columns(c_widths)
headers = ["馬番", "馬名", "人気", "指数", "斤量", "馬体重", "前3F", "父馬", "道悪", "騎手選択", "手入力メモ", "馬場", "脚質", "枠有利", "前走距離", "特記メモ補正①", "特記メモ補正②", "最終スコア"]
for col, h in zip(cols, headers):
    col.write(f"**{h}**")

current_inputs = {"course": sel_course, "track_condition": track_condition, "race_class": race_class, "rows": {}}
style_counts = {"逃げ": 0, "先行": 0, "差し": 0, "追い込み": 0}

row_tmp_data = []
for i in range(1, 19):
    c = st.columns(c_widths)
    s_row = st.session_state["loaded_data"].get("rows", {}).get(str(i), {})
    
    num = c[0].text_input(f"num_{i}", value=s_row.get("num", str(i)), label_visibility="collapsed")
    name = c[1].text_input(f"name_{i}", value=s_row.get("name", ""), label_visibility="collapsed")
    pop = c[2].number_input(f"pop_{i}", min_value=1, max_value=18, value=int(s_row.get("pop", 10)), label_visibility="collapsed")
    idx = c[3].number_input(f"idx_{i}", value=float(s_row.get("idx", 0.0)), step=0.1, label_visibility="collapsed")
    
    wgt = c[4].number_input(f"wgt_{i}", min_value=48.0, max_value=62.0, value=float(s_row.get("wgt", 56.0)), step=0.5, label_visibility="collapsed")
    wgh = c[5].number_input(f"wgh_{i}", min_value=350, max_value=600, value=int(s_row.get("wgh", 480)), step=2, label_visibility="collapsed")
    
    l3f = c[6].number_input(f"l3f_{i}", value=float(s_row.get("l3f", 35.0)), step=0.1, label_visibility="collapsed")
    sire = c[7].text_input(f"sire_{i}", value=s_row.get("sire", ""), label_visibility="collapsed", placeholder="父馬")
    has_heavy_record = c[8].checkbox(f"rec_{i}", value=s_row.get("heavy_record", False), label_visibility="collapsed")
    
    jock_list = sorted([k for k in JOCKEY_MASTER.keys() if k != "その他（自由手入力）"]) + ["その他（自由手入力）"]
    jock = c[9].selectbox(f"jock_{i}", ["(未選択)"] + jock_list, index=(["(未選択)"] + jock_list).index(s_row.get("jock", "(未選択)")) if s_row.get("jock") in (["(未選択)"] + jock_list) else 0, label_visibility="collapsed")
    
    special_opts = ["選択なし"]
    if jock in JOCKEY_MASTER and "special_factors" in JOCKEY_MASTER[jock]:
        special_opts += list(JOCKEY_MASTER[jock]["special_factors"].keys())
        
    custom_note = c[10].text_input(f"custom_note_{i}", value=s_row.get("custom_note", ""), label_visibility="collapsed", placeholder="特徴・メモ")
        
    sel_track = c[11].selectbox(f"track_{i}", ["選択なし", "芝", "ダート"], index=["選択なし", "芝", "ダート"].index(s_row.get("sel_track", auto_track if auto_track in ["芝", "ダート"] else "選択なし")), label_visibility="collapsed")
    sel_style = c[12].selectbox(f"style_{i}", ["選択なし", "逃げ", "先行", "差し", "追い込み"], index=["選択なし", "逃げ", "先行", "差し", "追い込み"].index(s_row.get("sel_style", "選択なし")), label_visibility="collapsed")
    
    if name and sel_style in style_counts:
        style_counts[sel_style] += 1
        
    f_opts = ["選択なし", "内枠", "外枠"]
    try: f_def_idx = 1 if int(num) <= 8 else (2 if int(num) >= 13 else 0)
    except: f_def_idx = 0
    sel_frame = c[13].selectbox(f"frame_{i}", f_opts, index=f_opts.index(s_row.get("sel_frame", f_opts[f_def_idx])), label_visibility="collapsed")
    
    sel_dist_change = c[14].selectbox(f"dist_change_{i}", ["同距離", "距離短縮", "距離延長"], index=["同距離", "距離短縮", "距離延長"].index(s_row.get("sel_dist_change", "同距離")), label_visibility="collapsed")
    
    sel_plus1 = c[15].selectbox(f"p5_1_{i}", special_opts, index=special_opts.index(s_row.get("sel_plus1")) if s_row.get("sel_plus1") in special_opts else 0, label_visibility="collapsed")
    sel_plus2 = c[16].selectbox(f"p5_2_{i}", special_opts, index=special_opts.index(s_row.get("sel_plus2")) if s_row.get("sel_plus2") in special_opts else 0, label_visibility="collapsed")
    
    current_inputs["rows"][str(i)] = {
        "num": num, "name": name, "pop": pop, "idx": idx, "wgt": wgt, "wgh": wgh, "l3f": l3f, "sire": sire, "heavy_record": has_heavy_record,
        "jock": jock, "custom_note": custom_note, "sel_track": sel_track, "sel_style": sel_style, 
        "sel_frame": sel_frame, "sel_dist_change": sel_dist_change, "sel_plus1": sel_plus1, "sel_plus2": sel_plus2
    }
    
    row_tmp_data.append((num, name, pop, idx, wgt, wgh, l3f, sire, has_heavy_record, jock, custom_note, sel_track, sel_style, sel_frame, sel_dist_change, sel_plus1, sel_plus2, c[17]))

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
# 📊 スコア計算ロジック
# ==========================================
calculated_results = []
for item in row_tmp_data:
    num, name, pop, idx, wgt, wgh, l3f, sire, has_heavy_record, jock, custom_note, sel_track, sel_style, sel_frame, sel_dist_change, sel_plus1, sel_plus2, score_cell = item
    
    score = 0.0
    final_apt = "C"
    
    if jock != "(未選択)" and name != "":
        j_data = JOCKEY_MASTER.get(jock, JOCKEY_MASTER["その他（自由手入力）"])
        jockey_modifier = 0.0
        
        chosen_conditions = [sel_track, sel_style, sel_frame, sel_dist_change, sel_course]
        for cond in chosen_conditions:
            if cond in j_data.get("factors", {}):
                jockey_modifier += j_data["factors"][cond]
            elif cond and cond.endswith("m") and cond[:-1] in j_data.get("factors", {}):
                jockey_modifier += j_data["factors"][cond[:-1]]
                
        if "special_factors" in j_data:
            if sel_plus1 in j_data["special_factors"]:
                jockey_modifier += j_data["special_factors"][sel_plus1]
            if sel_plus2 in j_data["special_factors"]:
                jockey_modifier += j_data["special_factors"][sel_plus2]
                
        if jockey_modifier < 0 and l3f <= 33.9: jockey_modifier = 0.0  
        final_jockey_rate = j_data["base"] + max(min(jockey_modifier, 0.20), -0.20)
        
        if idx < 45.0:
            mitigated_jockey_rate = 1.0 + (final_jockey_rate - 1.0) * 0.40
        else:
            mitigated_jockey_rate = 1.0 + (final_jockey_rate - 1.0) * 0.70
        
        horse_base_score = idx
        
        weight_diff = 56.0 - wgt
        horse_base_score += weight_diff * 1.5
        
        if wgh > 0:
            burden_rate = wgt / wgh
            if burden_rate > 0.125:
                if auto_dist == "長距離" or track_condition in ["稍重", "重・不良"]:
                    horse_base_score -= 3.0
                else:
                    horse_base_score -= 1.0
            elif burden_rate < 0.112:
                horse_base_score += 1.5
                
        is_upper_class_race = race_class in ["G1", "G2/G3", "オープン/L"]
        if is_upper_class_race and wgt >= 57.5:
            horse_base_score += 2.5
        elif race_class == "3勝クラス以下" and wgt <= 51.0:
            horse_base_score += 1.0
        
        if str(num).strip() == "7":
            horse_base_score += 2.0
        elif str(num).strip() in ["9", "13"]:
            horse_base_score += 1.0
        try:
            if int(num) % 2 != 0 and str(num).strip() not in ["7", "9", "13"]:
                horse_base_score += 0.5
        except ValueError:
            pass
        try:
            if int(num) >= 15:
                horse_base_score -= 1.5
        except ValueError:
            pass
            
        try:
            horse_num_int = int(num)
            if sel_course == "東京芝1600m":
                if 5 <= horse_num_int <= 12:
                    horse_base_score += 2.0
                elif 13 <= horse_num_int <= 17:
                    horse_base_score += 2.5
                elif 1 <= horse_num_int <= 2:
                    horse_base_score -= 2.0
            elif sel_course and "京都芝" in sel_course:
                if horse_num_int >= 10:
                    horse_base_score += 2.0
            elif sel_course in ["中京ダート1800m", "東京ダート1600m"]:
                if 1 <= horse_num_int <= 9:
                    horse_base_score += 2.0
                elif horse_num_int >= 14:
                    horse_base_score -= 2.0
        except ValueError:
            pass

        if sel_course != "(未選択)":
            detected_lineages = auto_detect_lineage(sire)
            lineage_matched = False
            for target in good_blood_list:
                if target in sire or (sire and sire in target):
                    lineage_matched = True
                for detected in detected_lineages:
                    if target in detected or detected in target:
                        lineage_matched = True
            if lineage_matched:
                horse_base_score += 5.0
            
            if sire and (sire in course_note):
                horse_base_score += 3.0
                
            fav_style = COURSE_MASTER[sel_course].get("fav_style", "")
            if sel_style in fav_style and sel_style != "選択なし":
                horse_base_score += 3.0
                
            if "内枠有利" in course_note or "1枠有利" in course_note:
                if sel_frame == "内枠": horse_base_score += 2.0
            if "外枠有利" in course_note:
                if sel_frame == "外枠": horse_base_score += 2.0
                
            if "距離短縮" in course_note and sel_dist_change == "距離短縮":
                horse_base_score += 3.0
            if "同距離" in course_note and sel_dist_change == "同距離":
                horse_base_score += 3.0
            if "距離延長" in course_note and sel_dist_change == "距離延長":
                horse_base_score += 3.0
                
            if is_upper_class_race:
                if idx >= 65.0:
                    horse_base_score += 2.0

        if (sel_style in ["逃げ", "先行"]) and (l3f <= 34.5): horse_base_score += 3.0 
        
        pop_penalty_factor = 0.7
        if pop >= 10:
            pop_penalty_factor = 0.95
            
        score = (horse_base_score * mitigated_jockey_rate) - (pop * pop_penalty_factor)
        
        if sel_style in pace_bonus:
            score += pace_bonus[sel_style]
        
        final_apt = determine_final_aptitude(sire, has_heavy_record)
        if track_condition == "稍重":
            if final_apt == "A": score += 2.0
            elif final_apt == "D": score -= 3.0
        elif track_condition == "重・不良":
            if final_apt == "A": score += 5.0
            elif final_apt == "B": score += 2.0
            elif final_apt == "C": score -= 4.0
            elif final_apt == "D": score -= 10.0
            
    score_cell.write(f"**{score:.2f}**")
    calculated_results.append({
        "馬番": num, "馬名": name, "最終スコア": score, "人気": pop, "斤量": wgt, "馬体重": wgh, "父馬": sire, "重道悪適性": final_apt, "騎手": jock, "戦略メモ": j_data.get("note", "") if jock != "(未選択)" else ""
    })

# ==========================================
# 💾 スマホ専用セーブデータ生成エリア（強化版）
# ==========================================
st.divider()
st.write("### 💾 スマホ用セーブデータ生成")

mobile_code = encode_for_mobile(current_inputs)

save_cols = st.columns(2)
with save_cols[0]:
    st.write("▼ 【推奨】コードだけをコピー（メモ帳用）")
    # 高度なクリップボード貼り付け用安全スクリプト
    if st.button("📋 セーブコードをコピー", use_container_width=True):
        html(f"""<script>
            function copyText() {{
                const text = '{mobile_code}';
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(text).then(() => {{
                        alert('📥 短いセーブコードをコピーしました！スマホのメモ帳等に貼り付けて保存してください。');
                    }}).catch(err => {{ fallbackCopy(text); }});
                }} else {{
                    fallbackCopy(text);
                }}
            }}
            function fallbackCopy(text) {{
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {{
                    document.execCommand('copy');
                    alert('📥 短いセーブコードをコピーしました！(安全モード)');
                }} catch (err) {{
                    alert('コピーに失敗しました。お手数ですがコード欄から手動で選択コピーしてください。');
                }}
                document.body.removeChild(textArea);
            }}
            copyText();
            </script>""", height=0)
    st.caption(f"コードプレビュー: `{mobile_code[:20]}...`")

with save_cols[1]:
    st.write("▼ URLごとコピー（ブラウザお気に入り用）")
    if st.button("🔗 復元URLをコピー", use_container_width=True):
        # 現在実行されている環境（localhostやクラウド等）のドメインをJS側で自動判別して結合
        html(f"""<script>
            function copyUrl() {{
                const code = '{mobile_code}';
                const generatedUrl = window.location.origin + window.location.pathname + '?data=' + code;
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(generatedUrl).then(() => {{
                        alert('🔗 復元URLをコピーしました！お気に入り等に登録してください。');
                    }}).catch(err => {{ fallbackCopyUrl(generatedUrl); }});
                }} else {{
                    fallbackCopyUrl(generatedUrl);
                }}
            }}
            function fallbackCopyUrl(text) {{
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {{
                    document.execCommand('copy');
                    alert('🔗 復元URLをコピーしました！(安全モード)');
                }} catch (err) {{
                    alert('コピーに失敗しました。お手数ですがURL欄を手動でコピーしてください。');
                }}
                document.body.removeChild(textArea);
            }}
            copyUrl();
            </script>""", height=0)

# ==========================================
# 🏆 ランキング生成 & 買い目自動生成
# ==========================================
if st.button("🏆 最終予想 ＆ 資金配分AI買い目生成", type="primary", use_container_width=True):
    res_df = pd.DataFrame(calculated_results)
    res_df = res_df[res_df["馬名"] != ""].sort_values(by="最終スコア", ascending=False)
    
    if not res_df.empty:
        st.balloons()
        
        symbols = ["◎", "○", "▲", "△", "⭐︎"]
        res_df["印"] = [symbols[idx] if idx < len(symbols) else " " for idx in range(len(res_df))]
        
        st.header(f"🎯 本命馬: {res_df.iloc[0]['印']} {res_df.iloc[0]['馬名']} ({res_df.iloc[0]['騎手']})")
        st.dataframe(res_df[["印", "馬番", "馬名", "人気", "斤量", "馬体重", "父馬", "最終スコア", "騎手", "重道悪適性"]], use_container_width=True, hide_index=True)
        
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

# ==========================================
# 📊 5. 的中率・回収率データログシミュレーター
# ==========================================
st.divider()
st.header("📊 的中率・回収率データログシミュレーター")

with st.expander("📝 当日レースの結果入力を記録する"):
    log_cols = st.columns(4)
    with log_cols[0]:
        res_course = st.text_input("レース名/コース:", value=st.session_state.get("last_predict_course", ""))
    with log_cols[1]:
        res_jiku = st.text_input("軸馬名:", value=st.session_state.get("last_predict_horse", ""))
    with log_cols[2]:
        is_hit = st.selectbox("軸馬の着順結果:", ["3着以内（的中）", "4着以下（不不不的中）"])
    with log_cols[3]:
        return_amt = st.number_input("実際の総払戻金 (円):", min_value=0, value=0, step=100)
        
    invest_amt = st.number_input("実際の総投資額 (円):", min_value=100, value=int(total_budget), step=100)

    if st.button("💾 この結果をシミュレーションログに公式記録する"):
        hit_flag = 1 if "3着以内" in is_hit else 0
        st.session_state["history_log"].append({
            "コース": res_course, "軸馬": res_jiku, "的中": hit_flag, "投資": invest_amt, "払戻": return_amt
        })
        st.toast("実績データを蓄積しました！")

if st.session_state["history_log"]:
    log_df = pd.DataFrame(st.session_state["history_log"])
    total_races = len(log_df)
    hits = log_df["的中"].sum()
    hit_rate = (hits / total_races) * 100 if total_races > 0 else 0
    total_invest = log_df["投資"].sum()
    total_return = log_df["払戻"].sum()
    recovery_rate = (total_return / total_invest) * 100 if total_invest > 0 else 0
    
    st.write("### 📉 現在の回収率・的中率スタッツ")
    stat_cols = st.columns(4)
    stat_cols[0].metric("総シミュレーションレース数", f"{total_races} 戦")
    stat_cols[1].metric("軸馬複勝的中率", f"{hit_rate:.1f} %")
    stat_cols[2].metric("累計投資総額", f"{total_invest:,} 円")
    stat_cols[3].metric("📊 総合回収率 (回収バロメータ)", f"{recovery_rate:.1f} %")
    
    st.write("▼ 直近の記録ログデータ一覧")
    st.dataframe(log_df, use_container_width=True)

