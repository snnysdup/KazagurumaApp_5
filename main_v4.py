import datetime
import pandas as pd
import requests
import streamlit as st
# from openai 
import openai # OpenAIのAPIを扱うためのライブラリをインポート

# # OpenAIクライアントの初期化
# client = openai

# StreamlitのSecretsからAPIキーを取得
# 生成AI
client = openai(api_key = st.secrets["GPTAPI"].get("OPENAI_API_KEY"))
# # google books
# books_api_key = st.secrets["google"].get("books_api_key")

# Google Books APIキーの取得（UIからは消す）
books_api_key = st.secrets["google"]["books_api_key"]

# タイトル
st.title('📚 学びたい内容に合った本をおすすめ！')

# サイドバーでユーザー入力を取得
content_text_to_gpt = st.sidebar.text_input("🔍 学びたい内容を入力してください（例: Python, 心理学）")
content_current_to_gpt = st.sidebar.text_input("上記入力した学びに対してのあなたの理解度を教えてください（例：初学者、業務で使用している）")
content_goal_to_gpt = st.sidebar.text_input("上記入力した学びに対してのあなたがどの程度理解を深めたいか教えてください（例：業務で使えるレベル）")
content_others_to_gpt = st.sidebar.text_input("その他本の選定にあたり考慮して欲しい事項を記載してください（例：英語の本は除く、なるべく分かりやすい本、短い時間で読める本）")

# Google Books APIを使用して書籍を検索する関数
# search_booksにGPTをかませられるとよいかも
def search_books(query, books_api_key, max_results=5):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "printType": "books",
        "key": books_api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        st.error(f"Google Books APIのリクエスト中にエラーが発生しました: {response.status_code}")
        return []

# 生成AIを使用して推薦理由を生成する関数
def generate_recommendation_reason(book_title, content_text, content_current, content_goal, content_others):
    prompt = f"""
    ユーザーは「{content_text}」について学びたいと考えています。
    現在の理解度: {content_current}
    目標とする理解度: {content_goal}
    その他の考慮事項: {content_others}

    以下の書籍が推薦されています:
    書籍タイトル: {book_title}

    なぜこの書籍がユーザーにとって適切なのか、簡潔に説明してください。
    """
    try:
        # ChatCompletionを使用して推薦理由を生成
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 使用するモデルを指定
            messages=[{"role": "user", "content": prompt}],  # プロンプトをチャットメッセージ形式で指定
            max_tokens=150  # 必要に応じてトークン数を設定
        )
        return response['choices'][0]['message']['content'].strip()  # 応答から推薦理由を取得
    except Exception as e:
        st.error(f"生成AIからの推薦理由の生成中にエラーが発生しました: {str(e)}")
        return "推薦理由を生成できませんでした。"

# 検索ボタンが押された場合の処理
if st.sidebar.button("本を探す！"):
    if content_text_to_gpt:
        books = search_books(content_text_to_gpt, books_api_key)
        # 上のコード、books = search_books(content_text_to_gpt, books_api_key)に理解度もかませられるとよいかも
        if books:
            st.subheader(f"🔎『{content_text_to_gpt}』に関するおすすめの本：")
            for book in books:
                volume_info = book.get("volumeInfo", {})
                title = volume_info.get("title", "タイトル不明")
                authors = ", ".join(volume_info.get("authors", ["著者不明"]))
                description = volume_info.get("description", "説明がありません")
                thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "")
                info_link = volume_info.get("infoLink", "#")

                st.markdown("---")
                st.subheader(f"📖 [{title}]({info_link})")
                st.write(f"**著者:** {authors}")
                st.write(f"**説明:** {description}")
                if thumbnail:
                    st.image(thumbnail, width=120)

                # 推薦理由の生成
                recommendation_reason = generate_recommendation_reason(title, content_text_to_gpt, content_current_to_gpt, content_goal_to_gpt, content_others_to_gpt)
                st.write(f"**推薦理由:** {recommendation_reason}")
        else:
            st.warning("❌ 該当する本が見つかりませんでした。別のキーワードを試してください。")
    else:
        st.info("🔍 検索ワードを入力してください。")
# # GPTに３つリクエストだしてもらう
# # chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定（書いてほしい内容、文章の種類、最大文字数を指定）
# def run_gpt(content_text_to_gpt,content_current_to_gpt,content_goal_to_gpt,content_others_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt):
#     # リクエスト内容を決める
#     request_to_gpt = content_text_to_gpt +"について学びたい。"+content_text_to_gpt +"に対する現在の理解度は"+content_current_to_gpt +"レベルです。"+content_text_to_gpt +"に対して"+content_goal_to_gpt+ "程度理解を深めたいと考えています。"+"今後の学習において、おすすめの本をランキング形式で3つ出力してください。おすすめの際に、理由を添えてください。また、おすすめにあたり参照した出典元のリンクを記載してください。その他、本の選定にあたっては、"+content_others_to_gpt + "を考慮してください。内容は"+ content_maxStr_to_gpt + "文字以内で出力してください。" + "また、文章は" + content_kind_of_to_gpt + "にしてください。"
#     # 検索ワードをGPTに入れこんだ内容から推測してもらって、検索ワードをGPTに考えてもらうのがよのがよさそう
#     # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "user", "content": request_to_gpt },
#         ],
#     )

#     # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
#     output_content = response.choices[0].message.content.strip()
#     return output_content # 返って来たレスポンスの内容を返す
