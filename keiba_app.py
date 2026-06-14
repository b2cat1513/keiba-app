import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 🗺️ COURSE_MASTER データ (10競馬場完全収録)
# ==========================================
COURSE_MASTER = {
    # 東京競馬場
    "東京芝1400": {"note": "京王杯SC等。3コーナーまでの直線が長く枠順の有利不利は少ない。短距離のスピードとマイルを乗り切るスタミナのバランスが重要。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー", "モーリス"]},
    "東京芝1600": {"note": "安田記念、NHKマイルC等。重賞はマイル以上のスタミナが必要なタフな流れになりやすく、差し・追い込み有利。ロードカナロア/エピファネイア産駒○。", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "モーリス", "キズナ"]},
    "東京芝1800": {"note": "毎日王冠等。スタート後すぐに2コーナーのカーブがあるため内枠が有利。キレ味（上がり3Fの速さ）が最重要視される舞台。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ", "キングカメハメハ"]},
    "東京芝2000": {"note": "天皇賞(秋)等。スタート直後に2コーナーがあり、外枠は大きなロス。1桁馬番が超強力。内枠の先行・好位差しが絶対有利。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "モーリス", "キズナ", "キタサンブラック"]},
    "東京芝2400": {"note": "日本ダービー、ジャパンC等。日本競馬の最高峰。極端な枠の有利不利はないが、インをロスなく回れる内〜中枠の立ち回り重視。前走での上がり3Fが速い馬が有利。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ドゥラメンテ", "ハーツクライ", "ディープインパクト系"]},
    "東京芝2500": {"note": "目黒記念等。坂の途中からのスタートでスタミナ要求値が高い。ハンデ戦も多く、タフに伸びるスタミナ血統が狙い目。", "track": "芝", "dist": "長距離", "good_lineage": ["ハーツクライ", "オルフェーヴル", "ルーラーシップ"]},
    "東京芝3400": {"note": "ダイヤモンドS。日本屈指の長距離。スローペースからの超ロングスパート持久力戦。スタミナ特化血統・長距離実績馬を素直に信頼。", "track": "芝", "dist": "長距離", "good_lineage": ["オルフェーヴル", "ゴールドシップ", "ハーツクライ"]},
    "東京ダ1300": {"note": "スタートから最初のコーナーまでが短く、内枠の先行馬が非常に有利。包まれると厳しいので、外枠の快速馬のハナ切りも警戒。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス", "ドレフォン"]},
    "東京ダ1400": {"note": "根岸S等。芝スタート。外枠に行くほど芝を走る距離が長くなるため、外枠のスピード馬が圧倒的に有利。直線が長く差しも届く。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "ロードカナロア", "シニスターミニスター"]},
    "東京ダ1600": {"note": "フェブラリーS等。スタートが芝で外枠有利。非常にスピードが出やすく、ダートながらマイル以上のスタミナと大型馬のパワーが必須。", "track": "ダート", "dist": "中距離", "good_lineage": ["ヘニーヒューズ", "ドレフォン", "ロードカナロア", "シニスターミニスター"]},
    "東京ダ2100": {"note": "直線が長く、ダートとしては屈指のスタミナとタフさが必要。スタミナ型の差し馬や、タフな流れを経験してきた馬が強い。", "track": "ダート", "dist": "長距離", "good_lineage": ["シニスターミニスター", "キングカメハメハ", "ハーツクライ系"]},

    # 中山競馬場
    "中山芝1200": {"note": "スプリンターズS等。スタートから4コーナーまで下り坂が続くため、超ハイペースになりやすい。スピードの持続力と、最後の急坂を耐えるパワーが必要。内枠有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー", "ビッグアーサー"]},
    "中山芝1600": {"note": "外回り。スタートが1コーナーのポケットにあり、外枠は常に外を回らされるため壊滅的に不利。1枠〜3枠の先行馬が絶対有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ダイワメジャー", "モーリス", "ロードカナロア"]},
    "中山芝1800": {"note": "中山記念等。内回り。スタート後すぐに1コーナーがあるため先行争いが激しくなりやすい。タフな小回り適性と急坂での加速力が求められる。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "キングカメハメハ", "ハーツクライ"]},
    "中山芝2000": {"note": "皐月賞、ホープフルS等。内回り。4回コーナーを回るため器用さが必要。開幕週はイン先行有利、荒れ馬場・重馬場は外差しが台頭。エピファネイア/ハービンジャー○。", "track": "芝", "dist": "中距離", "good_lineage": ["エピファネイア", "ハービンジャー", "モーリス", "キズナ"]},
    "中山芝2200": {"note": "オールカマー等。外回りから内回りへ合流するトリッキーなコース。スタミナと外から長く脚を使える持続力血統が強い。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "ステイゴールド系", "ルーラーシップ"]},
    "中山芝2500": {"note": "有馬記念等。内回り。内枠(1桁馬番)の勝率が突出しており外枠は圧倒的ロス。急坂を2回超えるため、タフなスタミナと小回りをロスなく回る立ち回りが必須。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キズナ", "ドゥラメンテ", "ゴールドシップ"]},
    "中山芝3600": {"note": "ステイヤーズS。スタミナのみが要求される究極の長距離。リピーターが非常に多く、ステイゴールドやゴールドシップ系、長距離実績馬が鉄板。", "track": "芝", "dist": "長距離", "good_lineage": ["ゴールドシップ", "オルフェーヴル", "ルーラーシップ"]},
    "中山ダ1200": {"note": "芝スタートで外枠が有利。テンのスピードが非常に速くなり、前残りになりやすいが、ハイペースが極まると外からの差しも届く。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス", "ロードカナロア"]},
    "中山ダ1800": {"note": "非常にタフな急坂がありスタミナが必要。基本は先行馬が圧倒的に有利。重馬場になると泥を嫌う馬が多く、外枠の先行馬がさらに有利に。", "track": "ダート", "dist": "中距離", "good_lineage": ["ホッコータルマエ", "シニスターミニスター", "ヘニーヒューズ", "パイロ"]},
    "中山ダ2400": {"note": "スタミナ自慢が集まる長距離ダート。バテ合いの過酷なレースになりやすく、先行してじわじわ伸びる大型スタミナ馬や血統が強い。", "track": "ダート", "dist": "長距離", "good_lineage": ["シニスターミニスター", "キングカメハメハ", "クロフネ系"]},

    # 京都競馬場
    "京都芝1200": {"note": "内回り。3コーナーの坂を上って下るため、下り坂を利用した高速スピードの持続力必要。基本は内枠の先行馬有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー", "ダイワメジャー"]},
    "京都芝1400": {"note": "重賞は外回り。直線が平坦なため、鋭い瞬発力を持つキレ味血統が有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ディープインパクト系", "ダイワメジャー"]},
    "京都芝1600": {"note": "マイルCS等。外回り。3コーナーの坂の下りから一気にペースが上がる。平坦な直線での高速キレ味勝負になりやすく、ディープ系やエピファネイア産駒○。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "エピファネイア", "キズナ", "モーリス"]},
    "京都芝1800": {"note": "外回り。スピードとキレ味の要求値が非常に高い。直線の瞬発力勝負になりやすいため、上がりの速いディープ系やハーツクライ系が中心。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ", "キングカメハメハ"]},
    "京都芝2000": {"note": "秋華賞等。内回り。スタート直後に1コーナーがあり内枠有利。先行・好位差しがベスト。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "エピファネイア", "ドゥラメンテ"]},
    "京都芝2200": {"note": "エリザベス女王杯等。外回りの長丁場。3コーナーの坂を2回走るため見た目以上にタフ。リピーター注意。", "track": "芝", "dist": "中距離", "good_lineage": ["ハーツクライ", "ハービンジャー", "オルフェーヴル", "キズナ"]},
    "京都芝2400": {"note": "京都大賞典等。外回り。長距離の王道コース。坂の下りを活かして長く良い脚を使える中長距離実績馬、ドゥラメンテ系やハーツ系が好相性。", "track": "芝", "dist": "長距離", "good_lineage": ["ドゥラメンテ", "ハーツクライ", "キタサンブラック"]},
    "京都芝3000": {"note": "菊花賞。坂を2回超える。長距離のスタミナはもちろん、坂の下りで引っかからない折り合いのセンスと騎手の腕が最も問われる舞台。", "track": "芝", "dist": "長距離", "good_lineage": ["エピファネイア", "キタサンブラック", "ディープインパクト系"]},
    "京都芝3200": {"note": "天皇賞(春)。長距離のスタミナと、インをロスなく回る立ち回り、精度。キタサンブラックやステイゴールド系の血が爆発する。", "track": "芝", "dist": "長距離", "good_lineage": ["キタサンブラック", "ゴールドシップ", "オルフェーヴル", "ハーツクライ"]},
    "京都ダ1200": {"note": "平坦でスピードが出やすい。かなり時計が速くなるため、テンのスピード能力が高い快速馬の内枠先行が有利。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス", "ドレフォン"]},
    "京都ダ1400": {"note": "平坦マイル以下。先行勢が止まりにくく前残りが多い。スピードのあるミスプロ系やヘニーヒューズ産駒が安定。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "シニスターミニスター", "ロードカナロア"]},
    "京都ダ1800": {"note": "主要ダートコース。急坂がないため、好位につけられる器用さと、最後の直線のスピード持続力が必要。内枠の先行・好位差し安定。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ", "キングカメハメハ", "ヘニーヒューズ"]},
    "京都ダ1900": {"note": "1800mよりさらにスタミナ寄り。タフなスタミナ型ダート馬や、シニスターミニスターなど道悪でもパワーで押し切れる血統が有利。", "track": "ダート", "dist": "長距離", "good_lineage": ["シニスターミニスター", "マジェスティックウォリアー"]},

    # 阪神競馬場
    "阪神芝1200": {"note": "内回り。急坂があるため、スピードだけでなくパワーが必要。荒れ馬場・重馬場になると一気にタフな消耗戦になり差し有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ダイワメジャー", "ビッグアーサー"]},
    "阪神芝1400": {"note": "内回り。阪神C等。内回りのため、3〜4コーナーの立ち回りと、直線の坂を乗り切るパワーが要求される。タフな持続力血統が良い。", "track": "芝", "dist": "短距離", "good_lineage": ["ダイワメジャー", "ロードカナロア", "モーリス"]},
    "阪神芝1600": {"note": "外回り。桜花賞、阪神JF等。外回りの直線が長く、非常に実力が反映されやすい。高速馬場なら瞬発力、重馬場ならスタミナパワー型。", "track": "芝", "dist": "中距離", "good_lineage": ["ロードカナロア", "エピファネイア", "キズナ", "ディープインパクト系"]},
    "阪神芝1800": {"note": "外回り. 直線が長いため実力勝負。少頭数になりやすくスローからのキレ味勝負になりがち。ハーツ系やディープ系の上がり最速馬が狙い目。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ", "キングカメハメハ"]},
    "阪神芝2000": {"note": "内回り。大阪杯等。スタート後すぐに急坂があり、先行争いが落ち着きやすい。内回りの器用さと、直線でもう一度坂を登る強靭なパワーが必要。", "track": "芝", "dist": "中距離", "good_lineage": ["キズナ", "ロードカナロア", "ドゥラメンテ", "エピファネイア"]},
    "阪神芝2200": {"note": "内回り. 宝塚記念等。非常にタフな内回りコース。時計のかかる馬場になりやすく、スタミナと持続力の消耗戦になりやすい。ステイゴールド系やキズナ○。", "track": "芝", "dist": "中距離", "good_lineage": ["ステイゴールド系", "ハーツクライ", "キズナ", "ルーラーシップ"]},
    "阪神芝2400": {"note": "外回り。神戸新聞杯等。直線が長いため紛れが少ない。スタミナと直線での末脚の持続力、G1級の実力が素直に要求されるタフなコース。", "track": "芝", "dist": "長距離", "good_lineage": ["ハーツクライ", "ドゥラメンテ", "キタサンブラック"]},
    "阪神芝3000": {"note": "阪神大賞典。内回りを1周半するタフな長距離。スタミナ型、荒れ馬場になればなるほどステイゴールド/ゴールドシップ系優勢。", "track": "芝", "dist": "長距離", "good_lineage": ["ゴールドシップ", "オルフェーヴル", "キズナ"]},
    "阪神ダ1200": {"note": "急坂スタートのため、テンのスピードだけでなくパワーが必要。スピードのある外枠の先行馬が泥を被らずに押し切る展開が多い。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "サウスヴィグラス", "シニスターミニスター"]},
    "阪神ダ1400": {"note": "プロキオンS等。芝スタートで外枠が圧倒的に有利。非常に時計が速くなりやすく、芝並みのスピード持続力と直線の坂をこなす大型馬が有利。", "track": "ダート", "dist": "短距離", "good_lineage": ["ヘニーヒューズ", "ロードカナロア", "シニスターミニスター"]},
    "阪神ダ1800": {"note": "主要ダート。スタート直後に急坂を登る。タフで過酷なスタミナ勝負になりやすく、先行して最後までバテずに伸びるシニスターミニスターが強力。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "ホッコータルマエ", "キングカメハメハ", "マジェスティックウォリアー"]},
    "阪神ダ2000": {"note": "シリウスS等。1800mよりもさらにスタミナ要求値が高い。JRAダートの中でも屈指のタフコースで、ダート長距離の適性を持つパワー型が狙い目。", "track": "ダート", "dist": "長距離", "good_lineage": ["シニスターミニスター", "キングカメハメハ"]},

    # 他、主要ローカルコース
    "中京芝1200": {"note": "高松宮記念等。最後の直線には急坂があり直線も長いため、短距離ながらマイル級のタフさが必要。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ミッキーアイル", "ダイワメジャー"]},
    "中京ダ1800": {"note": "チャンピオンズC等。1、2コーナーが非常にタイトで、内枠の先行・好位差しが抜群に有利。外枠は致命的なロスになりやすい。", "track": "ダート", "dist": "中距離", "good_lineage": ["キングカメハメハ", "シニスターミニスター", "ホッコータルマエ", "ドレフォン"]},
    "新潟芝1600": {"note": "関屋記念等。外回り。日本一長い直線（659m）を持つ。極限の瞬発力・キレ味勝負になりやすくディープ系や瞬発力血統有利。", "track": "芝", "dist": "中距離", "good_lineage": ["ディープインパクト系", "ハーツクライ", "スワーヴリチャード"]},
    "福島ダ1700": {"note": "ローカルダートの代表格。非常に小回りで、内枠から先手を奪える馬、または外枠から強引にハナを奪える快速馬を重視。", "track": "ダート", "dist": "中距離", "good_lineage": ["シニスターミニスター", "パイロ", "ホッコータルマエ", "マジェスティックウォリアー"]},
    "小倉芝1200": {"note": "小倉2歳S等。下り坂スタートのため超ハイペースの高速時計が出やすい。内枠の先行馬か、スピードのあるマクリ馬有利。", "track": "芝", "dist": "短距離", "good_lineage": ["ロードカナロア", "ビッグアーサー", "ダイワメジャー", "ミッキーアイル"]},
    "函館芝2000": {"note": "函館記念等。洋芝2000m。JRAで最も重い芝コースの1つ。スタミナとパワーを併せ持つハービンジャーやキズナが台頭。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "オルフェーヴル", "ルーラーシップ", "キズナ"]},
    "札幌芝2000": {"note": "札幌記念等。夏の最大大一番。コーナーが丸く平坦。洋芝のタフな持続力戦になりやすく、実績のある実力馬が強い。", "track": "芝", "dist": "中距離", "good_lineage": ["ハービンジャー", "ステイゴールド系", "キングカメハメハ系", "キズナ"]}
}

# ==========================================
# 🏇 JOCKEY_MASTER 精鋭ジョッキーデータ（36名）
# ==========================================
JOCKEY_MASTER = {
    # 超Sランク・トップランカー
    "ルメール": {"base_bonus": 10, "good_venues": ["東京", "中山", "京都", "阪神"], "bad_track_bonus": 2, "note": "JRA最強。大舞台の信頼度は異次元。"},
    "川田": {"base_bonus": 9, "good_venues": ["阪神", "京都", "中京", "小倉"], "bad_track_bonus": 3, "note": "抜群の勝率と先行意識。好位抜け出しの鬼。"},
    "モレイラ": {"base_bonus": 10, "good_venues": ["東京", "阪神", "京都", "中山"], "bad_track_bonus": 3, "note": "「マジックマン」。短期免許時は文句なしの最優先。"},
    "レーン": {"base_bonus": 9, "good_venues": ["東京", "中山", "阪神"], "bad_track_bonus": 3, "note": "オーストラリアの名手。重賞勝負強さは折り紙付き。"},
    "マーカンド": {"base_bonus": 8, "good_venues": ["東京", "中山", "中京"], "bad_track_bonus": 5, "note": "英国の剛腕。道悪や直線での叩き合いで馬を伸ばす。"},
    "武豊": {"base_bonus": 7, "good_venues": ["京都", "阪神", "東京"], "bad_track_bonus": 2, "note": "伝統のレジェンド。長距離・京都での手綱捌きは神。"},
    "坂井": {"base_bonus": 7, "good_venues": ["中京", "阪神", "新潟", "東京"], "bad_track_bonus": 3, "note": "積極果敢な逃げ・先行で高い勝率を誇る。"},
    "横山武": {"base_bonus": 7, "good_venues": ["中山", "東京", "函館", "札幌"], "bad_track_bonus": 4, "note": "中山巧者。洋芝やタフ馬場でもガシガシ追える。"},
    "戸崎": {"base_bonus": 6, "good_venues": ["東京", "中山", "新潟"], "bad_track_bonus": 2, "note": "関東の安定勢力。直線での粘り込みが得意。"},
    
    # 主要実力派・ベテラン
    "岩田康": {"base_bonus": 5, "good_venues": ["阪神", "京都", "中山"], "bad_track_bonus": 6, "note": "イン突きの極意。荒れ馬場・道悪のイン差し警戒。"},
    "松山": {"base_bonus": 6, "good_venues": ["京都", "阪神", "中京", "小倉"], "bad_track_bonus": 4, "note": "タフな消耗戦が得意。1日通して非常に安定。"},
    "岩田望": {"base_bonus": 6, "good_venues": ["中京", "阪神", "小倉", "新潟"], "bad_track_bonus": 3, "note": "若手トップクラス。ダートの複勝率が極めて高い。"},
    "西村淳": {"base_bonus": 6, "good_venues": ["中京", "京都", "阪神", "新潟"], "bad_track_bonus": 4, "note": "近年急成長。積極的な位置取りとローカル重賞○。"},
    "デムーロ": {"base_bonus": 5, "good_venues": ["中山", "阪神", "東京"], "bad_track_bonus": 6, "note": "道悪・荒れ馬場での外マクリは一級品の一発屋。"},
    "和田竜": {"base_bonus": 4, "good_venues": ["京都", "阪神", "中京"], "bad_track_bonus": 7, "note": "【道悪特効】重・不良馬場で追わせたら無類の強さ。"},
    "幸": {"base_bonus": 4, "good_venues": ["京都", "阪神", "小倉"], "bad_track_bonus": 5, "note": "ダートや道悪の先行粘り込みで穴をあける職人。"},
    "横山典": {"base_bonus": 5, "good_venues": ["中山", "東京", "函館"], "bad_track_bonus": 3, "note": "ベテランの魔術師。ポツンからの大外一気やイン突き。"},
    "鮫島駿": {"base_bonus": 5, "good_venues": ["中京", "小倉", "阪神", "新潟"], "bad_track_bonus": 4, "note": "ローカル開催や中京でのコース取りが非常に上手い。"},
    "菅原明": {"base_bonus": 5, "good_venues": ["東京", "中山", "新潟"], "bad_track_bonus": 4, "note": "関東の実力派。長い直線での追える末脚が武器。"},
    "三浦": {"base_bonus": 4, "good_venues": ["東京", "中山", "新潟"], "bad_track_bonus": 3, "note": "関東のベテラン。ダートの上位人気馬での安定感。"},
    "団野": {"base_bonus": 5, "good_venues": ["京都", "阪神", "小倉"], "bad_track_bonus": 4, "note": "大舞台でも物怖じしない度胸と鋭い差し脚が魅力。"},
    "津村": {"base_bonus": 4, "good_venues": ["東京", "中山", "新潟"], "bad_track_bonus": 4, "note": "G1勝利も果たした実力派。好位立ち回りで真価。"},
    "北村友": {"base_bonus": 4, "good_venues": ["阪神", "京都", "中京"], "bad_track_bonus": 3, "note": "復活を遂げた実力派。牝馬限定戦やマイル以下で妙味。"},
    "藤岡佑": {"base_bonus": 4, "good_venues": ["京都", "阪神", "函館"], "bad_track_bonus": 3, "note": "展開を読む目に長け、ペースが落ち着いた先行策○。"},
    "横山和": {"base_bonus": 5, "good_venues": ["中山", "東京", "札幌"], "bad_track_bonus": 4, "note": "ダート長距離や洋芝などスタミナ舞台で強気。"},
    "田辺": {"base_bonus": 4, "good_venues": ["東京", "中山"], "bad_track_bonus": 4, "note": "ノーマークの逃げ・先行での大穴演出が代名詞。"},
    "吉田隼": {"base_bonus": 4, "good_venues": ["中山", "函館", "札幌"], "bad_track_bonus": 3, "note": "ローカル・洋芝での安定感が高く、インを突く。"},
    "丹内": {"base_bonus": 4, "good_venues": ["函館", "札幌", "福島"], "bad_track_bonus": 5, "note": "北海道・ローカルの帝王。洋芝滞在競馬は鉄板。"},
    
    # 若手・期待株＆穴の職人
    "田口": {"base_bonus": 5, "good_venues": ["中京", "京都", "阪神", "小倉"], "bad_track_bonus": 4, "note": "若手の星。抜群の追込力と積極性。"},
    "西塚": {"base_bonus": 4, "good_venues": ["東京", "中山", "新潟"], "bad_track_bonus": 3, "note": "確かな騎乗技術で頭角を現す関東期待の若手。"},
    "今村": {"base_bonus": 3, "good_venues": ["小倉", "新潟", "中京"], "bad_track_bonus": 3, "note": "ローカル短距離・ダート戦でのハナ切りで真価。"},
    "佐々木": {"base_bonus": 5, "good_venues": ["函館", "札幌", "中山"], "bad_track_bonus": 4, "note": "北海道で大ブレイク。先行ポジション取りが秀逸。"},
    "菱田": {"base_bonus": 3, "good_venues": ["京都", "阪神", "小倉"], "bad_track_bonus": 4, "note": "穴馬を前線に持ってくる粘り強い追い込みが特徴。"},
    "斎藤": {"base_bonus": 3, "good_venues": ["中京", "小倉", "新潟"], "bad_track_bonus": 3, "note": "先行意識が高く、ローカルのダート戦で警戒。"},
    "武藤": {"base_bonus": 3, "good_venues": ["東京", "中山"], "bad_track_bonus": 4, "note": "ダートの短距離戦での内枠逃げ粘りに注意。"},
    "大野": {"base_bonus": 3, "good_venues": ["東京", "中山", "新潟"], "bad_track_bonus": 4, "note": "中山ダートや直線の長いコースでの追い込み特化。"}
}

BAD_TRACK_SIRES = {
    "芝": ["キズナ", "ハービンジャー", "エピファネイア", "オルフェーヴル", "ゴールドシップ", "ドゥラメンテ", "モーリス", "ルーラーシップ"],
    "ダート": ["シニスターミニスター", "ホッコータルマエ", "ヘニーヒューズ", "パイロ", "マジェスティックウォリアー", "ドレフォン"]
}

class HorseEncoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JRA全コース対応 AI予想システム ver1.01")
        self.root.geometry("1150x850")
        
        style = ttk.Style()
        style.theme_use("clam")
        
        self.num_horses = tk.IntVar(value=8)
        self.horse_inputs = []
        
        self.create_menu_and_header()
        self.create_main_layout()
        
        self.update_course_options()
        self.change_horse_count()

    def create_menu_and_header(self):
        header_frame = ttk.LabelFrame(self.root, text=" レース基本設定 ", padding=10)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(header_frame, text="競馬場:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.venue_combo = ttk.Combobox(header_frame, values=["東京", "中山", "京都", "阪神", "中京", "新潟", "福島", "小倉", "函館", "札幌"], width=10, state="readonly")
        self.venue_combo.grid(row=0, column=1, padx=5, pady=5)
        self.venue_combo.set("東京")
        self.venue_combo.bind("<<ComboboxSelected>>", lambda e: self.update_course_options())
        
        ttk.Label(header_frame, text="コース:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.course_combo = ttk.Combobox(header_frame, width=15, state="readonly")
        self.course_combo.grid(row=0, column=3, padx=5, pady=5)
        self.course_combo.bind("<<ComboboxSelected>>", lambda e: self.show_course_note())
        
        ttk.Label(header_frame, text="馬場状態:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.track_condition_combo = ttk.Combobox(header_frame, values=["良", "稍重", "重", "不良"], width=8, state="readonly")
        self.track_condition_combo.grid(row=0, column=5, padx=5, pady=5)
        self.track_condition_combo.set("良")
        
        ttk.Label(header_frame, text="出頭数:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.spin_horses = tk.Spinbox(header_frame, from_=2, to=18, textvariable=self.num_horses, command=self.change_horse_count, width=5)
        self.spin_horses.grid(row=0, column=7, padx=5, pady=5)
        
        self.calc_btn = ttk.Button(header_frame, text="📊 総合AIスコアを計算", command=self.calculate_scores)
        self.calc_btn.grid(row=0, column=8, padx=20, pady=5)
        
        self.note_label = ttk.Label(header_frame, text="※コースを選択してください", foreground="gray", font=("MS Gothic", 9, "italic"), wraplength=1000)
        self.note_label.grid(row=1, column=0, columnspan=9, padx=5, pady=5, sticky="w")

    def create_main_layout(self):
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=10, pady=5)
        
        left_frame = ttk.LabelFrame(main_paned, text=" 📝 出走馬＆ジョッキーデータ入力 (騎手欄は直接入力も可能) ", padding=5)
        self.canvas = tk.Canvas(left_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_input_frame = ttk.Frame(self.canvas)
        
        self.scroll_input_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_input_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        main_paned.add(left_frame, weight=6)
        
        right_frame = ttk.LabelFrame(main_paned, text=" 🏆 最終解析・評価結果一覧 ", padding=5)
        self.result_text = tk.Text(right_frame, font=("Courier", 10), wrap="none")
        r_scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=self.result_text.yview)
        r_scroll_x = ttk.Scrollbar(right_frame, orient="horizontal", command=self.result_text.xview)
        self.result_text.configure(yscrollcommand=r_scroll_y.set, xscrollcommand=r_scroll_x.set)
        
        self.result_text.pack(side="top", fill="both", expand=True)
        r_scroll_y.pack(side="right", fill="y")
        r_scroll_x.pack(side="bottom", fill="x")
        main_paned.add(right_frame, weight=5)

    def update_course_options(self):
        v = self.venue_combo.get()
        valid_courses = [k for k in COURSE_MASTER.keys() if k.startswith(v)]
        self.course_combo.config(values=valid_courses)
        if valid_courses:
            self.course_combo.set(valid_courses[0])
        else:
            self.course_combo.set("")
        self.show_course_note()

    def show_course_note(self):
        c_key = self.course_combo.get()
        if c_key in COURSE_MASTER:
            self.note_label.config(text=f"【コース特徴】 {COURSE_MASTER[c_key]['note']}", foreground="black")
        else:
            self.note_label.config(text="※該当するコースデータがありません", foreground="red")

    def change_horse_count(self):
        for widgets in self.scroll_input_frame.winfo_children():
            widgets.destroy()
            
        self.horse_inputs = []
        
        headers = ["馬番", "馬名", "前走着順", "前走人気", "前走上り", "父(種牡馬)", "想定騎手"]
        widths = [4, 12, 6, 6, 8, 12, 12]
        for col_idx, (text, w) in enumerate(zip(headers, widths)):
            lbl = ttk.Label(self.scroll_input_frame, text=text, font=("MS Gothic", 9, "bold"), anchor="center")
            lbl.grid(row=0, column=col_idx, padx=3, pady=5, sticky="ew")
            
        all_jockeys = list(JOCKEY_MASTER.keys())
        default_sires = ["キズナ", "ロードカナロア", "エピファネイア", "ハーツクライ", "シニスターミニスター", "ドゥラメンテ", "モーリス", "ゴールドシップ", "ハービンジャー", "ルーラーシップ"]
        
        for i in range(self.num_horses.get()):
            row = i + 1
            
            num_lbl = ttk.Label(self.scroll_input_frame, text=f" {row} ", anchor="center")
            num_lbl.grid(row=row, column=0, padx=3, pady=2)
            
            ent_name = ttk.Entry(self.scroll_input_frame, width=12)
            ent_name.insert(0, f"ウマ{row}")
            ent_name.grid(row=row, column=1, padx=3, pady=2)
            
            ent_rank = ttk.Entry(self.scroll_input_frame, width=6)
            ent_rank.insert(0, str((i % 4) + i // 4 + 1))
            ent_rank.grid(row=row, column=2, padx=3, pady=2)
            
            ent_pop = ttk.Entry(self.scroll_input_frame, width=6)
            ent_pop.insert(0, str((i % 5) + 1))
            ent_pop.grid(row=row, column=3, padx=3, pady=2)
            
            ent_f3f = ttk.Entry(self.scroll_input_frame, width=8)
            ent_f3f.insert(0, str(34.0 + (i * 0.2)))
            ent_f3f.grid(row=row, column=4, padx=3, pady=2)
            
            ent_sire = ttk.Entry(self.scroll_input_frame, width=12)
            ent_sire.insert(0, default_sires[i % len(default_sires)])
            ent_sire.grid(row=row, column=5, padx=3, pady=2)
            
            # 【★改良ポイント】EntryからComboboxに変更 (自由入力も許可する仕様)
            combo_jock = ttk.Combobox(self.scroll_input_frame, values=all_jockeys, width=10)
            combo_jock.insert(0, all_jockeys[i % len(all_jockeys)]) 
            combo_jock.grid(row=row, column=6, padx=3, pady=2)
            
            self.horse_inputs.append({
                "gate": row, "name": ent_name, "rank": ent_rank, 
                "pop": ent_pop, "f3f": ent_f3f, "sire": ent_sire, "jockey": combo_jock
            })
            
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def calculate_scores(self):
        c_key = self.course_combo.get()
        if not c_key or c_key not in COURSE_MASTER:
            messagebox.showerror("エラー", "有効なコースを選択してください。")
            return
            
        current_venue = self.venue_combo.get()
        course_data = COURSE_MASTER[c_key]
        condition = self.track_condition_combo.get()
        is_bad_track = condition in ["重", "不良"]
        
        scored_horses = []
        
        for idx, inp in enumerate(self.horse_inputs):
            try:
                name = inp["name"].get().strip()
                rank = int(inp["rank"].get())
                pop = int(inp["pop"].get())
                f3f = float(inp["f3f"].get())
                sire = inp["sire"].get().strip()
                jockey = inp["jockey"].get().strip()
            except ValueError:
                messagebox.showerror("入力エラー", f"馬番 {idx+1} の数値データが不正です。")
                return
                
            score = 100
            
            # 1. 前走成績補正
            if rank == 1: score += 5
            elif rank == 2: score += 2
            elif rank > 5: score -= (rank - 5) * 3
            if pop > 5: score -= (pop - 5) * 2
            
            # 2. 上り3F能力評価
            if course_data["track"] == "芝" and course_data["dist"] in ["中距離", "長距離"]:
                if f3f <= 34.0: score += 10
                elif f3f <= 35.0: score += 5
                elif f3f >= 36.5: score -= 8
            else:
                if f3f <= 35.0: score += 6
                elif f3f >= 37.5: score -= 6
                
            # 3. コース適合血統ボーナス
            if sire in course_data["good_lineage"]:
                score += 6
                
            # 4. 道悪血統特効補正
            if is_bad_track and sire in BAD_TRACK_SIRES.get(course_data["track"], []):
                score += 8
                
            # 5. ジョッキー能力＆舞台適合補正
            j_advice = "データなし"
            if jockey in JOCKEY_MASTER:
                j_data = JOCKEY_MASTER[jockey]
                j_advice = j_data["note"]
                score += j_data["base_bonus"]
                
                if current_venue in j_data["good_venues"]:
                    score += 4
                    
                if is_bad_track:
                    score += j_data["bad_track_bonus"]
            else:
                # リストにないジョッキーが手入力された場合の処理
                score += 2
                j_advice = "リスト外の騎手（標準補正適用）。展開次第。"
                
            scored_horses.append({
                "gate": inp["gate"], "name": name, "sire": sire, "jockey": jockey, "score": score, "j_note": j_advice
            })
            
        # スコアの高い順にソート
        scored_horses.sort(key=lambda x: x["score"], reverse=True)
        
        # 結果画面の描画
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"👑 JRA全コース対応 AI予想システム ver1.01 👑\n")
        self.result_text.insert(tk.END, f"◆ 開催舞台: {c_key} ({course_data['track']}/{course_data['dist']})\n")
        self.result_text.insert(tk.END, f"◆ 馬場状態: 【 {condition} 】\n")
        if is_bad_track:
            self.result_text.insert(tk.END, f"⚠️ 道悪警報：各騎手・血統固有の重馬場特効数値を算入済み。\n")
        self.result_text.insert(tk.END, f"-"*72 + "\n")
        self.result_text.insert(tk.END, f" 印 |馬番| 馬名          | 騎手     | 血統(父)     | 総合スコア \n")
        self.result_text.insert(tk.END, f"-"*72 + "\n")
        
        marks = ["◎", "○", "▲", "△", "☆"]
        for rank_idx, h in enumerate(scored_horses):
            mark = marks[rank_idx] if rank_idx < len(marks) else "  "
            self.result_text.insert(tk.END, f" {mark} | {h['gate']:02d} | {h['name']:<13s} | {h['jockey']:<8s} | {h['sire']:<12s} | {h['score']:5.1f} pt\n")
            
        self.result_text.insert(tk.END, f"-"*72 + "\n\n💡 コース攻略・戦術総評:\n")
        self.result_text.insert(tk.END, f" {course_data['note']}\n\n")
        
        self.result_text.insert(tk.END, "🏆 上位推奨馬のジョッキー補正根拠:\n")
        for i in range(min(3, len(scored_horses))):
            h = scored_horses[i]
            self.result_text.insert(tk.END, f" ・{h['name']} ({h['jockey']}): {h['j_note']}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = HorseEncoderApp(root)
    root.mainloop()
