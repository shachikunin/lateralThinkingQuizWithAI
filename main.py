import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import os
import time

if "chatHistory" not in st.session_state:
    st.session_state.chatHistory = []
    st.session_state.memberHistory = []
    st.session_state.judgeHistory = []
    st.session_state.execInitProcess = False
    st.session_state.disable = False
    st.session_state.gameStatus = 0
    st.session_state.g_message = ""
    st.session_state.questionAndAnswer = ""
    st.session_state.question = ""
    st.session_state.model = ""
    st.session_state.client = ""
    st.session_state.quizLevel = ""
    st.session_state.knowledge = []
    st.session_state.numOfMember = 1
    st.session_state.turn = 0

nicknameList = [
            "赤井はあと",
            "アキ・ローゼンタール",
            "天音かなた",
            "AZKi",
            "博衣こより",
            "姫森ルーナ",
            "火威青",
            "宝鐘マリン",
            "一条莉々華",
            "戌神ころね",
            "儒烏風亭らでん",
            "風真いろは",
            "ラプラス・ダークネス",
            "湊あくあ",
            "桃鈴ねね",
            "紫咲シオン",
            "百鬼あやめ",
            "夏色まつり",
            "猫又おかゆ",
            "尾丸ポルカ",
            "大神ミオ",
            "大空スバル",
            "音乃瀬奏",
            "ロボ子さん",
            "沙花叉クロヱ",
            "さくらみこ",
            "白上フブキ",
            "不知火フレア",
            "白銀ノエル",
            "獅白ぼたん",
            "星街すいせい",
            "鷹嶺ルイ",
            "轟はじめ",
            "ときのそら",
            "常闇トワ",
            "角巻わため",
            "兎田ぺこら",
            "夜空メル",
            "雪花ラミィ",
            "癒月ちょこ"]

iconList = [
            "❤️",
            "🍎",
            "💫",
            "⚒️",
            "🧪",
            "🍬",
            "🖋️",
            "🏴‍☠️",
            "🌃",
            "🥐",
            "🐚",
            "🍃",
            "🛸",
            "⚓️",
            "🍑",
            "🌙",
            "😈",
            "🏮",
            "🍙",
            "🎪",
            "🌲",
            "🚑",
            "🎹",
            "🤖",
            "🎣",
            "🌸",
            "🌽",
            "🔥",
            "⚔️",
            "♌️",
            "☄️",
            "🥀",
            "🐧",
            "🐻",
            "👾",
            "🐏",
            "👯‍♀️",
            "🌟",
            "☃️",
            "💋"]

LEVEL_EASY = "初級"
LEVEL_NORMAL = "中級"
LEVEL_HARD = "上級"

GAME_STATUS_STOP = 0
GAME_STATUS_START = 1
GAME_STATUS_CLEAR = 2
GAME_STATUS_RETIRE = 3

YOUR_NAME = "あなた"
AI_NAME = "AI"

QUESTION_YES = 0
QUESTION_NO = 1
QUESTION_NOT_MATTER = 2
QUESTION_CLEAR = 3
QUESTION_RETIRE = 4

def main():
    #アプリ起動時の処理、二重にロードしたくない処理はここで行う
    if st.session_state.execInitProcess == False:
        
        genai.configure(api_key = st.secrets.GoogleApiey.google_api_key)
        st.session_state.model = genai.GenerativeModel('gemini-pro')
        os.environ["OPENAI_API_KEY"] = st.secrets.GPT3ApiKey.api_key
        st.session_state.client = OpenAI()
        #初期化処理完了
        st.session_state.execInitProcess = True
    
    st.set_page_config(page_title="水平思考クイズ")
    st.title("水平思考クイズAI")
    
    showDescription = st.toggle('ゲームの説明を見る')
    if showDescription:
        st.write("ゲームを開始すると、AIが水平思考クイズを出します。")
        st.write("テキストボックスに、「はい/いいえ/関係ない」で回答できる質問を入力してください。")
        st.write("想定された回答に沿った質問をすれば正解となり、あなたの勝ちです。")
        st.write("なお、リタイアしたい場合は、各種設定からリタイアを押すと回答が表示されます。")
        
    message = st.chat_input("質問を入力", disabled = not st.session_state.disable)
    
    if message:
        if st.session_state.gameStatus == GAME_STATUS_START:
            st.session_state.chatHistory.append(message)
            st.session_state.memberHistory.append(YOUR_NAME)
            st.session_state.g_message = message
        else:
            st.toast('今はゲーム中ではありません。', icon='😡')
    
    st.sidebar.title("各種設定")
    #st.session_state.selectMemberList = st.sidebar.multiselect("ゲームに参加するメンバー", nicknameList, disabled = st.session_state.disable)
    #st.session_state.numOfMember = len(st.session_state.selectMemberList)
    st.session_state.quizLevel = st.sidebar.radio("難易度", (LEVEL_EASY, LEVEL_NORMAL, LEVEL_HARD), disabled = st.session_state.disable)
    if st.sidebar.button("ゲーム開始", key=2, disabled = st.session_state.disable):
        with st.spinner('問題作成中です...'):
            #questionAndAnswer = st.session_state.model.generate_content("水平思考ゲームのお題とその回答を一つ提案してください。")
            questionAndAnswer = st.session_state.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages = [
                    {"role": "user", 
                    "content": f"""ウミガメのスープのような水平思考クイズのお題とその回答を一つ提案してください。
                    ただし、以下の条件に従ってください。
                    
                    ・テーマは完全にランダム
                    ・難易度は{st.session_state.quizLevel}者向けの内容で作成すること。
                    ・お題と回答は、それぞれ一般的な道徳観、倫理観に則っていること。
                    ・お題だけを見ると、一見矛盾してるようなシチュエーションの文章であること。
                    ・回答は、起承転結を踏襲した内容であること。
                    ・出力形式は、「お題：...\n回答：...」という形で出力してください。"""
                    }],
                temperature=0.6,
            )
            st.session_state.questionAndAnswer = questionAndAnswer.choices[0].message.content
            st.session_state.question = st.session_state.questionAndAnswer.split('\n')[0]
        st.session_state.disable = True
        st.session_state.gameStatus = GAME_STATUS_START
        st.rerun()
    if st.sidebar.button("ゲーム終了", key=3, disabled = not st.session_state.disable):
        st.session_state.disable = False
        st.session_state.gameStatus = GAME_STATUS_STOP
        st.session_state.chatHistory = []
        st.session_state.memberHistory = []
        st.session_state.knowledge = []
        st.session_state.judgeHistory = []
        st.rerun()
    # if st.sidebar.button("履歴削除", key=4):
    #     st.session_state.chatHistory = []
    #     st.rerun()
    
    if st.session_state.disable:
        if st.sidebar.button("リタイア", key=5, disabled = not (st.session_state.gameStatus == GAME_STATUS_START)):
            if st.session_state.gameStatus == GAME_STATUS_START:
                st.session_state.gameStatus = GAME_STATUS_RETIRE
            else:
                st.toast('今はゲーム中ではありません。', icon='😡')
    
    if st.session_state.disable:
        #st.write(st.session_state.questionAndAnswer)
        with st.chat_message("ai"):
            st.write(st.session_state.question)
    
    count = 0
    judge = 0
    while len(st.session_state.chatHistory) > count:
        if st.session_state.memberHistory[count] == YOUR_NAME:
            with st.chat_message("user", avatar="🙍"):
                st.write(YOUR_NAME)
                st.write(st.session_state.chatHistory[count])
        elif st.session_state.memberHistory[count] == AI_NAME:
            with st.chat_message("ai"):
                st.write(AI_NAME)
                if st.session_state.judgeHistory[judge] == QUESTION_YES:
                    st.info(st.session_state.chatHistory[count])
                elif st.session_state.judgeHistory[judge] == QUESTION_NO:
                    st.error(st.session_state.chatHistory[count])
                elif st.session_state.judgeHistory[judge] == QUESTION_NOT_MATTER:
                    st.warning(st.session_state.chatHistory[count])
                elif st.session_state.judgeHistory[judge] == QUESTION_CLEAR:
                    st.info(st.session_state.chatHistory[count])
                elif st.session_state.judgeHistory[judge] == QUESTION_RETIRE:
                    st.error(st.session_state.chatHistory[count])
                judge = judge + 1
        count = count + 1
    
    if count > 0 and st.session_state.gameStatus == GAME_STATUS_START and st.session_state.g_message != "":
        answer = st.session_state.model.generate_content("以下は、水平思考ゲームのお題とその回答です。" + st.session_state.questionAndAnswer + "\n\nこれを参照して、以下の質問に正しければ「はい。」、正しくなければ「いいえ。」、問題解決に必要ない質問は「関係ありません。」のいずれかで回答してください。ただし、お題の回答と類似の意味の質問をした場合は「正解！」と出力してください。\n\n" + st.session_state.g_message)
        answerText = answer.text
        with st.chat_message("ai"):
            st.write(AI_NAME)
            if "はい" in answerText:
                st.info(answerText)
                st.session_state.judgeHistory.append(QUESTION_YES)
            elif "いいえ" in answerText:
                st.error(answerText)
                st.session_state.judgeHistory.append(QUESTION_NO)
            elif "関係" in answerText:
                st.warning(answerText)
                st.session_state.judgeHistory.append(QUESTION_NOT_MATTER)
                
            st.session_state.knowledge.append(st.session_state.g_message + "→" + answerText)
            #st.write(st.session_state.knowledge)
            if answerText == "正解！":
                st.session_state.gameStatus = GAME_STATUS_CLEAR
                st.session_state.judgeHistory.append(QUESTION_CLEAR)
                st.balloons()
                answerText = answerText + "お題と回答は以下の通りです。  \n  \n" + st.session_state.questionAndAnswer
                st.info(answerText)
        
            st.session_state.chatHistory.append(answerText)
            st.session_state.memberHistory.append(AI_NAME)
        
        st.session_state.g_message = ""
    
    if st.session_state.gameStatus == GAME_STATUS_RETIRE:
        with st.chat_message("ai"):
            st.write(AI_NAME)
            st.error("残念！今回のお題と回答は以下の通りです。またチャレンジしてね！  \n  \n" + st.session_state.questionAndAnswer)
        

if __name__ == "__main__":
    main()