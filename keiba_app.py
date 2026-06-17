import streamlit as st
import pandas as pd
import urllib.parse
import json

# ページ全体の基本設定
st.set_page_config(page_title="ジェニー予想完全版 ver1.40", layout="wide")

# ==========================================
# 🗺️ 1. コース完全マスター（以前のディープな解説と完全融合）
# ==========================================
COURSE_MASTER = {
    # --- 以前のアプリから完全融合・復元したコース群 ---
    "東京芝1600": {
        "note": "2月内枠、2月以外外枠。同距離＆距離短縮馬、重賞は差し・追い込み有利。ロードカナロア/エピファネイア/モーリス/キズナ/ハーツクライ。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス", "キズナ", "ハーツクライ"], "fav_gate": "時期による", "fav_style": "差し"},
    "東京芝2000": {
        "note": "1枠有利。前走同距離＆距離短縮が好走。エピファネイア/モーリス牡馬/キズナ/ハーツクライ/ロードカナロア。オークスは差し・追い込み。ジャパンカップはダービー・オークス3着以内の3歳。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "モーリス", "キズナ", "ハーツクライ", "ロードカナロア"], "fav_gate": "1枠絶対", "fav_style": "先行・差し"},
    "東京芝2400": {
        "note": "オークスは差し・追い込み。ジャパンカップはダービー・オークス3着以内の3歳馬有利。極端な有利不利はないがインをロスなく回れる内〜中枠有利。", 
        "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ドゥラメンテ", "ディープインパクト系"], "fav_gate": "内〜中枠", "fav_style": "差し"},
    "東京ダート1600": {
        "note": "外枠有利。前走同距離＆距離短縮馬。ヘニーヒューズ/ドレフォン(逃げ先行有利)。フェブラリーSなどマイル以上のスタミナとパワー必須。", 
        "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "シニスターミニスター"], "fav_gate": "外枠", "fav_style": "先行"},
    "中山芝1200": {
        "note": "ファインニードル産駒○、アメリカンペイトリオット産駒○。4角まで下り坂。スピードの持続力と最後の急坂を耐えるパワーが必要。内枠有利。", 
        "track": "芝", "dist": "短距離", "good_lineage": ["ファインニードル", "アメリカンペイトリオット", "ロードカナロア"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "中山芝2000": {
        "note": "皐月賞はマイル〜1800m重賞実績馬○。荒れ馬場は外差し○。エピファネイア牡馬/キズナ/ドゥラメンテ/モーリス/ロードカナロア。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "キズナ", "ドゥラメンテ", "モーリス", "ロードカナロア"], "fav_gate": "馬場による", "fav_style": "先行"},
    "中山芝2500": {
        "note": "高速馬場の有馬記念は東京中距離G1実績馬○。高速馬場は内枠、荒れ馬場は外枠有利。エピファネイア/キズナ/ブラックタイド/ゴールドシップ。", 
        "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キズナ", "ブラックタイド", "ゴールドシップ"], "fav_gate": "馬場による", "fav_style": "先行"},
    "中京芝1200": {
        "note": "内枠、距離短縮馬の内枠、内枠の逃げ先行馬○。ロードカナロア/ビッグアーサー/ミッキーアイル/ダイワメジャー/ドレフォン。", 
        "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー", "ミッキーアイル", "ダイワメジャー", "ドレフォン"], "fav_gate": "内枠", "fav_style": "逃げ先行"},
    "中京ダート1800": {
        "note": "内をロスなく立ち回れる逃げ先行馬○。時計がかかると外差し○。チャンピオンズCなどスタート直後に坂を超えるため内枠有利。", 
        "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "内枠", "fav_style": "逃げ先行"},
    "京都芝1600(外)": {
        "note": "同距離＆距離短縮馬。高速馬場は上がり時計重視○。荒れ馬場は外枠有利(キズナ/エピファネイア/ロードカナロア/モーリス)。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "エピファネイア", "ロードカナロア", "モーリス"], "fav_gate": "馬場による", "fav_style": "差し"},
    "京都芝2000": {
        "note": "上級条件は差し馬○。秋華賞は差し馬・オークス出走馬が狙い目。キズナ/キタサンブラック/エピファネイア/ドゥラメンテ/モーリス。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "キタサンブラック", "エピファネイア", "ドゥラメンテ", "モーリス"], "fav_gate": "内枠", "fav_style": "差し"},
    "京都芝2200": {
        "note": "馬場良好なら内枠○。エリザベス女王杯も内枠有利。キズナ/サトノダイヤモンド/ハービンジャー/ルーラーシップ/ノヴェリスト。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "サトノダイヤモンド", "ハービンジャー", "ルーラーシップ", "ノヴェリスト"], "fav_gate": "内枠", "fav_style": "差し"},
    "京都芝3000": {
        "note": "外枠有利。父または母父ステイゴールド系○。小柄なエピファネイア/ゴールドシップ/ドゥラメンテ/サトノダイヤモンド/ディープ系。", 
        "track": "芝", "dist": "長距離", "good_lineage": ["ステイゴールド系", "エピファネイア", "ゴールドシップ", "ドゥラメンテ", "サトノダイヤモンド"], "fav_gate": "外枠", "fav_style": "先行"},
    "京都芝3200": {
        "note": "人気馬○。父または母父ステイゴールド系○。前走阪神大賞典で上がり最速の馬○。騎手の絶妙なペース配分が不可欠。", 
        "track": "芝", "dist": "長距離", "good_lineage": ["ステイゴールド系", "キタサンブラック", "ハーツクライ"], "fav_gate": "内枠", "fav_style": "先行"},
    "阪神芝1600": {
        "note": "内枠有利。高速馬場は外差し、同距離＆距離短縮馬○。ロードカナロア/エピファネイア/モーリス/キズナ/ハーツクライ。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス", "キズナ", "ハーツクライ"], "fav_gate": "内枠", "fav_style": "差し"},
    "阪神芝2000": {
        "note": "外枠の先行馬有利。大阪杯は内差し。ドゥラメンテ牡馬/ルーラーシップ/キズナ/エピファネイア/ハーツクライ/ロードカナロア。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["ドゥラメンテ", "ルーラーシップ", "キズナ", "エピファネイア", "ハーツクライ", "ロードカナロア"], "fav_gate": "外枠", "fav_style": "先行"},
    "阪神芝2200": {
        "note": "先行〜中団差し馬○。キズナ/ルーラーシップ/イスラボニータ/キタサンブラック/エピファネイア/ドゥラメンテ。", 
        "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "ルーラーシップ", "イスラボニータ", "キタサンブラック", "エピファネイア", "ドゥラメンテ"], "fav_gate": "内枠", "fav_style": "差し"},

    # --- 補完用：その他の主要コース（最新マスターから維持） ---
    "東京芝1400": {"note": "3角までの直線が長く枠順差は少ない。短距離のスピードとマイルを乗り切るスタミナのバランス。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "不問", "fav_style": "先行"},
    "東京芝1800": {"note": "スタート後すぐに2角のカーブがあるため内枠有利。キレ味が最重要視される。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ"], "fav_gate": "内枠", "fav_style": "差し"},
    "東京芝2500": {"note": "坂の途中からのスタートでスタミナ要求値が高い。タフに伸びるスタミナ血統向き。", "track": "芝", "dist": "長距離", "good_lineage": ["ハーツクライ", "ルーラーシップ"], "fav_gate": "不問", "fav_style": "差し"},
    "東京芝3400": {"note": "向正面スタートからスタミナの絶対量が問われる。極限の折り合いと心肺機能が必要。", "track": "芝", "dist": "長距離", "good_lineage": ["ハーツクライ", "オルフェーヴル"], "fav_gate": "内枠", "fav_style": "差し"},
    "東京ダ1400": {"note": "芝スタート。外枠に行くほど芝を長く走れるため外枠のスピード馬が圧倒的有利。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "ロードカナロア"], "fav_gate": "外枠", "fav_style": "先行"},
    "東京ダ2100": {"note": "直線が長くダートとしては屈指のスタミナが必要。スタミナ型の差し馬やスタミナ血統が台頭。", "track": "ダート", "dist": "長距離", "good_lineage": ["シニスターミニスター", "キングカメハメハ"], "fav_gate": "不問", "fav_style": "差し"},
    "中山芝1600": {"note": "外回り。スタートが1角ポケットにあり外枠は壊滅的不利。1〜3枠絶対有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ダイワメジャー", "モーリス"], "fav_gate": "内枠", "fav_style": "先行"},
    "中山芝1800": {"note": "内回り。1角が近いため先行争い激化。タフな小回り適性と急坂での加速力が必要。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ"], "fav_gate": "内枠", "fav_style": "先行"},
    "中山芝2200": {"note": "外回りから内回りへ合流するトリッキーな構成。スタミナと持続力血統が強い。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "ルーラーシップ"], "fav_gate": "不問", "fav_style": "差し"},
    "中山芝3600": {"note": "内回りを3周、急坂を3回超えるJRA最長コース。純粋なスタミナと折り合い重視。", "track": "芝", "dist": "長距離", "good_lineage": ["ゴールドシップ", "オルフェーヴル"], "fav_gate": "不問", "fav_style": "先行"},
    "中山ダ1200": {"note": "芝スタートで外枠有利。テンのスピードが速く前残りしやすい。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス"], "fav_gate": "外枠", "fav_style": "逃げ"},
    "中山ダ1800": {"note": "非常にタフな急坂がありスタミナ必要。基本先行有利。", "track": "ダート", "dist": "中距離", "good_lineage": ["ホッコータルマエ", "シニスターミニスター"], "fav_gate": "不問", "fav_style": "先行"},
    "京都芝1200": {"note": "内回り。3角の坂を下るため高速スピードの持続力必要。基本は内枠の先行馬有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー"], "fav_gate": "内枠", "fav_style": "先行"},
    "京都芝1800": {"note": "外回り。スピードとキレ味の要求値が非常に高い。直線瞬発力勝負。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ"], "fav_gate": "不問", "fav_style": "差し"},
    "京都ダ1800": {"note": "主要ダート。急坂がないため好位につけられる器用さと最後の直線のスピード持続力必要。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "内枠", "fav_style": "先行"},
    "阪神芝1200": {"note": "内回り。急坂があるためパワー必要。タフな消耗戦になりやすい。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "内枠", "fav_style": "先行"},
    "阪神芝3000": {"note": "内回りを転戦し急坂を2回超えるタフなコース。バテないスタミナ型が有利。", "track": "芝", "dist": "長距離", "good_lineage": ["オルフェーヴル", "ディープインパクト系"], "fav_gate": "不問", "fav_style": "先行"},
    "阪神ダ1800": {"note": "主要ダート。スタート直後に急坂。タフなスタミナ勝負になりやすい。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},
    "中京芝2000": {"note": "スタート直後に坂がありスローになりやすい。インを立ち回れる先行が圧倒的有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "キズナ"], "fav_gate": "内枠", "fav_style": "先行"},
    "札幌芝1200": {"note": "オール洋芝。カーブが緩やかで直線が短いため内枠の逃げ・先行馬が圧倒的有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "札幌芝2000": {"note": "1コーナーまでが長い。1800mに比べペースが落ち着きやすく、インの立ち回り重視。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "キングカメハメハ系"], "fav_gate": "内枠", "fav_style": "先行"},
    "札幌ダ1700": {"note": "1コーナーが近く先行争い激化。基本前残りだがハイペースなら捲り決まる。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},
    "函館芝1200": {"note": "スタートから3角まで下り坂。超ハイペースになりやすいが直線短く前残り警戒。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "函館芝2000": {"note": "1コーナーまで十分距離あり。タフな洋芝の長丁場でスタミナが必要。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "オルフェーヴル"], "fav_gate": "不問", "fav_style": "先行"},
    "函館ダ1700": {"note": "小回りを4回。砂が深くタフ。泥を被りにくい外枠の先行馬が有利になりやすい。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "パイロ"], "fav_gate": "外枠", "fav_style": "先行"},
    "福島芝1200": {"note": "スタートから緩やかな下り。スパイラルカーブだが直線短く内枠先行馬が絶対有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ダイワメジャー", "ロードカナロア"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "福島芝2000": {"note": "直線長く枠順差は少ない。小回り平坦ながらラストの坂でタフな展開に。", "track": "芝", "dist": "中距離", "good_lineage": ["ステイゴールド系", "ハービンジャー"], "fav_gate": "不問", "fav_style": "先行"},
    "福島ダ1700": {"note": "1コーナーまでの距離が長く落ち着きやすい。基本先行だが3角からの捲りも届く。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},
    "新潟芝1000": {"note": "日本唯一の直線1000m。外ラチ沿いを走れる「7枠・8枠」が圧倒的に有利。内枠は壊滅的。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー"], "fav_gate": "外枠", "fav_style": "逃げ"},
    "新潟芝2000": {"note": "外回り。最初の直線が極めて長い。紛れがなく純粋な実力瞬発力勝負。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "キングカメハメハ系"], "fav_gate": "不問", "fav_style": "差し"},
    "新潟ダ1800": {"note": "1角までが長く枠順差は少ない。平坦でスピードが出やすく直線長い。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ"], "fav_gate": "不問", "fav_style": "先行"},
    "小倉芝1200": {"note": "スタートから4角まで下り坂。超高速決着になりやすく内枠の逃げ先行が圧倒的有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ミッキーアイル"], "fav_gate": "内枠", "fav_style": "逃げ"},
    "小倉芝2000": {"note": "タフなスピード持続力勝負になりやすく機動力のある差し・捲り馬評価上げる。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハービンジャー"], "fav_gate": "不問", "fav_style": "差し"},
    "小倉ダ1700": {"note": "小回りを4回。先行争い激化しやすい。外枠から被せる先行馬や3角捲り馬○。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "パイロ"], "fav_gate": "外枠", "fav_style": "先行"}
}

# ==========================================
# 🏇 2. 新ジョッキー事典データ＆全ファクターマスタ
# ==========================================
JOCKEY_MASTER = {
    "C.ルメール": {"base": 1.30, "factors": {"芝": 0.05, "ダート": -0.05, "差し": 0.05, "内枠": 0.05, "長距離": 0.10, "G1": 0.10}, "note": "G1・大舞台・長距離の信頼度は異次元。"},
    "川田将雅": {"base": 1.30, "factors": {"芝1枠": 0.15, "小回り2000": 0.15, "交流重賞": 0.15, "先行": 0.05, "ダート": 0.05}, "note": "圧倒的な勝率と先行意識の高さ。好位抜け出しの鬼。"},
    "坂井瑠星": {"base": 1.25, "factors": {"先行": 0.05, "内枠": 0.05, "外枠": -0.05, "ダート": 0.05, "海外": 0.15}, "note": "積極果敢な逃げ・先行が持ち味。ダートや前残りコースで強力。"},
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
    "石川裕紀人": {"base": 1.05, "factors": {"直線追い込み": 0.10, "穴激走": 0.15}, "note": "時折見せる大物喰いの激走。直線が長いコースでの追い込み。"},
    "大野拓弥": {"base": 1.05, "factors": {"新潟ダート": 0.15, "直線差し": 0.10}, "note": "追い込み・直線の差し馬に乗せたら屈指。新潟・東京ダートの穴。"},
    "松岡正海": {"base": 1.05, "factors": {"中山マクリ": 0.15, "ウイン": 0.10}, "note": "中山巧者であり、馬場を読んだマクリ・先行策が持ち味。"}
}

# 全ジョッキーのファクターを寄せ集めたマスタリスト
ALL_JOCKEY_FACTORS = {
    "なし": 0.0,
    "芝 (+0.05)": 0.05, "芝1枠 (+0.15)": 0.15, "芝内枠 (+0.15)": 0.15, "芝8枠 (+0.15)": 0.15, "芝短〜中距離 (+0.15)": 0.15, "京都芝 (+0.15)": 0.15, "福島芝 (+0.15)": 0.15, "東京芝 (+0.10)": 0.10, "中京芝 (+0.10)": 0.10,
    "ダート (+0.05)": 0.05, "ダート (+0.15)": 0.15, "ダート逃げ (+0.15)": 0.15, "ダート外枠 (+0.15)": 0.15, "ダートの人気馬 (+0.15)": 0.15, "中山ダート (+0.15)": 0.15, "東京ダート (+0.15)": 0.15, "新潟ダート (+0.15)": 0.15, "ダート粘り (+0.10)": 0.10, "ダート (-0.05)": -0.05,
    "逃げ (+0.10)": 0.10, "先行 (+0.05)": 0.05, "先行好位 (+0.10)": 0.10, "先行 (-0.05)": -0.05, "差し (+0.05)": 0.05, "マイル以下の差し (+0.15)": 0.15, "差し&追い込み (+0.15)": 0.15, "マクリ追い込み (+0.15)": 0.15, "直線差し (+0.10)": 0.10, "直線追い込み (+0.10)": 0.10,
    "内枠 (+0.05)": 0.05, "イン突き (+0.15)": 0.15, "外枠 (-0.05)": -0.05,
    "長距離 (+0.10)": 0.10, "長距離 (+0.15)": 0.15, "中長距離 (+0.15)": 0.15, "中長距離戦 (+0.15)": 0.15, "マイル重賞 (+0.15)": 0.15, "マイル (+0.10)": 0.10, "東京1600 (+0.15)": 0.15, "小回り2000 (+0.15)": 0.15, "距離延長 (+0.10)": 0.10, "長距離逃げ (+0.15)": 0.15,
    "G1 (+0.10)": 0.10, "重賞 (+0.15)": 0.15, "大舞台&重賞 (+0.15)": 0.15, "短距離重賞 (+0.15)": 0.15, "交流重賞 (+0.15)": 0.15, "2歳重賞 (+0.10)": 0.10, "中山重賞 (+0.15)": 0.15, "重賞の人気馬 (-0.15)": -0.15,
    "荒れ馬場 (+0.10)": 0.10, "荒れ馬場 (+0.15)": 0.15, "タフな泥臭い展開 (+0.15)": 0.15, "牡馬のタフ条件 (+0.15)": 0.15, "持久力戦 (+0.15)": 0.15,
    "継続騎乗 (+0.15)": 0.15, "乗り替わり (+0.15)": 0.15, "前走ルメール (+0.15)": 0.15, "1番人気 (+0.15)": 0.15, "人気薄 (+0.15)": 0.15, "自在性 (+0.15)": 0.15, "妙味 (+0.15)": 0.15, "新馬戦 (+0.15)": 0.15, "前哨戦 (+0.15)": 0.15, "海外 (+0.15)": 0.15, "馬ファースト (+0.15)": 0.15, "ズブい馬 (+0.15)": 0.15, "ポツン逃げ (+0.15)": 0.15, "穴激走 (+0.15)": 0.15, "中山マクリ (+0.15)": 0.15,
    "北海道シリーズ (+0.20)": 0.20, "函館・札幌 (+0.20)": 0.20, "洋芝 (+0.15)": 0.15, "洋芝マクリ (+0.15)": 0.15, "ローカル先行 (+0.10)": 0.10, "ローカル (+0.10)": 0.10, "裏開催 (+0.10)": 0.10,
    "ロードカナロア産駒 (+0.15)": 0.15, "マイネル (+0.15)": 0.15, "ウイン (+0.10)": 0.10, "減量特典 (+0.10)": 0.10
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
st.title("🎯 ジェニー予想完全版 ver1.40")
st.caption("【旧コース事典完全融合 ＆ ジョッキー別Wプルダウン搭載】")

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
    st.info(f"🧭 **【{course_key} コース特徴・血統事典】**\n\n{course_data['note']}")
else:
    st.error("⚠️ 有効なコースを選択してください。")
    st.stop()

# ------------------------------------------
# 📱 2. 出走馬データ入力（フォーム）
# ------------------------------------------
st.write("---")
st.header("📝 出走馬データ一括入力")

default_num_horses = int(loaded_data.get("num_horses", 12))
num_horses = st.number_input("出頭数", min_value=2, max_value=18, value=default_num_horses, step=1)

col_left, col_right = st.columns([8.5, 3.5])

with col_left:
    horse_inputs = []
    
    with st.form(key="jenny_input_form_v14"):
        jock_list = sorted(list(JOCKEY_MASTER.keys()))
        jock_options = ["(その他/手入力する)"] + jock_list
        sample_sires = ["キタサンブラック", "ゴールドシップ", "エピファネイア", "ハーツクライ", "オルフェーヴル", "ルーラーシップ"]
        
        # パドック補正用オプション
        plus_options = {"なし": 0, "＋1 (好気配)": 1, "＋2 (馬体増減理想)": 2, "＋3 (パドック抜群)": 3, "＋5 (究極のメイチ)": 5}
        minus_options = {"なし": 0, "ー1 (チャカつき)": -1, "ー2 (大幅馬体重増減)": -2, "ー3 (入れ込み酷い)": -3, "ー5 (デキ落ち)": -5}
        
        # 全ファクターのプルダウン用リスト
        all_factor_labels = list(ALL_JOCKEY_FACTORS.keys())
        
        loaded_horses = loaded_data.get("horses", [])
        
        for i in range(int(num_horses)):
            gate = i + 1
            st.markdown(f"##### 🐴 馬番 {gate:02d}")
            
            saved_h = next((h for h in loaded_horses if h["gate"] == gate), {})
            
            # --- 1段目: 基本情報入力 ---
            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 0.9, 0.9, 1.3, 1.6, 2.5])
            
            with c1:
                val_name = saved_h.get("name", f"競走馬{gate}")
                h_name = st.text_input("馬名", value=val_name, key=f"v4_name_{gate}")
            with c2:
                val_idx = saved_h.get("idx", 75)
                h_idx = st.number_input("能力値", min_value=0, max_value=200, value=val_idx, key=f"v4_idx_{gate}")
            with c3:
                val_pop = saved_h.get("pop", ((i % 12) + 1))
                h_pop = st.number_input("人気", min_value=1, max_value=18, value=val_pop, key=f"v4_pop_{gate}")
            with c4:
                val_f3f = saved_h.get("f3f", 34.2)
                h_f3f = st.number_input("最速上がり", min_value=30.0, max_value=45.0, value=val_f3f, step=0.1, format="%.1f", key=f"v4_f3f_{gate}")
            with c5:
                val_sire = saved_h.get("sire", sample_sires[i % len(sample_sires)])
                h_sire = st.text_input("父(種牡馬)", value=val_sire, key=f"v4_sire_{gate}")
            with c6:
                val_j_sel = saved_h.get("j_sel", "")
                default_j_idx = jock_options.index(val_j_sel) if val_j_sel in jock_options else ((i % len(jock_list)) + 1 if (i % len(jock_list)) + 1 < len(jock_options) else 1)
                selected_jock = st.selectbox("想定騎手", jock_options, index=default_j_idx, key=f"v4_jsel_{gate}")
                
                if selected_jock == "(その他/手入力する)":
                    val_j_txt = saved_h.get("jockey", "柴田善臣")
                    final_jockey = st.text_input("✍️ 騎手名手入力", value=val_j_txt, key=f"v4_jtxt_{gate}")
                else:
                    final_jockey = selected_jock

            # --- 2段目: 騎手特性ファクター ＆ 直前パドック補正 ---
            c_jp1, c_jp2, c_jm1, c_jm2, c_pl, c_mi = st.columns([1.8, 1.8, 1.8, 1.8, 1.8, 1.8])
            
            j_hints = []
            if final_jockey in JOCKEY_MASTER:
                j_hints = [f"{k} ({v:+.2f})" for k, v in JOCKEY_MASTER[final_jockey]["factors"].items()]

            with c_jp1:
                saved_jp1 = saved_h.get("j_plus1", "なし")
                jp1_idx = all_factor_labels.index(saved_jp1) if saved_jp1 in all_factor_labels else 0
                j_plus1 = st.selectbox("🏇 騎手特性 ➕①", all_factor_labels, index=jp1_idx, key=f"v4_jp1_{gate}", help=f"{final_jockey}の特性候補: {', '.join(j_hints)}")
            with c_jp2:
                saved_jp2 = saved_h.get("j_plus2", "なし")
                jp2_idx = all_factor_labels.index(saved_jp2) if saved_jp2 in all_factor_labels else 0
                j_plus2 = st.selectbox("🏇 騎手特性 ➕②", all_factor_labels, index=jp2_idx, key=f"v4_jp2_{gate}")
            with c_jm1:
                saved_jm1 = saved_h.get("j_minus1", "なし")
                jm1_idx = all_factor_labels.index(saved_jm1) if saved_jm1 in all_factor_labels else 0
                j_minus1 = st.selectbox("🏇 騎手特性 ➖①", all_factor_labels, index=jm1_idx, key=f"v4_jm1_{gate}")
            with c_jm2:
                saved_jm2 = saved_h.get("j_minus2", "なし")
                jm2_idx = all_factor_labels.index(saved_jm2) if saved_jm2 in all_factor_labels else 0
                j_minus2 = st.selectbox("🏇 騎手特性 ➖②", all_factor_labels, index=jm2_idx, key=f"v4_jm2_{gate}")

            with c_pl:
                val_plus = saved_h.get("plus_label", "なし")
                p_idx = list(plus_options.keys()).index(val_plus) if val_plus in plus_options else 0
                p_label = st.selectbox("🐴 直前パドック ➕", list(plus_options.keys()), index=p_idx, key=f"v4_pl_{gate}")
            with c_mi:
                val_minus = saved_h.get("minus_label", "なし")
                m_idx = list(minus_options.keys()).index(val_minus) if val_minus in minus_options else 0
                m_label = st.selectbox("🐴 直前パドック ➖", list(minus_options.keys()), index=m_idx, key=f"v4_mi_{gate}")
                
                manual_adjustment = plus_options[p_label] + minus_options[m_label]
            
            st.write("") 

            horse_inputs.append({
                "gate": gate, "name": h_name, "idx": h_idx, "pop": h_pop, "f3f": h_f3f, "sire": h_sire,
                "jockey": final_jockey, "j_sel": selected_jock,
                "j_plus1": j_plus1, "j_plus2": j_plus2, "j_minus1": j_minus1, "j_minus2": j_minus2,
                "plus_label": p_label, "minus_label": m_label, "manual_adj": manual_adjustment
            })
            
        submit_button = st.form_submit_button(label="🚀 ジェニー予想を実行（新旧ロジック完全融合）", use_container_width=True)

    # 🔗 URL保存機能
    st.write("---")
    st.markdown("### 🔗 この入力状態を保存するURLを発行")
    if st.button("🌐 保存用URLを生成する", use_container_width=True):
        current_state = {
            "venue": venue, "course_key": course_key, "condition": condition,
            "num_horses": num_horses, "horses": horse_inputs
        }
        json_str = json.dumps(current_state, ensure_ascii=False)
        encoded_data = urllib.parse.quote(json_str)
        share_url = f"https://share.streamlit.io/YOUR_APP_PATH/?d={encoded_data}"
        st.success("🎉 保存用URLが生成されました！")
        st.text_area("📋 コピペ用URL", value=share_url, height=100)

# ==========================================
# 🧮 5. 計算コア（新旧判定ハイブリッド）
# ==========================================
with col_right:
    st.header("🏆 最終解析結果")
    
    if submit_button or "d" in query_params:
        scored_output = []

        for h in horse_inputs:
            score = float(h["idx"])
            calc_log = []
            
            # 人気補正
            if h["pop"] == 1: score += 4.0
            elif h["pop"] == 2: score += 2.0
            elif h["pop"] > 5: score -= (h["pop"] - 5) * 1.0
            
            # 上がり補正
            if course_data.get("dist") == "長距離":
                if h["f3f"] <= 34.2: score += 12.0
                elif h["f3f"] <= 35.0: score += 7.0
                elif h["f3f"] >= 36.5: score -= 4.0
            else:
                if h["f3f"] <= 33.8: score += 10.0
                elif h["f3f"] <= 34.5: score += 5.0
            
            # 血統自動補正（事典テキストに含まれる種牡馬名、またはgood_lineage、道悪特効に完全対応）
            sire_matched = False
            # 1. コース事典のテキスト内に、入力した種牡馬の名前が含まれているかを判定
            if h["sire"] and h["sire"] in course_data["note"]:
                score += 6.0 if course_data.get("dist") == "長距離" else 5.0
                sire_matched = True
            # 2. マスターの系統リストと合致する場合（バックアップ判定）
            elif h["sire"] in course_data["good_lineage"]:
                score += 6.0 if course_data.get("dist") == "長距離" else 5.0
                sire_matched = True
                
            if sire_matched:
                calc_log.append("適性血統クリア")
                
            # 道悪特効判定
            if is_bad_track and h["sire"] in BAD_TRACK_SIRES.get(course_data["track"], []):
                score += 8.0
                calc_log.append("道悪特効血統")
            
            # 🏇 ジョッキー倍率計算
            jockey_name = h["jockey"].strip()
            j_base = 1.05 
            factor_sum = 0.0
            
            if jockey_name in JOCKEY_MASTER:
                j_data = JOCKEY_MASTER[jockey_name]
                j_base = j_data["base"]
                
                # 自動判定（コース条件を読み取り）
                if course_data["track"] == "芝" and "芝" in j_data["factors"]: factor_sum += j_data["factors"]["芝"]
                if course_data["track"] == "ダート" and "ダート" in j_data["factors"]: factor_sum += j_data["factors"]["ダート"]
                if course_data.get("dist") == "長距離" and "長距離" in j_data["factors"]: factor_sum += j_data["factors"]["長距離"]
                if is_bad_track and "荒れ馬場" in j_data["factors"]: factor_sum += j_data["factors"]["荒れ馬場"]
                if h["gate"] <= 3 and "内枠" in j_data["factors"]: factor_sum += j_data["factors"]["内枠"]
                if h["gate"] >= 14 and "外枠" in j_data["factors"]: factor_sum += j_data["factors"]["外枠"]
            
            # 手動選定されたジョッキーファクターを加減算
            manual_factor_val = 0.0
            for jp in [h["j_plus1"], h["j_plus2"], h["j_minus1"], h["j_minus2"]]:
                if jp != "なし":
                    manual_factor_val += ALL_JOCKEY_FACTORS[jp]
            
            # 倍率確定と適用
            final_multiplier = j_base + factor_sum + manual_factor_val
            score *= final_multiplier
            
            calc_log.append(f"騎手倍率: {final_multiplier:.2f}倍(基本{j_base}/自動{factor_sum:+.2f}/手動{manual_factor_val:+.2f})")
            
            # 直前パドック補正
            score += h["manual_adj"]
            if h["manual_adj"] != 0:
                calc_log.append(f"パドック: {h['manual_adj']:+f}pt")
                    
            scored_output.append({
                "gate": h["gate"], "name": h["name"], "pop": h["pop"],
                "jockey": jockey_name, "score": score, "log": " / ".join(calc_log)
            })
            
        # 結果表示の構築
        scored_output.sort(key=lambda x: x["score"], reverse=True)
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
            st.caption(f"鞍上: {h['jockey']} \n\n {h['log']}")
            
    else:
        st.info("👈 左側に入力して『予想を実行』ボタンを押してください。")
