import openai
import os
import shutil

# 환경 변수에서 API 키 읽어오기
api_key = os.environ.get('OPENAI_API_KEY')

# API 키가 존재하는지 확인
if not api_key:
    print("API 키를 찾을 수 없습니다.")
    quit()

openai.api_key = api_key

def translate(korean):
    # Define prompt for the model
    prompt_text = '''I'm trying to translate the .md file from Korean to English. At the header of the md file, there is a metadata like this:
                   
                   ---
                   title: "Unreal GAS Overview"
                   date: 2024-02-14T13:53:44+09:00
                   image: img/unreal.svg
                   
                   tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
                   categories: ["Unreal"]
                   series: ["Gameplay Ability System (GAS)"]
                   ---
                   
                   Please translate only the values of 'title', 'tags', 'categories', and 'series' into English without altering the structure.
                   After header, a Korean document body written in Markdown including header will be provided. Please translate its header and body into English.
                   Now, translate this following my instructions above : 
                   ''' + korean
    """
    Sends the prompt to OpenAI API using the chat interface and gets the model's response.
    """
    message = {
        'role': 'user',
        'content': prompt_text
    }

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[message],
        max_tokens=4096
    )

    chatbot_response = response.choices[0].message
    return chatbot_response.content

# 새로 푸시된 파일의 경로를 받아 번역 작업 수행
def translate_files(files):
    for file_path in files:
        print(file_path)
        if file_path and file_path.startswith('content') and file_path.endswith('.md'):
            with open(file_path, 'r', encoding='UTF-8') as file:
                korean_text = file.read()
            print('succeed to open file ' + file_path +'. try to translate...')
            translated_text = translate(korean_text)
            # 영어 파일 경로 생성
            english_file_path = file_path.replace('content/ko/', 'content/en/')
            # 디렉토리 생성
            os.makedirs(os.path.dirname(english_file_path), exist_ok=True)

            # img 디렉토리 경로 불러오기
            img_dir = os.path.join(os.path.dirname(file_path), 'img')
            # 영어 img 디렉토리 경로 생성
            english_img_dir = os.path.join(os.path.dirname(english_file_path), 'img')
            # img 디렉토리의 내용을 영어 img 디렉토리로 복사
            shutil.copytree(img_dir, english_img_dir, dirs_exist_ok=True) 

            print('succeed to translate. try to save translated file...')
            # 번역된 텍스트 저장
            with open(english_file_path, 'w', encoding='UTF-8') as file:
                file.write(translated_text)

# 스크립트 실행
if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        print('there are/is some/a file(s) that needs to be converted!!')
        files = sys.argv[1:]
        translate_files(files)
