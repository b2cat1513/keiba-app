import streamlit as st
import pandas as pd
import urllib.parse
import json

# ページ全体の基本設定
st.set_page_config(page_title="ジェニー予想完全版 ver1.20", layout="wide")

# ==========================================
# 🗺️ 1. コース完全マスター（全38コース網羅）
# ==========================================
COURSE_MASTER = {
    # 東京
    "東京芝1400": {"note": "3角までの直線が長く枠順差は少ない。短距離のスピードとマイルを乗り切るスタミナのバランス。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "不問", "fav_style": "先行"},
    "東京芝1600": {"note": "安田記念など。スタミナが必要なタフな流れになりやすく、差し・追い込み有利。上がり最速馬強力。", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア"], "fav_gate": "不問", "fav_style": "差し"},
    "東京芝1800": {"note": "毎日王冠など。スタート後すぐに2角のカーブがあるため内枠有利。キレ味が最重要視される。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ"], "fav_gate": "内枠", "fav_style": "差し"},
    "東京芝2000": {"note": "天皇賞(秋)など。スタート直後に2角があり外枠は壊滅的ロス。内枠の先行・好位差しが絶対有利。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "キズナ"], "fav_gate": "内枠", "fav_style": "先行"},
    "東京芝2400": {"note": "日本ダービーなど。日本競馬の最高峰。極端な有利不利はないがインをロスなく回れる内〜中枠有利。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ドゥラメンテ"], "fav_gate": "内枠", "fav_style": "差し"},
    "東京芝2500": {"note": "目黒記念など。坂の途中からのスタートでスタミナ要求値が高い。タフに伸びるスタミナ血統向き。", "track": "芝", "dist": "長距離", "good_lineage": ["ハーツクライ", "ルーラーシップ"], "fav_gate": "不問", "fav_style": "差し"},
    "東京芝3400": {"note": "【超長距離】ダイヤモンドS。向正面スタートからスタミナの絶対量が問われる。極限の折り合いと心肺機能が必要。", "track": "芝", "dist": "長距離", "good_lineage": ["ハーツクライ", "オルフェーヴル"], "fav_gate": "内枠", "fav_style": "差し"},
    "東京ダ1400": {"note": "根岸Sなど。芝スタート。外枠に行くほど芝を長く走れるため外枠のスピード馬が圧倒的有利。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "ロードカナロア"], "fav_gate": "外枠", "fav_style": "先行"},
    "東京ダ1600": {"note": "フェブラリーSなど。スタートが芝で外枠有利。ダートながらマイル以上のスタミナとパワー必須。", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "シニスターミニスター"], "fav_gate": "外枠", "fav_style": "先行"},
    "東京ダ2100": {"note": "直線が長くダートとしては屈指のスタミナが必要。スタミナ型の差し馬やスタミナ血統が台頭。", "track": "ダート", "dist": "長距離", "good_lineage": ["シニスターミニスター", "キングカメハメハ"], "fav_gate": "不問", "fav_style": "差し"},
    
    # 中山
    "中山芝1200": {"note": "スプリンターズSなど。4角まで下り坂。スピードの持続力と最後の急坂を耐えるパワーが必要。内枠有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "中山芝1600": {"note": "外回り。スタートが1角ポケットにあり外枠は壊滅的不利。1〜3枠絶対有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ダイワメジャー", "モーリス"], "fav_gate": "内枠", "fav_style": "先行"},
    "中山芝1800": {"note": "中山記念など。内回り。1角が近いため先行争い激化. タフな小回り適性と急坂での加速力が必要。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ"], "fav_gate": "内枠", "fav_style": "先行"},
    "中山芝2000": {"note": "皐月賞など。内回り。4回コーナーを回るため器用さが必要。開幕週はイン、荒れ馬場は外差し。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "キズナ"], "fav_gate": "不問", "fav_style": "先行"},
    "中山芝2200": {"note": "オールカマーなど。外回りから内回りへ合流するトリッキーな構成。スタミナと持続力血統が強い。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "ルーラーシップ"], "fav_gate": "不問", "fav_style": "差し"},
    "中山芝2500": {"note": "有馬記念。内回り。内枠(1桁馬番)の勝率が突出。急坂を2回超えるためタフなスタミナが必須。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "ゴールドシップ"], "fav_gate": "内枠", "fav_style": "先行"},
    "中山芝3600": {"note": "【超長距離】ステイヤーズS。内回りを3周、急坂を3回超えるJRA最長コース。純粋なスタミナと折り合い重視。", "track": "芝", "dist": "長距離", "good_lineage": ["ゴールドシップ", "オルフェーヴル", "ルーラーシップ"], "fav_gate": "不問", "fav_style": "先行"},
    "中山ダ1200": {"note": "芝スタートで外枠有利。テンのスピードが速く前残りしやすいが、ハイペース極まると外差し届く。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス"], "fav_gate": "外枠", "fav_style": "逃げ"},
    "中山ダ1800": {"note": "非常にタフな急坂がありスタミナ必要。基本先行有利。重馬場になると泥を嫌い外先行がさらに有利。", "track": "ダート", "dist": "中距離", "good_lineage": ["ホッコータルマエ", "シニスターミニスター"], "fav_gate": "不問", "fav_style": "先行"},
    
    # 京都
    "京都芝1200": {"note": "内回り。3角の坂を下るため高速スピードの持続力必要。基本は内枠の先行馬有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー"], "fav_gate": "内枠", "fav_style": "先行"},
    "京都芝1600": {"note": "マイルCSなど。外回り。3角坂下りから一気にペースアップ。平坦な直線での高速キレ味勝負。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "エピファネイア"], "fav_gate": "不問", "fav_style": "差し"},
    "京都芝1800": {"note": "外回り. スピードとキレ味の要求値が非常に高い。直線瞬発力勝負になりディープ系中心。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ"], "fav_gate": "不問", "fav_style": "差し"},
    "京都芝2000": {"note": "秋華賞など。内回り。スタート直後に1角があり内枠有利。先行・好位差しがベスト。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "エピファネイア"], "fav_gate": "内枠", "fav_style": "先行"},
    "京都芝2200": {"note": "エリザベス女王杯など。外回り。3角の坂を2回走るため見た目以上にタフ。リピーター注意。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "キズナ"], "fav_gate": "不問", "fav_style": "差し"},
    "京都芝3000": {"note": "【長距離】菊花賞。坂を2回超える。長距離スタミナと、坂下りで引っかからない折り合いのセンスが必須。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キタサンブラック"], "fav_gate": "内枠", "fav_style": "先行"},
    "京都芝3200": {"note": "【超長距離】天皇賞(春)。外回りを2周。淀の坂を2度超える過酷な3200m。騎手の絶妙なペース配分が不可欠。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ハーツクライ", "ゴールドシップ"], "fav_gate": "内枠", "fav_style": "先行"},
    "京都ダ1800": {"note": "主要ダート。急坂がないため好位につけられる器用さと最後の直線のスピード持続力必要。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "内枠", "fav_style": "先行"},
    
    # 阪神
    "阪神芝1200": {"note": "内回り. 急坂があるためパワー必要。荒れ馬場・重馬場になると一気にタフな消耗戦になり差し有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "内枠", "fav_style": "先行"},
    "阪神芝1600": {"note": "外回り。桜花賞など。直線が長く実力が反映されやすい。高速馬場なら瞬発力、道悪ならスタミナ。", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア"], "fav_gate": "不問", "fav_style": "差し"},
    "阪神芝2000": {"note": "内回り。大阪杯など。スタート直後に急坂あり先行落ち着く。内回り器用さとパワー必要。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "ドゥラメンテ"], "fav_gate": "内枠", "fav_style": "先行"},
    "阪神芝2200": {"note": "内回り。宝塚記念など。時計のかかる過酷な内回り。スタミナと持続力の消耗戦になりやすい。", "track": "芝", "dist": "中距離", "good_lineage": ["ステイゴールド系", "キズナ"], "fav_gate": "内枠", "fav_style": "差し"},
    "阪神芝3000": {"note": "【長距離】阪神大賞典。内回りを転戦し急坂を2回超えるタフなコース。バテないスタミナ型が有利。", "track": "芝", "dist": "長距離", "good_lineage": ["オルフェーヴル", "ディープインパクト系", "ハーツクライ"], "fav_gate": "不問", "fav_style": "先行"},
    "阪神ダ1800": {"note": "主要ダート。スタート直後に急坂。タフなスタミナ勝負になりやすくシニスターミニスター強力。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},

    # 中京
    "中京芝1200": {"note": "高松宮記念など。直線に急坂がありスピードだけでなくタフなパワーと差し脚が求められる。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "不問", "fav_style": "差し"},
    "中京芝2000": {"note": "金鯱賞など。スタート直後に坂がありスローになりやすい。インを立ち回れる先行が圧倒的有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "キズナ"], "fav_gate": "内枠", "fav_style": "先行"},
    "中京ダ1800": {"note": "チャンピオンズCなど。スタート直後に坂を超えるためイン前残り多発。外枠厳しい。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "内枠", "fav_style": "先行"},

    # 札幌
    "札幌芝1200": {"note": "オール洋芝。カーブが緩やかで直線が短いため内枠の逃げ・先行馬が圧倒的有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "札幌芝2000": {"note": "1コーナーまでが長い。1800mに比べペースが落ち着きやすく、インの立ち回り重視。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "キングカメハメハ系"], "fav_gate": "内枠", "fav_style": "先行"},
    "札幌ダ1700": {"note": "エルムSなど。1コーナーが近く先行争い激化. 基本前残りだがハイペースなら捲り決まる。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},

    # 函館
    "函館芝1200": {"note": "スタートから3角まで下り坂。超ハイペースになりやすいが直線短く前残り警戒。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "函館芝2000": {"note": "函館記念など。1コーナーまで十分距離あり。タフな洋芝の長丁場でスタミナが必要。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "オルフェーヴル"], "fav_gate": "不問", "fav_style": "先行"},
    "函館ダ1700": {"note": "小回りを4回。砂が深くタフ。泥を被りにくい外枠の先行馬が有利になりやすい。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "パイロ"], "fav_gate": "外枠", "fav_style": "先行"},

    # 福島
    "福島芝1200": {"note": "スタートから緩やかな下り。スパイラルカーブだが直線短く内枠先行馬が絶対有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ダイワメジャー", "ロードカナロア"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "福島芝2000": {"note": "福島記念など。直線長く枠順差は少ない。小回り平坦ながらラストの坂でタフな展開に。", "track": "芝", "dist": "中距離", "good_lineage": ["ステイゴールド系", "ハービンジャー"], "fav_gate": "不問", "fav_style": "先行"},
    "福島ダ1700": {"note": "1コーナーまでの距離が長く落ち着きやすい。基本先行だが3角からの捲りも届く。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},

    # 新潟
    "新潟芝1000": {"note": "日本唯一の直線1000m。外ラチ沿いを走れる「7枠・8枠」が圧倒的に有利。内枠は壊滅的。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "外枠", "fav_style": "逃げ"},
    "新潟芝2000": {"note": "外回り. 新潟記念など。最初の直線が極めて長い。紛れがなく純粋な実力瞬発力勝負。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "キングカメハメハ系"], "fav_gate": "不問", "fav_style": "差し"},
    "新潟ダ1800": {"note": "レパードSなど。1角までが長く枠順差は少ない。平坦でスピードが出やすく直線長い。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},

    # 小倉
    "小倉芝1200": {"note": "スタートから4角まで下り坂。超高速決着になりやすく内枠の逃げ先行が圧倒的有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ミッキーアイル"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "小倉芝2000": {"note": "小倉記念など。タフなスピード持続力勝負になりやすく機動力のある差し・捲り馬評価上げる。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハービンジャー"], "fav_gate": "不問", "fav_style": "差し"},
    "小倉ダ1700": {"note": "小回りを4回. 先行争い激化しやすい。外枠から被せる先行馬や3角捲り馬○。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "パイロ"], "fav_gate": "外枠", "fav_style": "先行"}
}

# ==========================================
# 🏇 2. 【画像準拠】新ジョッキー事典・大幅拡充マスター
# ==========================================
JOCKEY_MASTER = {
    # 栗東（関西）所属
    "C.ルメール": {"base": 1.30, "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": 0.05, "長距離": 0.10, "G1": 0.10}, "note": "G1・大舞台・長距離の信頼度は異次元。"},
    "川田将雅": {"base": 1.30, "factors": {"芝1枠": 0.15, "小回り2000": 0.15, "交流重賞": 0.15, "先行": 0.05, "ダート": 0.05}, "note": "圧倒的な勝率と先行意識の高さ。好位抜け出しの鬼。"},
    "坂井瑠星": {"base": 1.25, "factors": {"先行": -0.05, "内枠": 0.05, "外枠": -0.05, "ダート": 0.05, "海外": 0.15}, "note": "積極果敢な逃げ・先行が持ち味。ダートや前残りコースで強力。"},
    "武豊": {"base": 1.20, "factors": {"芝": 0.05, "継続騎乗": 0.15, "人気薄": 0.15, "距離延長": 0.10, "長距離": 0.15}, "note": "レジェンド。ペース配分と折り合い技術、長距離戦は神業レベル。"},
    "松山弘平": {"base": 1.15, "factors": {"ダート": 0.15, "新馬戦": 0.15, "前哨戦": 0.15, "荒れ馬場": 0.10}, "note": "タフな消耗戦や小回りのイン突きが得意。非常に堅実。"},
    "岩田望来": {"base": 1.10, "factors": {"マイル以下の差し": 0.15, "乗り替わり": 0.15}, "note": "若手トップ集団。中距離での立ち回りと勝負勘が非常に優秀。"},
    "西村淳也": {"base": 1.10, "factors": {"京都芝": 0.15, "ロードカナロア産駒": 0.15}, "note": "ローカルの帝王から中央主要場へ完全定着。抜群の勝負強さ。"},
    "団野大成": {"base": 1.10, "factors": {"短距離重賞": 0.15, "荒れ馬場": 0.15}, "note": "大舞台での進路取りが巧み。荒れ馬場での信頼度が高い。"},
    "鮫島克駿": {"base": 1.05, "factors": {"イン突き": 0.15, "中長距離": 0.15, "ダート外枠": 0.15}, "note": "人気薄を持ってくる穴の演出家。丁寧なイン突きが武器。"},
    "藤岡佑介": {"base": 1.10, "factors": {"自在性": 0.15, "妙味": 0.15, "重賞の人気馬": -0.15}, "note": "理論派。的確なペース判断で人気薄の先行粘り込みに注意。"},
    "幸英明": {"base": 1.05, "factors": {"ダート": 0.15, "牡馬のタフ条件": 0.15}, "note": "JRAきっての鉄人。ダート戦での堅実な先行・追い上げ能力。"},
    "池添謙一": {"base": 1.15, "factors": {"大舞台&重賞": 0.15, "差し&追い込み": 0.15}, "note": "グランプリ男。本番・大舞台での勝負強さと一発を狙う差し脚。"},
    "岩田康誠": {"base": 1.15, "factors": {"重賞": 0.15, "イン突き": 0.15}, "note": "代名詞「イン突き」。馬場が荒れても最内を割ってくるド根性。"},
    "M.デムーロ": {"base": 1.15, "factors": {"大舞台&重賞": 0.15, "マクリ追い込み": 0.15}, "note": "出遅れリスクあるが、大舞台の捲りは破壊力抜群。"},
    "浜中俊": {"base": 1.05, "factors": {"芝短〜中距離": 0.15, "1番人気": 0.15}, "note": "高速馬場の立ち回りが得意な実力派。"},
    "北村友一": {"base": 1.10, "factors": {"芝8枠": 0.15, "中長距離": 0.15}, "note": "阪神・京都の内回りや、ダート戦での堅実な仕掛けに定評。"},
    "横山典弘": {"base": 1.15, "factors": {"芝内枠": 0.15, "継続騎乗": 0.15, "馬ファースト": 0.15}, "note": "奇才。馬のポテンシャルを極限まで引き出す。"},
    "和田竜二": {"base": 1.05, "factors": {"タフな泥臭い展開": 0.15, "ズブい馬": 0.15}, "note": "剛腕。ズブいスタミナ馬を最後まで持たせる持久力戦の鬼。"},
    "永島まなみ": {"base": 1.05, "factors": {"ダート逃げ": 0.15, "ローカル先行": 0.10}, "note": "軽量を活かしたローカル・短距離での積極的な逃げ・先行策が武器。"},
    "田口貫太": {"base": 1.05, "factors": {"ダートの人気馬": 0.15, "重賞": 0.15, "芝1枠": 0.15}, "note": "抜群のセンスとハングリー精神で成長著しい若手のホープ。"},

    # 美浦（関東）所属
    "戸崎圭太": {"base": 1.20, "factors": {"前走ルメール": 0.15, "ダート外枠": 0.15, "東京1600": 0.15}, "note": "関東の安定軸。東京ダートや芝中距離の立ち回りが優秀。"},
    "横山武史": {"base": 1.20, "factors": {"中山重賞": 0.15, "持久力戦": 0.15, "マイネル": 0.15, "荒れ馬場": 0.10}, "note": "中山巧者。ガシガシ追える剛腕でタフな道悪馬場に滅法強い。"},
    "菅原明良": {"base": 1.10, "factors": {"東京直線": 0.15, "中長距離戦": 0.15}, "note": "関東の実力派。東京の長い直線で見せる追える脚が魅力。"},
    "三浦皇成": {"base": 1.10, "factors": {"2歳重賞": 0.10, "東京ダート": 0.15}, "note": "関東の中堅安定株。上位人気馬に跨った際の手堅さは健在。"},
    "津村明秀": {"base": 1.10, "factors": {"マイル重賞": 0.15, "先行": 0.10}, "note": "近年大舞台での激走が目立つガッツ溢れる粘り。"},
    "横山和生": {"base": 1.10, "factors": {"長距離逃げ": 0.15, "洋芝": 0.15, "逃げ": 0.10}, "note": "長距離スタミナ戦での逃げ・先行で無類の強さを発揮する。"},
    "北村宏司": {"base": 1.05, "factors": {"東京芝": 0.10, "マイル": 0.10}, "note": "ベテランの安定感。東京の長い直線やマイル戦での仕掛けが綺麗。"},
    "田辺裕信": {"base": 1.10, "factors": {"ポツン逃げ": 0.15, "中山ダート": 0.15}, "note": "意表を突くポツン逃げや好位差しなど、トリッキーな中山で穴。"},
    "丹内祐次": {"base": 1.10, "factors": {"北海道シリーズ": 0.20, "福島芝": 0.15}, "note": "ローカルの絶対王者。北海道シリーズ・福島ではリーディング常連。"},
    "吉田隼人": {"base": 1.10, "factors": {"洋芝マクリ": 0.15, "中京芝": 0.10}, "note": "インをロスなく立ち回る技術と強気な捲りが持ち味。"},
    "丸山元気": {"base": 1.05, "factors": {"裏開催": 0.10, "先行好位": 0.10}, "note": "裏開催での安定感抜群。中位人気の馬を好位へ導く。"},
    "佐々木大輔": {"base": 1.10, "factors": {"函館・札幌": 0.20, "減量特典": 0.10}, "note": "驚異的な成長力。特に北海道・洋芝の勝率はトップクラス。"},
    "武藤雅": {"base": 1.05, "factors": {"ダート粘り": 0.10, "ローカル": 0.10}, "note": "ダートでの粘り込み、差し込みに定評。ローカルでの打率高い。"},
    "石川裕紀人": {"base": 1.05, "factors": {"直線追い込み": 0.10, "穴激走": 0.15}, "note": "時旧見せる大物喰いの激走。直線が長いコースでの追い込み。"},
    "大野拓弥": {"base": 1.05, "factors": {"新潟ダート": 0.15, "直線差し": 0.10}, "note": "追い込み・直線の差し馬に乗せたら屈指。新潟・東京ダートの穴。"},
    "松岡正海": {"base": 1.05, "factors": {"中山マクリ": 0.15, "ウイン": 0.10}, "note": "中山巧者であり、馬場を読んだマクリ・先行策が持ち味。"}
}

# ☔ 道悪特効（重・不良馬場）種牡馬リスト
BAD_TRACK_SIRES = {
    "芝": ["キズナ", "ハービンジャー", "エピファネイア", "オルフェーヴル", "ゴールドシップ"],
    "ダート": ["シニスターミニスター", "ホッコータルマエ", "ヘニーヒューズ", "パイロ"]
}

# ==========================================
# 🗺️ 3. URLデータロード・デコードの処理
# ==========================================
query_params = st.query_params
loaded_data = {}

if "d" in query_params:
    try:
        encoded_json = query_params["d"]
        decoded_json = urllib.parse.unquote(encoded_json)
        loaded_data = json.loads(decoded_json)
        st.toast("🎉 URLからデータを自動で復元しました！")
    except Exception as e:
        st.error(f"URLデータの復元に失敗しました: {e}")

# ==========================================
# 💻 4. アプリケーション メイン UI
# ==========================================
st.title("🎯 ジェニー予想完全版 ver1.20")
st.caption("【最新ジョッキー倍率ロジック×URLセーブ完全融合モデル】")

st.write("---")

# 📍 1. 基本環境設定
st.header("📍 レース基本環境")
col_cfg1, col_cfg2, col_cfg3 = st.columns(3)

with col_cfg1:
    default_venue = loaded_data.get("venue", "東京")
    venue_list = ["東京", "中山", "京都", "阪神", "中京", "新潟", "福島", "小倉", "函館", "札幌"]
    venue_idx = venue_list.index(default_venue) if default_venue in venue_list else 0
    venue = st.selectbox("競馬場選択", venue_list, index=venue_idx)

with col_cfg2:
    valid_courses = [k for k in COURSE_MASTER.keys() if k.startswith(venue)]
    default_course = loaded_data.get("course_key", "")
    course_idx = valid_courses.index(default_course) if default_course in valid_courses else 0
    course_key = st.selectbox("コース選択", valid_courses if valid_courses else ["該当なし"], index=course_idx)

with col_cfg3:
    default_condition = loaded_data.get("condition", "良")
    cond_list = ["良", "稍重", "重", "不良"]
    cond_idx = cond_list.index(default_condition) if default_condition in cond_list else 0
    condition = st.selectbox("馬場状態", cond_list, index=cond_idx)
    is_bad_track = condition in ["重", "不良"]

# コース情報のサマリー自動表示
if course_key in COURSE_MASTER:
    course_data = COURSE_MASTER[course_key]
    st.info(f"🧭 **【{course_key} コース特徴】** 枠順傾向: **{course_data['fav_gate']}** / 有利脚質: **{course_data['fav_style']}**\n\n{course_data['note']}")
else:
    st.error("⚠️ 有効なコースを選択してください。")
    st.stop()

# ------------------------------------------
# 📱 2. 出走馬一括データ入力
# ------------------------------------------
st.write("---")
st.header("📝 出走馬データ一括入力")

default_num_horses = int(loaded_data.get("num_horses", 12))
num_horses = st.number_input("出頭数", min_value=2, max_value=18, value=default_num_horses, step=1)

col_left, col_right = st.columns([8.0, 4.0])

with col_left:
    horse_inputs = []
    
    with st.form(key="jenny_input_form"):
        jock_list = sorted(list(JOCKEY_MASTER.keys()))
        jock_options = ["(その他/手入力する)"] + jock_list
        sample_sires = ["キタサンブラック", "ゴールドシップ", "エピファネイア", "ハーツクライ", "オルフェーヴル", "ルーラーシップ"]
        
        plus_options = {"なし": 0, "＋1 (好気配)": 1, "＋2 (馬体増減理想)": 2, "＋3 (パドック抜群)": 3, "＋5 (究極のメイチ)": 5}
        minus_options = {"なし": 0, "ー1 (チャカつき)": -1, "ー2 (大幅馬体重増減)": -2, "ー3 (入れ込み酷い)": -3, "ー5 (デキ落ち)": -5}
        
        loaded_horses = loaded_data.get("horses", [])
        
        for i in range(int(num_horses)):
            gate = i + 1
            st.markdown(f"##### 🐴 馬番 {gate:02d}")
            
            saved_h = next((h for h in loaded_horses if h["gate"] == gate), {})
            
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 0.9, 0.9, 1.3, 1.6, 2.0, 2.0])
            
            with c1:
                val_name = saved_h.get("name", f"競走馬{gate}")
                h_name = st.text_input("馬名", value=val_name, key=f"form_name_{gate}")
            with c2:
                val_idx = saved_h.get("idx", 75)
                h_idx = st.number_input("能力値", min_value=0, max_value=200, value=val_idx, key=f"form_idx_{gate}")
            with c3:
                val_pop = saved_h.get("pop", ((i % 12) + 1))
                h_pop = st.number_input("人気", min_value=1, max_value=18, value=val_pop, key=f"form_pop_{gate}")
            with c4:
                val_f3f = saved_h.get("f3f", 34.2)
                h_f3f = st.number_input("最速上がり", min_value=30.0, max_value=45.0, value=val_f3f, step=0.1, format="%.1f", key=f"form_f3f_{gate}")
            with c5:
                val_sire = saved_h.get("sire", sample_sires[i % len(sample_sires)])
                h_sire = st.text_input("父(種牡馬)", value=val_sire, key=f"form_sire_{gate}")
            with c6:
                val_j_sel = saved_h.get("j_sel", "")
                default_idx = jock_options.index(val_j_sel) if val_j_sel in jock_options else ((i % len(jock_list)) + 1 if (i % len(jock_list)) + 1 < len(jock_options) else 1)
                selected_jock = st.selectbox("想定騎手", jock_options, index=default_idx, key=f"form_j_sel_{gate}")
                
                if selected_jock == "(その他/手入力する)":
                    val_j_txt = saved_h.get("jockey", "柴田善臣")
                    final_jockey = st.text_input("✍️ 騎手手入力", value=val_j_txt, key=f"form_j_txt_{gate}")
                else:
                    final_jockey = selected_jock
            
            with c7:
                val_plus = saved_h.get("plus_label", "なし")
                p_idx = list(plus_options.keys()).index(val_plus) if val_plus in plus_options else 0
                p_label = st.selectbox("➕ プラス項目", list(plus_options.keys()), index=p_idx, key=f"form_plus_{gate}")
                
                val_minus = saved_h.get("minus_label", "なし")
                m_idx = list(minus_options.keys()).index(val_minus) if val_minus in minus_options else 0
                m_label = st.selectbox("➖ マイナス項目", list(minus_options.keys()), index=m_idx, key=f"form_minus_{gate}")
                
                manual_adjustment = plus_options[p_label] + minus_options[m_label]
                    
            horse_inputs.append({
                "gate": gate, "name": h_name, "idx": h_idx, "pop": h_pop, "f3f": h_f3f, 
                "sire": h_sire, "jockey": final_jockey, "j_sel": selected_jock,
                "plus_label": p_label, "minus_label": m_label, "manual_adj": manual_adjustment
            })
            
        submit_button = st.form_submit_button(label="🚀 ジェニー予想を実行（最終解析）", use_container_width=True)

    # ------------------------------------------
    # 🔗 URLデータ生成セクション
    # ------------------------------------------
    st.write("---")
    st.markdown("### 🔗 この入力状態を保存するURLを発行")
    
    if st.button("🌐 保存用URLを生成する", use_container_width=True):
        current_state = {
            "venue": venue, "course_key": course_key, "condition": condition,
            "num_horses": num_horses, "horses": horse_inputs
        }
        json_str = json.dumps(current_state, ensure_ascii=False)
        encoded_data = urllib.parse.quote(json_str)
        share_url = f"https://share.streamlit.io/ (あなたのアプリのURL)/?d={encoded_data}"
        
        st.success("🎉 保存用URLが生成されました！")
        st.text_area("📋 コピペ用URL", value=share_url, height=100)

# ==========================================
# 🧮 5. 画像ロジック準拠：解析計算コア
# ==========================================
with col_right:
    st.header("🏆 最終解析結果")
    
    if submit_button or "d" in query_params:
        scored_output = []

        for h in horse_inputs:
            # 1. 基本スコア
            score = float(h["idx"])
            calc_log = []
            
            # 2. 人気補正
            if h["pop"] == 1: score += 4.0
            elif h["pop"] == 2: score += 2.0
            elif h["pop"] > 5: score -= (h["pop"] - 5) * 1.0
            
            # 3. 上がり時計補正
            if course_data.get("dist") == "長距離":
                if h["f3f"] <= 34.2: score += 12.0
                elif h["f3f"] <= 35.0: score += 7.0
                elif h["f3f"] >= 36.5: score -= 4.0
            else:
                if h["f3f"] <= 33.8: score += 10.0
                elif h["f3f"] <= 34.5: score += 5.0
            
            # 4. 血統補正
            if h["sire"] in course_data["good_lineage"]:
                score += 6.0 if course_data.get("dist") == "長距離" else 5.0
            if is_bad_track:
                if h["sire"] in BAD_TRACK_SIRES.get(course_data["track"], []):
                    score += 8.0
            
            # 5. 【画像完全準拠】ジョッキー倍率計算
            jockey_name = h["jockey"].strip()
            if jockey_name in JOCKEY_MASTER:
                j_data = JOCKEY_MASTER[jockey_name]
                j_base = j_data["base"]
                factor_sum = 0.0
                
                # 詳細ファクター自動判定
                # 芝/ダート
                if course_data["track"] == "芝" and "芝" in j_data["factors"]:
                    factor_sum += j_data["factors"]["芝"]
                if course_data["track"] == "ダート" and "ダート" in j_data["factors"]:
                    factor_sum += j_data["factors"]["ダート"]
                
                # 長距離
                if course_data.get("dist") == "長距離" and "長距離" in j_data["factors"]:
                    factor_sum += j_data["factors"]["長距離"]
                
                # 会場特化 (北海道シリーズ/京都芝など)
                if venue in ["函館", "札幌"] and "北海道シリーズ" in j_data["factors"]:
                    factor_sum += j_data["factors"]["北海道シリーズ"]
                if venue in ["函館", "札幌"] and "函館・札幌" in j_data["factors"]:
                    factor_sum += j_data["factors"]["函館・札幌"]
                if venue == "京都" and course_data["track"] == "芝" and "京都芝" in j_data["factors"]:
                    factor_sum += j_data["factors"]["京都芝"]
                if venue == "福島" and course_data["track"] == "芝" and "福島芝" in j_data["factors"]:
                    factor_sum += j_data["factors"]["福島芝"]
                if venue == "東京" and "東京直線" in j_data["factors"]:
                    factor_sum += j_data["factors"]["東京直線"]
                if venue == "中山" and is_bad_track == False and "中山ダート" in j_data["factors"]:
                    factor_sum += j_data["factors"]["中山ダート"]

                # 荒れ馬場・タフ馬場判定
                if is_bad_track and "荒れ馬場" in j_data["factors"]:
                    factor_sum += j_data["factors"]["荒れ馬場"]
                if is_bad_track and "タフな泥臭い展開" in j_data["factors"]:
                    factor_sum += j_data["factors"]["タフな泥臭い展開"]
                
                # 枠・脚質による簡易連動判定
                if h["gate"] <= 3 and "内枠" in j_data["factors"]:
                    factor_sum += j_data["factors"]["内枠"]
                if h["gate"] >= 14 and "外枠" in j_data["factors"]:
                    factor_sum += j_data["factors"]["外枠"]
                if course_data["fav_style"] == "先行" and "先行" in j_data["factors"]:
                    factor_sum += j_data["factors"]["先行"]
                if course_data["fav_style"] == "差し" and "差し" in j_data["factors"]:
                    factor_sum += j_data["factors"]["差し"]

                # 最終倍率の決定
                final_multiplier = j_base + factor_sum
                score *= final_multiplier
                calc_log.append(f"騎手倍率: {final_multiplier:.2f}倍 (基本 {j_base} + 補正 {factor_sum:+.2f})")
            else:
                # 事典外の一律補正
                score *= 1.05
                calc_log.append("騎手倍率: 1.05倍 (事典外一律)")
                
            # 6. パドック直前手動補正 (倍率計算の後に加減算)
            score += h["manual_adj"]
            if h["manual_adj"] != 0:
                calc_log.append(f"直前補正: {h['manual_adj']:+f}pt")
                    
            scored_output.append({
                "gate": h["gate"], "name": h["name"], "pop": h["pop"],
                "jockey": jockey_name, "score": score, "log": " / ".join(calc_log)
            })
            
        # スコア順にソート
        scored_output.sort(key=lambda x: x["score"], reverse=True)
        
        # 結果テーブル表示
        marks = ["◎", "○", "▲", "△", "☆"]
        result_rows = []
        for idx, h in enumerate(scored_output):
            mark = marks[idx] if idx < len(marks) else " "
            result_rows.append({
                "印": mark, "馬番": f"{h['gate']:02d}", "馬名": h["name"],
                "人気": f"{h['pop']}人", "総合スコア": f"{h['score']:.1f} pt"
            })
            
        st.dataframe(pd.DataFrame(result_rows), use_container_width=True, hide_index=True)
        
        st.write("---")
        st.subheader("💡 上位馬の計算根拠")
        for i in range(min(3, len(scored_output))):
            h = scored_output[i]
            st.markdown(f"**【{marks[i]}】 {h['name']}（{h['gate']}番）**")
            st.caption(f"鞍上: {h['jockey']} | 算出ログ: {h['log']}")
            
    else:
        st.info("👈 左側に入力、またはURLから復元したのち、中央の『予想を実行』ボタンを押してください。")
