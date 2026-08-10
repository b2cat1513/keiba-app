import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="画像アップロード診断", layout="centered")
st.title("📱 画像アップロード診断")
st.write("まず「ファイル選択テスト」を試してください。画像が戻らない場合は「カメラ入力テスト」を試します。")

st.subheader("1. ファイル選択テスト")
uploaded = st.file_uploader(
    "PNG・JPG画像を1枚選択",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
    key="simple_upload_test",
)

if uploaded is None:
    st.info("まだ画像は届いていません。")
else:
    data = uploaded.getvalue()
    st.success(f"受信成功：{uploaded.name} / {len(data):,} bytes")
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
        st.image(image, caption=uploaded.name, use_container_width=True)
        st.write(f"画像サイズ：{image.width} × {image.height}")
        st.write(f"画像形式：{image.format}")
    except Exception as exc:
        st.error(f"画像を開けませんでした：{exc}")

st.divider()

st.subheader("2. カメラ入力テスト")
camera = st.camera_input("カメラで1枚撮影")

if camera is None:
    st.info("まだカメラ画像は届いていません。")
else:
    data = camera.getvalue()
    st.success(f"カメラ画像受信成功：{len(data):,} bytes")
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
        st.image(image, caption="カメラ入力", use_container_width=True)
    except Exception as exc:
        st.error(f"カメラ画像を開けませんでした：{exc}")

st.divider()
st.caption("このページではOCRやセッション保存など、本体アプリの処理は一切実行しません。")
