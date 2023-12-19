import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import os
import time
import numpy as np
from PIL import Image

if "chatHistory" not in st.session_state:
    st.session_state.chatHistory = []
    st.session_state.memberHistory = []
    st.session_state.judgeHistory = []
    st.session_state.turnList = []
    st.session_state.execInitProcess = False
    st.session_state.disable = False
    st.session_state.gameStatus = 0
    st.session_state.g_message = ""
    st.session_state.questionAndAnswer = ""
    st.session_state.question = ""
    st.session_state.model = ""
    st.session_state.client = ""
    st.session_state.quizLevel = ""
    st.session_state.knowledge = ""
    st.session_state.numOfMember = 1
    st.session_state.turn = 0
    st.session_state.gameStart = 0
    st.session_state.gameEnd = 0

nicknameList = [
            "ときのそら",
            "ロボ子さん",
            "さくらみこ",
            "星街すいせい",
            "AZKi",
            "夜空メル",
            "アキ・ローゼンタール",
            "赤井はあと",
            "白上フブキ",
            "夏色まつり",
            "湊あくあ",
            "紫咲シオン",
            "百鬼あやめ",
            "癒月ちょこ",
            "大空スバル",
            "大神ミオ",
            "猫又おかゆ",
            "戌神ころね",
            "兎田ぺこら",
            "不知火フレア",
            "白銀ノエル",
            "宝鐘マリン",
            "天音かなた",
            "角巻わため",
            "常闇トワ",
            "姫森ルーナ",
            "雪花ラミィ",
            "桃鈴ねね",
            "獅白ぼたん",
            "尾丸ポルカ",
            "ラプラス・ダークネス",
            "鷹嶺ルイ",
            "博衣こより",
            "沙花叉クロヱ",
            "風真いろは",
            "火威青",
            "音乃瀬奏",
            "一条莉々華",
            "儒烏風亭らでん",
            "轟はじめ"]

iconList = [
            "🐻",
            "🤖",
            "🌸",
            "☄️",
            "⚒️",
            "🌟",
            "🍎",
            "❤️",
            "🌽",
            "🏮",
            "⚓️",
            "🌙",
            "😈",
            "💋",
            "🚑",
            "🌲",
            "🍙",
            "🥐",
            "👯‍♀️",
            "🔥",
            "⚔️",
            "🏴‍☠️",
            "💫",
            "🐏",
            "👾",
            "🍬",
            "☃️",
            "🍑",
            "♌️",
            "🎪",
            "🛸",
            "🥀",
            "🧪",
            "🎣",
            "🍃",
            "🖋️",
            "🎹",
            "🌃",
            "🐚",
            "🐧"]

LEVEL_EASY = "初級"
LEVEL_NORMAL = "中級"
LEVEL_HARD = "上級"

GAME_STATUS_STOP = 0
GAME_STATUS_START = 1
GAME_STATUS_CLEAR = 2
GAME_STATUS_RETIRE = 3

YOUR_NAME = "あなた"
AI_NAME = "AIこより"

QUESTION_YES = 0
QUESTION_NO = 1
QUESTION_NOT_MATTER = 2
QUESTION_CLEAR = 3
QUESTION_RETIRE = 4

AIKoyoriImage = np.array(Image.open("./image/AIKoyori.png"))

def format_time(seconds):
    # 時間、分、秒に分割
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60

    # 時間の書式を hh:mm:ss.ss にフォーマット
    return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"

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
    st.title("AIこよりからの挑戦状　～水平思考クイズ～")
    
    showDescription = st.toggle('ゲームの説明を見る')
    if showDescription:
        st.write("このゲームは、#AIこよりと#ホロのウミガメから着想を得て作成しました。")
        st.write("ゲームを開始すると、AIこよりが水平思考クイズを出します。")
        st.write("テキストボックスに、「はい/いいえ/関係ない」で回答できる質問を入力してください。")
        st.write("想定された回答に沿った質問をすれば正解となり、あなたの勝ちです。")
        st.write("また、一人だけではなく、ホロメン（JP限定）を自由に選んでCPU対戦方式で遊ぶこともできます。")
        st.write("なお、リタイアしたい場合は、各種設定からリタイアを押すと回答が表示されます。")
        st.write("その他、このアプリに関する質問や連絡はこちらまで→必殺社畜人(X:@Jblx_xldLo0)")
        
    message = st.chat_input("質問を入力", disabled = not st.session_state.disable)
    
    if message:
        if st.session_state.gameStatus == GAME_STATUS_START:
            st.session_state.chatHistory.append(message)
            st.session_state.memberHistory.append(YOUR_NAME)
            st.session_state.g_message = message
        else:
            st.toast('ゲーム終了を押してください。', icon='😡')
    
    st.sidebar.title("各種設定")
    st.session_state.selectMemberList = st.sidebar.multiselect("ゲームに参加するメンバー", nicknameList, disabled = st.session_state.disable)
    st.sidebar.write(str(len(st.session_state.selectMemberList) + 1) + "人でプレイ")
    st.session_state.quizLevel = st.sidebar.radio("難易度", (LEVEL_EASY, LEVEL_NORMAL, LEVEL_HARD), disabled = st.session_state.disable)
    
    # ゲームの開始ボタン
    if st.sidebar.button("ゲーム開始", key=2, disabled = st.session_state.disable):
        st.session_state.numOfMember = len(st.session_state.selectMemberList)
        st.session_state.turnList.append(YOUR_NAME)
        st.session_state.turnList = st.session_state.turnList + st.session_state.selectMemberList
        st.session_state.gameStart = time.time()
        
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
        
    # ゲームの終了ボタン
    if st.sidebar.button("ゲーム終了", key=3, disabled = not st.session_state.disable):
        st.session_state.disable = False
        st.session_state.gameStatus = GAME_STATUS_STOP
        st.session_state.chatHistory = []
        st.session_state.memberHistory = []
        st.session_state.knowledge = ""
        st.session_state.judgeHistory = []
        st.session_state.turn = 0
        st.session_state.turnList = []
        st.rerun()
    
    # ゲームのリタイアボタン
    if st.session_state.disable:
        if st.sidebar.button("リタイア", key=5, disabled = not (st.session_state.gameStatus == GAME_STATUS_START)):
            if st.session_state.gameStatus == GAME_STATUS_START:
                st.session_state.gameStatus = GAME_STATUS_RETIRE
            else:
                st.toast('ゲーム終了を押してください。', icon='😡')
    
    # お題表示
    if st.session_state.disable:
        with st.chat_message(AI_NAME, avatar=AIKoyoriImage):
            st.write(AI_NAME)
            st.write(st.session_state.question)
    
    # チャット画面の表示
    count = 0
    judge = 0
    while len(st.session_state.chatHistory) > count:
        if st.session_state.memberHistory[count] == YOUR_NAME:
            with st.chat_message("user", avatar="🙍"):
                st.write(YOUR_NAME)
                st.write(st.session_state.chatHistory[count])
        elif st.session_state.memberHistory[count] == AI_NAME:
            with st.chat_message(AI_NAME, avatar=AIKoyoriImage):
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
        else:
            with st.chat_message("user", avatar=iconList[nicknameList.index(st.session_state.memberHistory[count])]):
                st.write(st.session_state.memberHistory[count])
                st.write(st.session_state.chatHistory[count])
        count = count + 1
    
    # プレイヤーの質問入力か、ゲーム参加者が質問したときの処理
    if count > 0 and st.session_state.gameStatus == GAME_STATUS_START and st.session_state.g_message != "":
        answer = st.session_state.model.generate_content("以下は、水平思考ゲームのお題とその回答です。" + st.session_state.questionAndAnswer + "\n\nこれを参照して、以下の質問に正しければ「はい。」、間違っていれば「いいえ。」、お題と回答に全く関係ない質問は「関係ありません。」のいずれかで回答してください。ただし、お題の回答と類似の意味の質問をした場合は「正解！」と出力してください。\n\n" + st.session_state.g_message)
        answerText = answer.text
        with st.chat_message(AI_NAME, avatar=AIKoyoriImage):
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
                
            st.session_state.knowledge = st.session_state.knowledge + st.session_state.g_message + "→" + answerText + "\n"
            
            # 正解の時以外は、負荷をかけないために2秒処理止めを入れる
            if answerText == "正解！":
                st.session_state.gameStatus = GAME_STATUS_CLEAR
                st.session_state.judgeHistory.append(QUESTION_CLEAR)
                if st.session_state.turnList[st.session_state.turn] == YOUR_NAME:
                    st.balloons()
                st.session_state.gameEnd = time.time() 
                formattedTime = format_time(st.session_state.gameEnd - st.session_state.gameStart)
                answerText = answerText + "お題と回答は以下の通りです。  \n  \n" + st.session_state.questionAndAnswer + "  \n  \n回答者:" + st.session_state.turnList[st.session_state.turn] + "  \n経過時間:" + formattedTime
                st.info(answerText)
            else:
                time.sleep(2)
        
            st.session_state.chatHistory.append(answerText)
            st.session_state.memberHistory.append(AI_NAME)
        
        # 正解がまだ出てないとき、順番の更新と、AIが質問を考えるかプレイヤーの番にするかを決める
        if st.session_state.gameStatus != GAME_STATUS_CLEAR:
            if st.session_state.turn < st.session_state.numOfMember:
                st.session_state.turn = st.session_state.turn + 1
                st.toast(st.session_state.selectMemberList[st.session_state.turn - 1] + "の番です。", icon=iconList[nicknameList.index(st.session_state.selectMemberList[st.session_state.turn - 1])])
                question = st.session_state.model.generate_content("以下は、水平思考ゲームのお題です。\n" + st.session_state.question + "\n\nこれに対して、「はい。」、「いいえ。」、「関係ありません。」のいずれかで回答できるような質問を考えて、正解を導くようにしてください。なお、現時点で既に質問されている内容と回答を以下に示すので、その内容を推測して答えを出すために不足している情報を補完するように質問してください。もしくは、情報が十分あると判断した場合は、「～したからですか？」のように理由を尋ねるような質問をしてください。\n\n・すでに分かっている情報\n" + st.session_state.knowledge)
                st.session_state.g_message = question.text
                st.session_state.chatHistory.append(st.session_state.g_message)
                st.session_state.memberHistory.append(st.session_state.selectMemberList[st.session_state.turn - 1])
                st.rerun()
            else:
                st.session_state.turn = 0
                st.session_state.g_message = ""
    
    # リタイアしたときは回答を表示、ゲーム中は誰の回答の番か表示する
    if st.session_state.gameStatus == GAME_STATUS_RETIRE:
        with st.chat_message(AI_NAME, avatar=AIKoyoriImage):
            st.write(AI_NAME)
            st.error("残念！今回のお題と回答は以下の通りです。またチャレンジしてね！  \n  \n" + st.session_state.questionAndAnswer)
    elif st.session_state.gameStatus == GAME_STATUS_START:
        if st.session_state.disable:
            st.toast(st.session_state.turnList[st.session_state.turn] + "の番です。")

if __name__ == "__main__":
    main()