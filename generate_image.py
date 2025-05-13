import streamlit as st
from PIL import Image
import openai
import base64
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


st.title("印刷方式判定アプリ")
st.write("画像をアップロードすると、最適な印刷方式（スクリーン印刷 / DTG / DTF）をAIが判定します。")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    if st.button("印刷方式を判定する"):
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたはTシャツ用デザイン画像に最適な印刷方式を判定する専門家です。"},
                {"role": "user", "content": [
                    {"type": "text", "text":
                        """あなたはTシャツの印刷方式を判別する専門家です。

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

【画像は以下に添付されています】

"""}, 
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]}
            ],
            max_tokens=500,
        )

        result = response.choices[0].message.content  # ← これが正しい
        st.markdown("### 判定結果")
        st.write(result)
