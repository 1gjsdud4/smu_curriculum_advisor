from openai import OpenAI
import streamlit as st
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json


scope = 'https://spreadsheets.google.com/feeds'
json_keyfile_dict = {
    "type": "service_account",
    "project_id": "smu-curriculum-advisor",
    "private_key_id": "79d292e4d94542b2d1b8c2fa2453f883ce81cde2",
    "private_key": "",
    "client_email": "id-501@smu-curriculum-advisor.iam.gserviceaccount.com",
    "client_id": "117414229599963526193",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-501%40smu-curriculum-advisor.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

assistant_id_main = "asst_BWSKDg1ekVCIk56JC2rb8hlF"
assistant_id_json = "asst_3C7sJxwHxsm2oYx6PnCFO2MQ"


# OpenAI 및 Google API 키 설정
google_api_key = st.secrets["google_api_key"]
openai_api_key = st.secrets["openai_api_key"]

empty_data = {
    "name": "",
    "student_id": "",
    "hope_job": [],
    "skill": [],
    "curriculum": {
        "1 학기": [],
        "2 학기": [],
        "3 학기": [],
        "4 학기": [],
        "5 학기": [],
        "6 학기": [],
        "7 학기": [],
        "8 학기": []
    }
}


# Google 스프레드시트에 데이터를 업로드하는 함수
def upload_data_to_spreadsheet(name, student_id, thread_id, plan, conversation):
    # Google 스프레드시트에 업로드할 데이터를 JSON 문자열로 변환
    json_keyfile_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{google_api_key}\nnxoTuVtIiP953QNl84NkqkpdBxfiwM66xgddCKMVRpB2WQx4WC6iY29qvZqLK5Ml\nMv+Vfpcf38hDiwNPMueN7ISoYxDBhUgR+7j9kcYuJD4WmDFPScJLlvmuoVjMvI7C\n/s9sfyYKdNHhQPd0G30aB5jqW7vDkp7EOTilOmHkizO5XPE6oIt4sCE6wSzpiLsx\nC8dji9zIoWZFoZ11D3tkPXlzrVtoFqYKyz3SSH7KmD2G5vOQuTyNXN9Y/rRrnRyt\ntaAa8t7KQ7ldbp//oLtDLndNEwRFmMAOk5JBgr/eXQ0on+bOC+sKvZdd6HJQwgMD\nsNk2hKIDAgMBAAECggEAD7HIZ4hm1sNvahEbBpq1447qXDMpAW7fLJ385suajpXi\nsJk9I7l9sk5FjrTvJBzTu+2hruGv1rc0e4JF5xWcocOA9qojHJwe2g9lPFy9kVaF\nYKAyhLD9ieT6/M5gwfRURdn8bMU+9W4fj4cpwb4XkiWkmkixS8SnRCN1rx6+f8IT\n7g+NeUVHxK/Pa/Ir3TBCXTR2ifJxy5Be5IeGn1GuF2R6jnusinUdGIerJNYlDP7+\nIwAZv7dJlBAA61HJCe9S+Yj9qhSBEzOY7ZP/PFC1CI99RIwotBPv/1j608L9C73U\nP9/tVjCUEPYPeuNFhId+H41sOIY+lM/NxxmPo2mHUQKBgQDiAa2QZduWl7o6HgN8\ncIZCkPcZ1P24OCunr3iYil4/Ul1RdPlAd1sVv10C72iu4SyuzVwT9c+P2SSnJ3Uu\nwl+N22rDGjHz/vNSOB/cwMSfG7us8AY4tT2Do5zKA4NcTLuPRJgW1L+GuPP+MBMm\nPSJjc1Ihi879h6O8kr4V+8CIFQKBgQDbFJkoi30q542sHaGsRpUnz85qKGNJqBzv\nEfhQgSqorLstm7G/w8M+w+/6ri7TFD8FGqq5CJ0SNjaYz/VEAEzuGaMzr2+AB4pN\nVtQD17p1iSaf6/FxAM0ePZvHDcg6X73mq4zl5r/XWeAJDWfb0m2XCq9YpsCiwU0i\nMpe+2amvtwKBgC1FuMbcIIiiDCPoLzqWL87VyynZiJmGZvhIJhgoX4i/rwHKNMO9\nJPnOQ4t6+bVOVe0OJgu5icJ+9OCm/spHFW0NLu22KZt+zq8BnyBRXRGiNI4H5rcl\nVxUviRDOc1nh5RBl5TFtnJAYLIgWiT93r5PMXf9qSiRvL1Vu77TnoUGhAoGBANPW\nJQqJZmx4HgtRU6ULUup+C6+mgesU/XVFwP/HBgK3kv5U0BkHJ+GnAIM6rdg4eX9r\n+6yTYZ3cggpc+2HXkIuiiqZNetkncVm7HaLhlFBWX9y+/mUwSyZ0mA5viy62qR9E\nvicHanTHWNQn/EcYQBOOp2JnS1mU5AqvNP+75FIdAoGAKZRjd/wWZy4/CYSwICmx\n9mPS55ySeQ6BF4NLK6R5fTt/OQjXjbyR3EPqgBl/eaejDGlO8YG4EJ6FxBx86aBI\nzxo5G9f/5Zs2Bs5xSvyR87Ekg8+zhDjeTwE5Ir/6ZcgwRkrQkPmmAujDeSF8lwas\n3KHdDQ9AKL9OOyjDFrFC+Q0=\n-----END PRIVATE KEY-----\n"
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)
    gc = gspread.authorize(credentials)
    sheet_url = 'https://docs.google.com/spreadsheets/d/1Mw6ONEIrFJHum-TRsEVPFXr3CU6G-VxauGbzMA8n8_0/edit?gid=0#gid=0'
    doc = gc.open_by_url(sheet_url)
    worksheet = doc.worksheet('시트1')
    plan_json = json.dumps(plan, ensure_ascii=False) 
    conversation_json = json.dumps(conversation,ensure_ascii=False)
    # 해당 학번의 행을 찾아 데이터를 치환하거나 새로 추가
    
    # 학번을 찾아 해당 위치의 셀 가져오기
    cell = worksheet.find(student_id)

    # 학번이 있는 행에 데이터를 치환
    worksheet.update_cell(cell.row, 1, name)  # 이름 업데이트
    worksheet.update_cell(cell.row, 2, student_id)  # 학번 업데이트
    worksheet.update_cell(cell.row, 3, thread_id)  # thread_id 업데이트
    worksheet.update_cell(cell.row, 4, plan_json)
    worksheet.update_cell(cell.row, 5, conversation_json)  # plan JSON 업데이트

    st.rerun()





# 프롬프트를 st.session_state.plan 데이터와 결합하여 JSON 형태로 만드는 함수
def create_conversation_payload(prompt):
    # 기본 사용자 정보를 포함하는 JSON 구조 생성
    conversation_payload = {
        "conversation": prompt,  # 사용자가 입력한 질문
        "name": name,  # 사용자의 이름
        "student_id": student_id,  # 사용자의 학번
        "hope_job": st.session_state.plan.get("hope_job", []),  # 희망 직업 리스트
        "skill": st.session_state.plan.get("skill", []),  # 보유 스킬 리스트
        "curriculum": st.session_state.plan.get("curriculum", {})  # 학기별 커리큘럼
    }
    
    return conversation_payload
########### 화면 구성 ##############3


# 스트림릿 페이지 설정: 넓은 레이아웃 사용
st.set_page_config(layout="wide")

# 상단에 고정된 부분: 제목 및 설명
st.header("📝상명대 학습 어드바이저")
st.caption("학습자의 진로와 흥미에 기반한 맞춤형 커리큘럼 추천 챗봇, by 상명대 교육학과 이헌영")

# 페이지 레이아웃: 두 개의 열 (왼쪽: 대시보드, 오른쪽: 챗봇 인터페이스)
col1, col2 = st.columns([3, 1.5])  # 왼쪽 열을 3, 오른쪽 열을 1.5로 설정하여 챗봇 인터페이스 확장







############ 챗봇 #######################

# 사이드바: API 키 및 학번 입력을 위한 사용자 인터페이스
with st.sidebar:
    name = st.text_input("이름")
    student_id = st.text_input("학번")
    start = st.button("대화 시작")

    st.caption(f"thread: {st.session_state.main_thread if 'main_thread' in st.session_state else '없음'}")

    # Reset conversation button
    reset = st.button('새 대화')
    # Set API key
    client = OpenAI(api_key=openai_api_key)

    if start:
        # Google API 키 설정
        json_keyfile_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{google_api_key}\nnxoTuVtIiP953QNl84NkqkpdBxfiwM66xgddCKMVRpB2WQx4WC6iY29qvZqLK5Ml\nMv+Vfpcf38hDiwNPMueN7ISoYxDBhUgR+7j9kcYuJD4WmDFPScJLlvmuoVjMvI7C\n/s9sfyYKdNHhQPd0G30aB5jqW7vDkp7EOTilOmHkizO5XPE6oIt4sCE6wSzpiLsx\nC8dji9zIoWZFoZ11D3tkPXlzrVtoFqYKyz3SSH7KmD2G5vOQuTyNXN9Y/rRrnRyt\ntaAa8t7KQ7ldbp//oLtDLndNEwRFmMAOk5JBgr/eXQ0on+bOC+sKvZdd6HJQwgMD\nsNk2hKIDAgMBAAECggEAD7HIZ4hm1sNvahEbBpq1447qXDMpAW7fLJ385suajpXi\nsJk9I7l9sk5FjrTvJBzTu+2hruGv1rc0e4JF5xWcocOA9qojHJwe2g9lPFy9kVaF\nYKAyhLD9ieT6/M5gwfRURdn8bMU+9W4fj4cpwb4XkiWkmkixS8SnRCN1rx6+f8IT\n7g+NeUVHxK/Pa/Ir3TBCXTR2ifJxy5Be5IeGn1GuF2R6jnusinUdGIerJNYlDP7+\nIwAZv7dJlBAA61HJCe9S+Yj9qhSBEzOY7ZP/PFC1CI99RIwotBPv/1j608L9C73U\nP9/tVjCUEPYPeuNFhId+H41sOIY+lM/NxxmPo2mHUQKBgQDiAa2QZduWl7o6HgN8\ncIZCkPcZ1P24OCunr3iYil4/Ul1RdPlAd1sVv10C72iu4SyuzVwT9c+P2SSnJ3Uu\nwl+N22rDGjHz/vNSOB/cwMSfG7us8AY4tT2Do5zKA4NcTLuPRJgW1L+GuPP+MBMm\nPSJjc1Ihi879h6O8kr4V+8CIFQKBgQDbFJkoi30q542sHaGsRpUnz85qKGNJqBzv\nEfhQgSqorLstm7G/w8M+w+/6ri7TFD8FGqq5CJ0SNjaYz/VEAEzuGaMzr2+AB4pN\nVtQD17p1iSaf6/FxAM0ePZvHDcg6X73mq4zl5r/XWeAJDWfb0m2XCq9YpsCiwU0i\nMpe+2amvtwKBgC1FuMbcIIiiDCPoLzqWL87VyynZiJmGZvhIJhgoX4i/rwHKNMO9\nJPnOQ4t6+bVOVe0OJgu5icJ+9OCm/spHFW0NLu22KZt+zq8BnyBRXRGiNI4H5rcl\nVxUviRDOc1nh5RBl5TFtnJAYLIgWiT93r5PMXf9qSiRvL1Vu77TnoUGhAoGBANPW\nJQqJZmx4HgtRU6ULUup+C6+mgesU/XVFwP/HBgK3kv5U0BkHJ+GnAIM6rdg4eX9r\n+6yTYZ3cggpc+2HXkIuiiqZNetkncVm7HaLhlFBWX9y+/mUwSyZ0mA5viy62qR9E\nvicHanTHWNQn/EcYQBOOp2JnS1mU5AqvNP+75FIdAoGAKZRjd/wWZy4/CYSwICmx\n9mPS55ySeQ6BF4NLK6R5fTt/OQjXjbyR3EPqgBl/eaejDGlO8YG4EJ6FxBx86aBI\nzxo5G9f/5Zs2Bs5xSvyR87Ekg8+zhDjeTwE5Ir/6ZcgwRkrQkPmmAujDeSF8lwas\n3KHdDQ9AKL9OOyjDFrFC+Q0=\n-----END PRIVATE KEY-----\n"
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)
        gc = gspread.authorize(credentials)
        sheet_url = 'https://docs.google.com/spreadsheets/d/1Mw6ONEIrFJHum-TRsEVPFXr3CU6G-VxauGbzMA8n8_0/edit?gid=0#gid=0'
        doc = gc.open_by_url(sheet_url)
        worksheet = doc.worksheet('시트1')
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])

        # Check if student_id is in the DataFrame and get thread_id
        if student_id in df['학번'].values:
            matched_row = df[(df['학번'] == student_id) & (df['이름'] == name)]
            if not matched_row.empty:
                st.session_state.main_thread = matched_row['thread_id'].values[0]
                a = matched_row['학생_커리큘럼'].values[0]
                b= matched_row['conversation'].values[0]
                st.session_state.plan = json.loads(a)
                st.session_state.conversation_history = json.loads(b)
                st.info('안녕하세요!')
            else:
                st.warning('학번 또는 이름이 일치하지 않습니다.')
        else:
            new_thread = client.beta.threads.create()
            st.session_state.main_thread = new_thread.id
            st.session_state.plan = empty_data
            st.session_state.conversation_history = []
            new_data = [name, student_id, st.session_state.main_thread, json.dumps(st.session_state.plan, ensure_ascii=False),json.dumps(st.session_state.conversation_history, ensure_ascii=False)]
            worksheet.append_row(new_data)
            st.info('처음뵙겠습니다.')

        # Retrieve all messages from the thread, 
        thread_messages = client.beta.threads.messages.list(st.session_state.main_thread)

        # Check if there are no messages and add a default bot message
        if not thread_messages.data:
            default_content = f"안녕하세요! {name}님! 상명대학교 커리큘럼 어드바이저입니다. 저는 여러분의 진로와 흥미에 기반한 맞춤형 커리큘럼을 추천해드립니다.😁 수강계획을 세워볼까요?"
            default_message = client.beta.threads.messages.create(
                thread_id=st.session_state.main_thread,
                role="assistant",
                content= default_content
            )
            thread_messages.data.append(default_message)

            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": default_content
            })
            upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
            


# 대화를 저장할 리스트가 있는지 확인하고, 없으면 초기화
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []  

# 오른쪽 열: 챗봇 인터페이스
with col2.container(height=650):
    st.subheader("챗봇 인터페이스")
    with st.container(height=500):
        

        
        if reset:
            if 'main_thread' in st.session_state:
                # Google API key 설정
                json_keyfile_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{google_api_key}\nnxoTuVtIiP953QNl84NkqkpdBxfiwM66xgddCKMVRpB2WQx4WC6iY29qvZqLK5Ml\nMv+Vfpcf38hDiwNPMueN7ISoYxDBhUgR+7j9kcYuJD4WmDFPScJLlvmuoVjMvI7C\n/s9sfyYKdNHhQPd0G30aB5jqW7vDkp7EOTilOmHkizO5XPE6oIt4sCE6wSzpiLsx\nC8dji9zIoWZFoZ11D3tkPXlzrVtoFqYKyz3SSH7KmD2G5vOQuTyNXN9Y/rRrnRyt\ntaAa8t7KQ7ldbp//oLtDLndNEwRFmMAOk5JBgr/eXQ0on+bOC+sKvZdd6HJQwgMD\nsNk2hKIDAgMBAAECggEAD7HIZ4hm1sNvahEbBpq1447qXDMpAW7fLJ385suajpXi\nsJk9I7l9sk5FjrTvJBzTu+2hruGv1rc0e4JF5xWcocOA9qojHJwe2g9lPFy9kVaF\nYKAyhLD9ieT6/M5gwfRURdn8bMU+9W4fj4cpwb4XkiWkmkixS8SnRCN1rx6+f8IT\n7g+NeUVHxK/Pa/Ir3TBCXTR2ifJxy5Be5IeGn1GuF2R6jnusinUdGIerJNYlDP7+\nIwAZv7dJlBAA61HJCe9S+Yj9qhSBEzOY7ZP/PFC1CI99RIwotBPv/1j608L9C73U\nP9/tVjCUEPYPeuNFhId+H41sOIY+lM/NxxmPo2mHUQKBgQDiAa2QZduWl7o6HgN8\ncIZCkPcZ1P24OCunr3iYil4/Ul1RdPlAd1sVv10C72iu4SyuzVwT9c+P2SSnJ3Uu\nwl+N22rDGjHz/vNSOB/cwMSfG7us8AY4tT2Do5zKA4NcTLuPRJgW1L+GuPP+MBMm\nPSJjc1Ihi879h6O8kr4V+8CIFQKBgQDbFJkoi30q542sHaGsRpUnz85qKGNJqBzv\nEfhQgSqorLstm7G/w8M+w+/6ri7TFD8FGqq5CJ0SNjaYz/VEAEzuGaMzr2+AB4pN\nVtQD17p1iSaf6/FxAM0ePZvHDcg6X73mq4zl5r/XWeAJDWfb0m2XCq9YpsCiwU0i\nMpe+2amvtwKBgC1FuMbcIIiiDCPoLzqWL87VyynZiJmGZvhIJhgoX4i/rwHKNMO9\nJPnOQ4t6+bVOVe0OJgu5icJ+9OCm/spHFW0NLu22KZt+zq8BnyBRXRGiNI4H5rcl\nVxUviRDOc1nh5RBl5TFtnJAYLIgWiT93r5PMXf9qSiRvL1Vu77TnoUGhAoGBANPW\nJQqJZmx4HgtRU6ULUup+C6+mgesU/XVFwP/HBgK3kv5U0BkHJ+GnAIM6rdg4eX9r\n+6yTYZ3cggpc+2HXkIuiiqZNetkncVm7HaLhlFBWX9y+/mUwSyZ0mA5viy62qR9E\nvicHanTHWNQn/EcYQBOOp2JnS1mU5AqvNP+75FIdAoGAKZRjd/wWZy4/CYSwICmx\n9mPS55ySeQ6BF4NLK6R5fTt/OQjXjbyR3EPqgBl/eaejDGlO8YG4EJ6FxBx86aBI\nzxo5G9f/5Zs2Bs5xSvyR87Ekg8+zhDjeTwE5Ir/6ZcgwRkrQkPmmAujDeSF8lwas\n3KHdDQ9AKL9OOyjDFrFC+Q0=\n-----END PRIVATE KEY-----\n"
                
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)
                gc = gspread.authorize(credentials)
                sheet_url = 'https://docs.google.com/spreadsheets/d/1Mw6ONEIrFJHum-TRsEVPFXr3CU6G-VxauGbzMA8n8_0/edit?gid=0#gid=0'
                doc = gc.open_by_url(sheet_url)
                worksheet = doc.worksheet('시트1')
                data = worksheet.get_all_values()
                df = pd.DataFrame(data[1:], columns=data[0])

                # Check if student_id is in the DataFrame and get thread_id
                if student_id in df['학번'].values:
                    thread_id = df.loc[df['학번'] == student_id, 'thread_id'].values[0]
                    # Save the old thread ID with a '_last' suffix
                    thread_count = (df['이름'] == name).sum()
                    old_data = [name, f'{student_id}_{thread_count}', thread_id, json.dumps(st.session_state.plan, ensure_ascii=False), json.dumps(st.session_state.conversation_history, ensure_ascii=False)]
                    worksheet.append_row(old_data)
                    # Find and delete the row with the student_id
                    for idx, record in enumerate(df.to_dict('records'), start=2):  # start=2 to skip header row
                        if record['학번'] == student_id:
                            worksheet.delete_rows(idx)

                # Create a new thread
                new_thread = client.beta.threads.create()
                st.session_state.main_thread = new_thread.id
                st.session_state.conversation_history = []

                # Update the new thread ID in Google Sheets
                new_data = [name, student_id, st.session_state.main_thread, json.dumps(st.session_state.plan, ensure_ascii=False), json.dumps(st.session_state.conversation_history, ensure_ascii=False)]
                worksheet.append_row(new_data)

                st.info('새로운 대화를 시작합니다.')

                # Retrieve all messages from the new thread
                thread_messages = client.beta.threads.messages.list(st.session_state.main_thread)

                # Check if there are no messages and add a default bot message
                if not thread_messages.data:
                    default_content = f"안녕하세요! {name}님 상명대학교 커리큘럼 어드바이저입니다. 저는 여러분의 진로와 흥미에 기반한 맞춤형 커리큘럼을 추천해드립니다.😁 수강계획을 세워볼까요?"
                    default_message = client.beta.threads.messages.create(
                        thread_id=st.session_state.main_thread,
                        role="assistant",
                        content= default_content
                    )
                    thread_messages.data.append(default_message)
                    
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": default_content
                    })
                    upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
            
        

    
    # 대화 내용 업데이트
        for msg in st.session_state.conversation_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    with st.container():
        # Input box to receive user input and generate a new message
        prompt = st.chat_input("물어보고 싶은 것을 입력하세요!")
        if prompt and 'main_thread' in st.session_state:
            if not student_id:
                st.info('학번을 입력해주세요')
                st.stop()
            
            conversation_payload = create_conversation_payload(prompt)
            
            # 사용자 메시지 생성 및 리스트에 추가
            st.session_state.conversation_history.append({
                "role": "user",
                "content": prompt
            })

            message = client.beta.threads.messages.create(
                thread_id=st.session_state.main_thread,
                role="user",
                content= json.dumps(conversation_payload, ensure_ascii=False)
            )


            # 기본 대화  assistant 
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.main_thread,
                assistant_id=assistant_id_main,
                
            )

            # Check if the run is completed every 0.5 seconds
            while run.status != "completed":
                print("status 확인 중", run.status)
                time.sleep(0.5)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.main_thread,
                    run_id=run.id
                )


            # 메시지를 가져와 첫 번째 어시스턴트 응답만 리스트에 추가
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.main_thread
            )

            if messages.data:
                assi = messages.data[0].content[0].text.value
                print(assi)

            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": assi
            })




            # 대화를 json으로  변환 assistant 
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.main_thread,
                assistant_id=assistant_id_json,   
            )

            

            # Check if the run is completed every 0.5 seconds
            while run.status != "completed":
                print("status 확인 중", run.status)
                time.sleep(0.5)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.main_thread,
                    run_id=run.id
                )

            # Retrieve and display the last message
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.main_thread
            )
            
            if messages.data:
                plan_assistant = messages.data[0].content[0].text.value
                print(plan_assistant)

            if plan_assistant:
            
                # JSON 파싱
                response_data = json.loads(plan_assistant)
                
                # "change" 값이 1인지 확인
                if int(response_data.get("change")) == 1:
                    # 나머지 데이터를 st.session_state.plan에 저장
                    st.session_state.plan["name"] = response_data.get("name", "")
                    st.session_state.plan["student_id"] = response_data.get("student_id", "")
                    st.session_state.plan["hope_job"] = response_data.get("hope_job", [])
                    st.session_state.plan["skill"] = response_data.get("skill", [])
                    st.session_state.plan["curriculum"] = response_data.get("curriculum", {})
                    
                    st.success("변경 사항이 적용되었습니다.")

                upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)


                    
        

############## 학습경로 설계 ######################
    

# 데이터 파일 경로
file_path = 'data/curriculum.csv'

# CSV 파일을 읽어오기
df = pd.read_csv(file_path)


# 수강 계획 데이터를 유지하기 위한 session state 초기화
if 'plan' not in st.session_state:
    st.session_state.plan = empty_data.copy()

# 학과 목록 생성 (중복 제거)
departments = df['학부(과)'].unique().tolist()

# "과목명 (학수번호)" 형식의 리스트 생성
course_options = [f"{row['교과목명']} ({row['학수번호']})" for index, row in df.iterrows()]




# 수강 계획 대시보드 UI 구성
with col1.container(height=650):
    st.header("대학교 강의 수강 계획")

    # 희망 직업 입력 및 삭제
    col_hope_job, col_input, col_add_button = st.columns([2, 6, 1])
    
    with col_hope_job:
        st.subheader("희망 직업")
    with col_input:
        hope_job_input = st.text_input("새로운 희망 직업을 입력하세요", value="", label_visibility="collapsed", key="hope_job_input")
    with col_add_button:
        if st.button("➕", key="add_hope_job_button"):
            if hope_job_input and hope_job_input not in st.session_state.plan['hope_job']:
                st.session_state.plan['hope_job'].append(hope_job_input)
                upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)

    # 희망 직업 리스트와 제거 버튼
    if st.session_state.plan['hope_job']:
        for job in st.session_state.plan['hope_job']:
            col_job, col_button = st.columns([4, 0.5])
            with col_job:
                st.write(job)
            with col_button:
                if st.button("➖", key=f"remove_job_{job}"):
                    st.session_state.plan['hope_job'].remove(job)
                    upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
        
        
    else:
        st.write("희망 직업이 없습니다.")

    # 스킬 입력 및 삭제
    col_skill, col_skill_input, col_skill_button = st.columns([2, 6, 1])
    
    with col_skill:
        st.subheader("역량")
    with col_skill_input:
        new_skill_input = st.text_input("새로운 역량을 입력하세요", value="", label_visibility="collapsed", key="new_skill_input")
    with col_skill_button:
        if st.button("➕", key="add_skill_button"):
            if new_skill_input and new_skill_input not in st.session_state.plan['skill']:
                st.session_state.plan['skill'].append(new_skill_input)
                upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
    

    # 스킬 리스트와 제거 버튼
    if st.session_state.plan['skill']:
        for skill in st.session_state.plan['skill']:
            col_skill, col_button = st.columns([4, 0.5])
            with col_skill:
                st.write(skill)
            with col_button:
                if st.button("➖", key=f"remove_skill_{skill}"):
                    st.session_state.plan['skill'].remove(skill)
                    upload_data_to_spreadsheet(name, student_id, st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
                    st.rerun()
                
    else:
        st.write("보유 스킬이 없습니다.")
    # 학기별 수강 계획 표시
    for semester, courses in st.session_state.plan['curriculum'].items():
        st.subheader(semester)
        for course_code in courses:
            course_info = df[df['학수번호'] == course_code]
            if not course_info.empty:
                course_name = course_info['교과목명'].values[0]
                display_name = f"{course_name} ({course_code})"
            else:
                display_name = course_code  # 학수번호만 표시
                course_info = None

            col_course, col_button = st.columns([4, 0.5])
            with col_course:
                if course_info is not None:
                    with st.expander(display_name):  
                        st.write(course_info.to_dict('records')[0])  # 모든 세부 정보 출력
                else:
                    st.write(display_name)
            with col_button:
                if st.button("➖", key=f"remove_{semester}_{course_code}"):  # '-' 아이콘으로 오른쪽에 배치
                    st.session_state.plan['curriculum'][semester].remove(course_code)
                    upload_data_to_spreadsheet(name,student_id,st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
                    
            
                    

    with st.expander('과목추가'):

        # 학과 선택
        selected_department = st.selectbox("학과를 선택하세요", ["모든 학과"] + departments)
        
        # 선택한 학과로 과목 필터링
        if selected_department != "모든 학과":
            filtered_df = df[df['학부(과)'] == selected_department]
        else:
            filtered_df = df

        # 과목명 (학수번호) 형식의 리스트 생성
        course_options = [f"{row['교과목명']} ({row['학수번호']})" for index, row in filtered_df.iterrows()]

        # 과목 추가 기능
        selected_semester = st.selectbox("과목을 추가할 학기를 선택하세요", list(st.session_state.plan['curriculum'].keys()))
        
        # 과목명 (학수번호) 선택지에서 선택하도록 설정
        selected_course_display = st.selectbox("추가할 과목을 선택하세요", course_options)
        
        # 사용자가 선택한 과목에서 학수번호 추출
        selected_course_code = selected_course_display.split('(')[-1].strip(')')

        # 선택한 과목의 세부 정보 표시
        selected_course_info = df[df['학수번호'] == selected_course_code]
        if not selected_course_info.empty:
            selected_course_name = selected_course_info['교과목명'].values[0]
            st.write(f"**{selected_course_name} ({selected_course_code}) 세부 정보**:")
            st.write(selected_course_info.to_dict('records')[0])
        else:
            st.write("선택한 과목의 정보가 없습니다.")

        if st.button("과목 추가"):
            if selected_course_code not in st.session_state.plan['curriculum'][selected_semester]:
                st.session_state.plan['curriculum'][selected_semester].append(selected_course_code)
                upload_data_to_spreadsheet(name,student_id,st.session_state.main_thread, st.session_state.plan, st.session_state.conversation_history)
                
 # 페이지를 다시 로드하여 변경사항 반영