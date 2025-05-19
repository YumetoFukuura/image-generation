import streamlit as st
from PIL import Image
import io
import google.generativeai as genai

# Streamlit Cloud向け：APIキーをsecretsから取得
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("印刷方式判定アプリ（Gemini 1.5 Flash版）")
st.write("画像をアップロードすると、最適な印刷方式（スクリーン印刷 / DTG / DTF）をAIが判定します。")

model = genai.GenerativeModel("gemini-1.5-flash")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["png", "jpg", "jpeg"])

if uploaded_file:
    if any(c in uploaded_file.name for c in ' 　') or not uploaded_file.name.isascii():
        st.error("⚠ ファイル名に空白や日本語を含まない英数字名にしてください")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="アップロードされた画像", use_container_width=True)

        if st.button("印刷方式を判定する"):
            with st.spinner("AIが解析中です..."):
                prompt = """
あなたはTシャツの印刷方式を判別する専門家です。

以下の画像は、Tシャツにプリントされる予定のデザイン画像です。この画像に対して、以下の3つの印刷方式の中で最も適したものを1つだけ選んでください。また、その理由を専門的な観点から具体的に説明してください。

▼ 印刷方式の詳細：

1. 【スクリーン印刷】
- 最大5色までしか使えません。
- グラデーションは使用できません（色が徐々に変化する表現は不可）。
- 線や点は0.8mm以上必要です（細すぎる表現は印刷時に再現できません）。
- 注文枚数が多い場合にコストメリットがあります。

2. 【DTG（Direct to Garment）】
- A3サイズ（3507×4962ピクセル）を想定し、300dpiの解像度で印刷します。
- グラデーションや多色表現などの制限は特にありません。
- インクを直接生地に吹き付ける方式です。

3. 【DTF（Direct to Film）】
- A3サイズ（7014×9924ピクセル）を想定し、600dpiの解像度で印刷します。
- 色→色のグラデーションは可能ですが、色→透明へのグラデーション（フェードアウト）は不可です。
- フィルムに印刷して後で転写します。

▼ 判定タスク：
アップロードされた画像を見て、次の3点に答えてください：

1. 最も適している印刷方式（スクリーン印刷 / DTG / DTF）
2. 理由（使用されている色数、グラデーションの有無、線の細さなどを評価してください）
3. 必要があれば、注意点やデザイン修正のアドバイスも記載してください
"""

        # 🚨 修正：画像を明示的にバイト列で渡す
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            image_bytes = output.getvalue()

        image_part = {
            "mime_type": "image/png",
            "data": image_bytes
        }

        try:
            response = model.generate_content([prompt, image_part])
            st.markdown("### 判定結果")
            st.write(response.text)
        except Exception as e:
            st.error("Gemini API呼び出しでエラーが発生しました。")
            st.code(str(e))