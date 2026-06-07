import streamlit as st
import pandas as pd
import json
import urllib.parse
from streamlit.components.v1 import html

# ==========================================
# 🏇 1. ジョッキー事典マスターデータ（大幅拡充・調整版）
# ==========================================
# インフレを抑えるため、トップジョッキーのベースを1.25〜1.30にマイルド化し、
# 各コースや条件への適性を一字一句綺麗に統一しました。
JOCKEY_MASTER = {
    # --- 栗東（関西）所属 ---
    "C.ルメール": {"base": 1.30, "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": -0.05, "外枠": 0.05, "長距離": 0.05, "東京芝1600": 0.15, "東京芝2000": 0.15, "東京芝2400": 0.15, "京都芝1600": 0.15, "京都芝2400": 0.15, "中山芝2500": -0.10}, "note": "東京・京都外回り・長距離◎。中山のトリッキーなコースは僅かに割引"},
    "川田将雅": {"base": 1.30, "factors": {"芝1枠": 0.15, "小回り": 0.15, "交流重賞": 0.15, "長距離": -0.05, "阪神芝2000": 0.15, "中京ダ1800": 0.15, "中山芝2000": 0.15, "ローカル芝": -0.05}, "note": "阪神・中京・中山の内回り小回り◎。確勝級の馬での信頼度抜群"},
    "坂井瑠星": {"base": 1.25, "factors": {"先行": 0.10, "内枠": 0.05, "外枠": -0.05, "ダート重賞": 0.15, "東京ダ1600": 0.15, "中京ダ1800": 0.15}, "note": "逃げ先行・ダート重賞◎。海外や大舞台での積極策が光る"},
    "武豊": {"base": 1.20, "factors": {"芝": 0.05, "継続騎乗": 0.15, "人気薄": 0.15, "距離延長": 0.15, "京都芝2000": 0.15, "京都芝2200": 0.15, "東京芝2400": 0.15}, "note": "継続騎乗・大舞台での一発◎。京都コースを最も熟知するレジェンド"},
    "松山弘平": {"base": 1.15, "factors": {"ダート": 0.15, "新馬戦": 0.15, "前哨戦": 0.15, "中山ダ1800": 0.15, "京都ダ1800": 0.15}, "note": "ダート・新馬戦◎。非常に堅実で、乗り替わりも苦にしない"},
    "岩田望来": {"base": 1.10, "factors": {"マイル以下の差し": 0.15, "乗り替わり": 0.15, "中京芝1600": 0.10, "阪神芝1600": 0.10}, "note": "乗り替わり・マイル以下の差し○。平場・特別戦での安定感が高い"},
    "西村淳也": {"base": 1.10, "factors": {"京都芝": 0.15, "先行": 0.05, "京都芝1600": 0.15, "阪神芝1400": 0.15}, "note": "京都芝・先行策◎。G1でも穴を明ける度胸と勝負強さあり"},
    "団野大成": {"base": 1.10, "factors": {"短距離重賞": 0.15, "荒れ馬場": 0.15, "京都芝1200": 0.15, "阪神芝 1600": 0.10}, "note": "短距離重賞・荒れた芝◎。勝負どころでの思い切りの良さが魅力"},
    "鮫島克駿": {"base": 1.10, "factors": {"イン突き": 0.15, "中長距離": 0.15, "ダート外枠": 0.15, "中京芝2000": 0.10}, "note": "好位イン突き・中長距離◎。ロスを抑える立ち回りが得意"},
    "高杉吏麒": {"base": 1.05, "factors": {"減量活かした先行": 0.15, "ローカル芝": 0.10, "ローカルダート": 0.10, "短距離": 0.05}, "note": "急成長中の若手。減量を活かした積極策やローカルでの穴に要注意"},
    "藤岡佑介": {"base": 1.10, "factors": {"自在性": 0.15, "重賞の人気馬": -0.15}, "note": "展開読み◎（展開アドバイザー）。重賞の人気馬はやや割引"},
    "幸英明": {"base": 1.05, "factors": {"ダート": 0.15, "牡馬のタフ条件": 0.15, "阪神ダ1800": 0.10}, "note": "タフなダート戦・牡馬◎。とにかくタフで騎乗数も非常に多い"},
    "池添謙一": {"base": 1.15, "factors": {"大舞台＆重賞": 0.15, "差し＆追い込み": 0.15, "中山芝2500": 0.15}, "note": "G1・重賞での勝負強さ抜群。人気薄のグランプリで激走"},
    "岩田康誠": {"base": 1.15, "factors": {"重賞": 0.15, "内枠": 0.15, "阪神芝2000": 0.15}, "note": "内枠からのイン突き強襲◎。ベテランのイン攻め注意"},
    "M.デムーロ": {"base": 1.15, "factors": {"大舞台＆重賞": 0.15, "追い込み": 0.15, "東京芝2000": 0.10}, "note": "出遅れ注意も、大舞台でのマクリ・追い込みは破壊力あり"},
    "浜中俊": {"base": 1.05, "factors": {"芝": 0.05, "1番人気": 0.15, "中京芝1200": 0.10}, "note": "芝の短〜中距離・人気馬○。乗れている時の爆発力あり"},
    "北村友一": {"base": 1.10, "factors": {"芝8枠": 0.15, "中長距離戦": 0.15, "京都芝2200": 0.10}, "note": "外枠からの差し・中長距離○。復活後の大舞台でも健闘"},
    "横山典弘": {"base": 1.15, "factors": {"芝内枠": 0.15, "継続騎乗": 0.15, "東京芝2400": 0.10}, "note": "ポツン注意も内枠・継続◎。馬の気分に合わせた一発あり"},
    "和田竜二": {"base": 1.05, "factors": {"荒れ馬場": 0.15, "先行": 0.05, "京都ダ1800": 0.10}, "note": "追えるベテラン。タフな消耗戦やズブい馬で真価発揮"},
    "永島まなみ": {"base": 1.05, "factors": {"ローカルダート": 0.15, "先行": 0.10}, "note": "ローカルやダートの逃げ・先行は無類の強さ"},
    "田口貫太": {"base": 1.05, "factors": {"ローカルダート": 0.15, "芝1枠": 0.15, "中京芝1200": 0.10}, "note": "減量ブレイクから定着した若手。ダート人気馬・イン戦◎"},
    "松若風馬": {"base": 1.05, "factors": {"逃げ": 0.15, "ダート": 0.05}, "note": "積極的な逃げ・先行策が持ち味。ダート○"},
    "吉村誠之助": {"base": 1.00, "factors": {"ローカルダート": 0.10}, "note": "期待の若手。ダート戦や減量を活かした競馬で台頭"},

    # --- 美浦（関東）所属 ---
    "戸崎圭太": {"base": 1.25, "factors": {"前走ルメール": 0.10, "東京芝1600": 0.15, "東京ダ1600": 0.15, "中山ダ1800": 0.10, "重賞": 0.10}, "note": "東京マイル・ダート外枠・前走ルメールからの乗り替わり◎"},
    "横山武史": {"base": 1.25, "factors": {"中山芝2000": 0.15, "中山芝2500": 0.15, "先行": 0.10, "持久力戦": 0.15, "東京芝2400": 0.10}, "note": "中山重賞・先行持久力戦◎。関東のエース格"},
    "菅原明良": {"base": 1.15, "factors": {"長距離": 0.10, "差し": 0.05, "東京芝1600": 0.10, "新潟直線1000": 0.15}, "note": "G1制覇を経て大舞台の信頼度UP。穴を明ける長距離差し"},
    "佐々木大輔": {"base": 1.15, "factors": {"芝内枠": 0.15, "ローカル芝": 0.15, "中山芝1200": 0.10}, "note": "若手屈指の立ち回り。内枠＆北海道・ローカル開催の鬼"},
    "丹内祐次": {"base": 1.10, "factors": {"ローカル芝": 0.15, "ローカルダート": 0.15}, "note": "ローカル（函館・札幌・福島・小倉等）の帝王。人気薄激走多数"},
    "田辺裕信": {"base": 1.10, "factors": {"長距離戦": 0.15, "逃げ": 0.10, "東京ダ1400": 0.10}, "note": "人気薄の大胆な逃げや、ポツン差しなどノリに勝る奇策注意"},
    "横山和生": {"base": 1.15, "factors": {"東京芝2400": 0.10, "中山芝2500": 0.10, "ダート重賞": 0.15}, "note": "長距離の逃げ・先行や、ダート重賞での信頼度高"},
    "津村明秀": {"base": 1.10, "factors": {"新潟直線1000": 0.15, "東京芝1600": 0.10, "京都芝1600": 0.10}, "note": "新潟直線◎。マイルG1での立ち回り・勝負強さも完全に本格化"},
    "三浦皇成": {"base": 1.05, "factors": {"1番人気": 0.15, "重賞": -0.15, "東京ダ1600": 0.10}, "note": "平場・条件戦の1番人気は堅実。重賞ではやや割引"},
    "大野拓哉": {"base": 1.05, "factors": {"東京ダ1600": 0.15, "追い込み": 0.15, "中山芝1200": 0.10}, "note": "東京ダートや外枠の追い込み穴馬で強烈な差しを見せる"},
    "石川裕紀人": {"base": 1.10, "factors": {"芝1枠": 0.15, "積極策": 0.10, "東京芝2000": 0.10}, "note": "大舞台での思い切った先行策・イン突きの魅力あり"},
    "北村宏司": {"base": 1.05, "factors": {"東京芝1600": 0.10, "内枠": 0.10, "東京芝2400": 0.10}, "note": "ベテランの安定感。東京の芝コースや内枠での立ち回り○"},
    "石橋脩": {"base": 1.05, "factors": {"先行": 0.10, "中山芝1600": 0.10}, "note": "ベテランの先行押し切り。中山などタフなコースで注意"},
    "柴田善臣": {"base": 1.00, "factors": {"人気薄": 0.10}, "note": "現役最年長レジェンド。時折見せる絶妙な差し込み注意"},

    # --- 短期免許外国人・地方・その他 ---
    "J.モレイラ": {"base": 1.30, "factors": {"中長距離": 0.15, "ダート": 0.10, "東京芝2400": 0.15, "阪神芝1600": 0.10}, "note": "マジックマン。短期免許で来日時は勝率・連対率が異次元"},
    "D.レーン": {"base": 1.30, "factors": {"重賞": 0.15, "芝": 0.10, "東京芝2400": 0.10, "東京芝1600": 0.15}, "note": "日本の馬場適性が非常に高く、G1大舞台での信頼度絶大"},
    "R.キング": {"base": 1.25, "factors": {"先行": 0.15, "内枠": 0.10, "東京芝1600": 0.10}, "note": "抜群のスタートセンスと好位キープ力で前残り連発"},
    "T.マーカンド": {"base": 1.20, "factors": {"ダート": 0.15, "荒れ馬場": 0.10, "中山ダ1800": 0.15}, "note": "剛腕。タフな馬場やダート戦での追い比べは無類の強さ"},
    "H.ドイル": {"base": 1.15, "factors": {"先行": 0.10, "芝": 0.05}, "note": "好位からの手堅い立ち回りが光る英国の新星"},
    "短期免許外国人": {"base": 1.20, "factors": {"重賞": 0.10}, "note": "その他短期免許の外国人騎手。有力馬配置が多く高評価"},
    "地方所属騎手": {"base": 1.05, "factors": {"ダート": 0.15, "東京ダ1600": 0.10}, "note": "大井・川崎等の地方リーディング級。ダート戦で警戒"},
    
    "その他（自由手入力）": {"base": 1.00, "factors": {}, "note": "リスト外の騎手。右の入力欄に名前を記入してください。"}
}

# ==========================================
# 🗺️ 2. コース事典マスターデータ（JRA全10場＋主要コース網羅）
# ==========================================
COURSE_MASTER = {
    # --- 東京 ---
    "東京芝1600": {"note": "安田記念・NHKマイル等。重賞は差し・追い込み有利。ロードカナロア/エピファネイア産駒○", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス"]},
    "東京芝2000": {"note": "天皇賞秋等。1桁馬番(①〜⑧)が超強力。1枠有利。前走同距離＆距離短縮が好走。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "モーリス", "キズナ", "キタサンブラック"]},
    "東京芝2400": {"note": "日本ダービー・ジャパンC等。内〜中枠の立ち回り重視。前走速い脚を使った馬が有利。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ドゥラメンテ", "ハーツクライ"]},
    "東京ダ1400": {"note": "スタートが芝。外枠の先行馬が有利。スピード型の米国血統○。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス"]},
    "東京ダ1600": {"note": "フェブラリーS等。スタートが芝で外枠有利。ヘニーヒューズ/ドレフォン○。大型馬有利。", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "ロードカナロア"]},
    "東京ダ2100": {"note": "スタミナ必須。リピーターが走りやすい。ダートの長距離適性が最重要。", "track": "ダート", "dist": "長距離", "good_lineage": ["キングカメハメハ", "ハーツクライ"]},

    # --- 中山 ---
    "中山芝1200": {"note": "スプリンターズS等。スタートから下り坂でハイペース必至。内枠の先行・イン差し○。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"]},
    "中山芝1600": {"note": "トリッキーな1勝クラスのコーナー。外枠は絶望的に不利。内枠の先行馬が絶対有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ダイワメジャー", "スクリーンヒーロー"]},
    "中山芝2000": {"note": "皐月賞等。荒れ馬場は外差し○。エピファネイア/ハービンジャー/モーリス○。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "ハービンジャー", "モーリス"]},
    "中山芝2500": {"note": "有馬記念等。内枠（1桁馬番）の勝率が突出。高速馬場は内枠、荒れ馬場は外枠有利。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キズナ", "ドゥラメンテ", "ゴールドシップ"]},
    "中山ダ1200": {"note": "スタートが芝。外枠の快速馬が圧倒的に有利。スピードで押し切れる血統○。", "track": "ダート", "dist": "短距離", "good_lineage": ["サウスヴィグラス", "ヘニーヒューズ"]},
    "中山ダ1800": {"note": "非常にタフでスタミナが必要。先行馬が圧倒的に有利で、追い込みは厳しい。", "track": "ダート", "dist": "中距離", "good_lineage": ["ホッコータルマエ", "シニスターミニスター"]},

    # --- 京都 ---
    "京都芝1200": {"note": "内回り。直線が平坦のため前残りに注意。開幕週は内枠が絶対条件。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー"]},
    "京都芝1600": {"note": "マイルCS等。外回りコース。3コーナーの坂の登り下りがあり、ディープ系や差し馬台頭。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "エピファネイア", "キズナ"]},
    "京都芝2000": {"note": "秋華賞等。内回りコース。直線が短いため、一瞬の加速力を持つ先行・内立ち回り馬○。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "キングカメハメハ系"]},
    "京都芝2200": {"note": "エリザベス女王杯等。外回り。スタミナと持続力が必要で、リピーターの活躍が目立つ。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "ハービンジャー", "オルフェーヴル"]},
    "京都芝2400": {"note": "菊花賞のステップ等。外回り。長距離適性と、坂を下りながら加速できる器用さが必要。", "track": "芝", "dist": "長距離", "good_lineage": ["ディープインパクト系", "ルーラーシップ"]},
    "京都ダ1200": {"note": "直線平坦でスピード重視。逃げ・先行馬が圧倒的に有利なハイスピード馬場。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス"]},
    "京都ダ1800": {"note": "タフな中山と違い、スピード巡航能力が問われる。主流のダート血統が走りやすい。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "キングカメハメハ"]},

    # --- 阪神 ---
    "阪神芝1400": {"note": "内回り。タフなコースで短距離ながらスタミナ要求値が高い。ダイワメジャー○。", "track": "芝", "dist": "短距離", "good_lineage": ["ダイワメジャー", "ロードカナロア"]},
    "阪神芝1600": {"note": "桜花賞・ジュベナイルF等。外回り。高速馬場は外差し、ロードカナロア/エピファネイア○。", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "キズナ"]},
    "阪神芝2000": {"note": "大阪杯等。内回り。急坂を2回超える。外枠の先行馬有利。ドゥラメンテ/ルーラーシップ○。", "track": "芝", "dist": "中距離", "good_lineage": ["ドゥラメンテ", "ルーラーシップ", "キズナ"]},
    "阪神芝2200": {"note": "宝塚記念等。内回りコース。非常にタフなスタミナ消耗戦になりやすく、非根幹距離の鬼○。", "track": "芝", "dist": "中距離", "good_lineage": ["ステイゴールド系", "ハーツクライ", "キズナ"]},
    "阪神ダ1400": {"note": "スタートが芝。芝スタートをこなせる快速馬、外枠が有利。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "ロードカナロア"]},
    "阪神ダ1800": {"note": "基本的には先行有利。急坂があるため、馬体重のあるパワー型が信頼できる。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"]},

    # --- 中京 ---
    "中京芝1200": {"note": "高松宮記念等。直線が長く急坂もある。中京に実績のある中京リピーターに注意。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ミッキーアイル"]},
    "中京芝1600": {"note": "差しが届きやすいマイルコース。タフな血統やマイル実績馬○。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "ハービンジャー"]},
    "中京芝2000": {"note": "金鯱賞等。中京の2000mは急坂スタートでタフ。内枠の立ち回りとスタミナ重視。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "ハーツクライ"]},
    "中京ダ1200": {"note": "直線が長く坂もあるため、ダート短距離としては差しが決まりやすい部類に入る。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン"]},
    "中京ダ1800": {"note": "チャンピオンズC等。タフなダートコース。内枠の先行・好位差しが抜群に有利。", "track": "ダート", "dist": "中距離", "good_lineage": ["キングカメハメハ", "シニスターミニスター"]},

    # --- ローカル・その他 ---
    "新潟直線1000": {"note": "アイビスSD等。日本唯一の直線G1/重賞。外枠（7・8枠）が圧倒的に絶対有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ジョーカプチーノ"]},
    "ローカル芝": {"note": "福島・新潟・小倉・函館・札幌。小回りで直線が短いため、イン先行や開幕週の前残り警戒。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "ダイワメジャー"]},
    "ローカルダート": {"note": "小回りのダート。とにかく前に行ける減量ジョッキーや快速馬の押し切りが多い。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "サウスヴィグラス"]}
}

# ==========================================
# ⚙️ 3. アプリ初期設定 & レイアウト
# ==========================================
st.set_page_config(page_title="競馬予想・完全予想版システム", layout="wide")
st.title("🏆 競馬予想・ジョッキー＆コース事典 【完全予想版】")

if "loaded_data" not in st.session_state:
    st.session_state["loaded_data"] = None

# スマホ再開用URL（クエリパラメータ）のキャッチ
query_params = st.query_params
if "loaded_json" in query_params:
    try:
        st.session_state["loaded_data"] = json.loads(query_params["loaded_json"])
        st.query_params.clear()
    except:
        pass

# --- 🗺️ コース選択セクション ---
st.header("🗺️ コース選択")
saved_course = st.session_state["loaded_data"].get("course", "(未選択)") if st.session_state["loaded_data"] else "(未選択)"
sel_course = st.selectbox(
    "レースが行われるコースを選択してください:", 
    ["(未選択)"] + list(COURSE_MASTER.keys()), 
    index=(["(未選択)"] + list(COURSE_MASTER.keys())).index(saved_course) if saved_course in COURSE_MASTER else 0
)

auto_track, auto_dist, good_blood_list = "選択なし", "選択なし", []
if sel_course != "(未選択)":
    c_info = COURSE_MASTER[sel_course]
    st.info(f"**【{sel_course} の特徴・有力血統】**\n\n{c_info['note']}")
    auto_track, auto_dist, good_blood_list = c_info["track"], c_info["dist"], c_info["good_lineage"]

st.divider()

# ==========================================
# 📋 4. 出馬表入力エリア
# ==========================================
st.write("### 📝 出馬表データ入力（18頭フル対応・スマホ保存・インフレ抑制機能搭載）")

# セーブ・ロードボタン（スマホ完全対応）
save_cols = st.columns([3, 3, 6])
with save_cols[0]:
    save_clicked = st.button("📥 入力内容をスマホに一時保存（URLコピー）", use_container_width=True)
with save_cols[1]:
    load_clicked = st.button("📤 画面を更新して保存データを反映", use_container_width=True, type="secondary")

calculated_results = []

# グリッドの列幅
c_widths = [0.6, 1.4, 0.6, 0.6, 0.9, 1.4, 1.8, 1.2, 0.9, 0.9, 0.9, 0.9, 1.1, 1.1, 1.1, 1.1, 0.9]
cols = st.columns(c_widths)
headers = ["馬番", "馬名", "人気", "指数", "前3F", "父馬", "騎手選択", "手入力用", "馬場", "脚質", "枠順", "距離", "プラス条件①", "プラス条件②", "マイナス①", "マイナス②", "スコア"]
for col, h in zip(cols, headers):
    col.write(f"**{h}**")

current_inputs = {"course": sel_course, "rows": {}}

# 18頭分の入力行自動生成
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
    
    jock_list = sorted([k for k in JOCKEY_MASTER.keys() if k != "その他（自由手入力）"]) + ["その他（自由手入力）"]
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
        f_def_idx = 1 if int(num) <= 8 else (2 if int(num) >= 13 else 0)
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
    
    # ==========================================
    # 🧮 5. 新・スコア計算ロジック（インフレ抑制・マイルド化版）
# ==========================================
    score = 0.0
    note_text = ""
    
    if jock != "(未選択)":
        j_data = JOCKEY_MASTER.get(jock, JOCKEY_MASTER["その他（自由手入力）"])
        jockey_base = j_data["base"]
        factors = j_data["factors"]
        note_text = j_data.get("note", "")
        
        # 累積加点によるインフレを最大+0.20までに制限（キャップ制）
        jockey_modifier = 0.0
        chosen_conditions = [sel_track, sel_style, sel_frame, sel_dist, sel_plus1, sel_plus2, sel_minus1, sel_minus2, sel_course]
        for cond in chosen_conditions:
            if cond in factors:
                val = factors[cond]
                if val < 0 and l3f <= 33.9: val = 0.0  # 速い上がりを使える馬の減点保護
                jockey_modifier += val
                
        jockey_modifier = min(jockey_modifier, 0.20)
        jockey_modifier = max(jockey_modifier, -0.20)
        
        final_jockey_rate = jockey_base + jockey_modifier
        
        # 🌟 ジョッキーの影響度をマイルド（70%）に圧縮し、馬の実力を前に出す
        mitigated_jockey_rate = 1.0 + (final_jockey_rate - 1.0) * 0.70
        
        # 馬自体の基本値算出（指数に血統や馬場・展開補正を加算）
        horse_base_score = idx
        if sire != "" and any(target in sire for target in good_blood_list):
            horse_base_score += 5.0 # 血統適性加点
        if (sel_style in ["逃げ", "先行"]) and (l3f <= 34.5):
            horse_base_score += 3.0 # 前残り展開加点
            
        # 最終スコアの算出（人気による減点調整も含む）
        score = (horse_base_score * mitigated_jockey_rate) - (pop * 0.7)
        
    c[16].write(f"**{score:.2f}**")
    
    display_jock = custom_jock if jock == "その他（自由手入力）" else (jock if jock != "(未選択)" else "")
    calculated_results.append({
        "馬番": num, "馬name": name, "スコア": score, "父馬": sire, "騎手": display_jock, "戦略メモ": note_text
    })

# ==========================================
# 💾 6. スマホ完全対応ストレージ管理システム
# ==========================================
if save_clicked:
    json_str = json.dumps(current_inputs, ensure_ascii=False)
    encoded_json = urllib.parse.quote(json_str)
    # 現在のページURL（ブラウザの仕様に合わせ自動でクエリを付与）
    share_url = f"?loaded_json={encoded_json}"
    
    html(f"""
        <script>
        const url = window.parent.location.origin + window.parent.location.pathname + "{share_url}";
        navigator.clipboard.writeText(url).then(function() {{
            alert('📥 スマホ対応URLをコピーしました！\\nメモ帳やLINEに貼り付けて保存してください。');
        }}).catch(function(err) {{
            prompt('URLを長押ししてコピーしてください：', url);
        }});
        </script>
    """, height=0)

if load_clicked:
    html("<script>window.parent.location.reload();</script>", height=0)

# ==========================================
# 🏆 7. ランキング生成
# ==========================================
st.divider()
if st.button("🏆 最終予想ランキングを生成", type="primary", use_container_width=True):
    res_df = pd.DataFrame(calculated_results)
    res_df = res_df[res_df["馬name"] != ""].sort_values(by="スコア", ascending=False)
    
    if not res_df.empty:
        st.balloons()
        st.header(f"🎯 本命推奨馬: {res_df.iloc[0]['馬name']} ({res_df.iloc[0]['騎手']})")
        st.dataframe(res_df[["馬番", "馬name", "父馬", "スコア", "騎手", "戦略メモ"]], use_container_width=True, hide_index=True)
