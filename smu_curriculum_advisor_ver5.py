from openai import OpenAI
import streamlit as st
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

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

assistant_id_step = "asst_YJZVrh2sYDUVDy5cm42wErSM"
assistant_id_CDR = "asst_5p1sQz3NbaEt3T1LHzPm6dC2"
assistant_id_졸업 = "asst_oXS20SE2bYHHjZWf5cubRUmw"

google_api_key = st.secrets["google_api_key"]
openai_api_key = st.secrets["openai_api_key"]




if 'main_thread' not in st.session_state:
    st.session_state.main_thread = ""

# 상단에 고정된 부분
st.header("📝상명대 학습 어드바이저")
st.caption("학습자의 진로와 흥미에 기반한 맞춤형 커리큘럼 추천 챗봇")


# Sidebar for API keys and student ID input
with st.sidebar:
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
            st.session_state.main_thread = df.loc[df['학번'] == student_id, 'thread_id'].values[0]
            st.info('안녕하세요!')
        else:
            new_thread = client.beta.threads.create()
            st.session_state.main_thread = new_thread.id
            new_data = [student_id, st.session_state.main_thread]
            worksheet.append_row(new_data)
            st.info('처음뵙겠습니다.')

        # Retrieve all messages from the thread
        thread_messages = client.beta.threads.messages.list(st.session_state.main_thread)

        # Check if there are no messages and add a default bot message
        # if not thread_messages.data:
        #     default_message = client.beta.threads.messages.create(
        #         thread_id=st.session_state.main_thread,
        #         role="assistant",
        #         content=f"안녕하세요! {student_id}님 상명대학교 커리큘럼 어드바이저입니다. 주전공이 어떻게 되나요?😁"
        #     )
        #     thread_messages.data.append(default_message)

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
            old_data = [f'{student_id}_last', thread_id]
            worksheet.append_row(old_data)
            # Find and delete the row with the student_id
            for idx, record in enumerate(df.to_dict('records'), start=2):  # start=2 to skip header row
                if record['학번'] == student_id:
                    worksheet.delete_rows(idx)

        # Create a new thread
        new_thread = client.beta.threads.create()
        st.session_state.main_thread = new_thread.id

        # Update the new thread ID in Google Sheets
        new_data = [student_id, st.session_state.main_thread]
        worksheet.append_row(new_data)

        st.info('새로운 대화를 시작합니다.')

        # Retrieve all messages from the new thread
        thread_messages = client.beta.threads.messages.list(st.session_state.main_thread)

        # Check if there are no messages and add a default bot message
        # if not thread_messages.data:
        #     default_message = client.beta.threads.messages.create(
        #         thread_id=st.session_state.main_thread,
        #         role="assistant",
        #         content=f"안녕하세요! {student_id}님 상명대학교 커리큘럼 어드바이저입니다. 주전공이 어떻게 되나요?😁"
        #     )
        #     thread_messages.data.append(default_message)

        # Display the messages in reverse order
        for msg in reversed(thread_messages.data):
            with st.chat_message(msg.role):
                st.write(msg.content[0].text.value)

if start and 'main_thread' in st.session_state:
    # Display the messages in reverse order
    for msg in reversed(thread_messages.data):
        with st.chat_message(msg.role):
            st.write(msg.content[0].text.value)

# Input box to receive user input and generate a new message
prompt = st.chat_input("물어보고 싶은 것을 입력하세요!")
if prompt and 'main_thread' in st.session_state:
    if not student_id:
        st.info('학번을 입력해주세요')
        st.stop()

    message = client.beta.threads.messages.create(
        thread_id=st.session_state.main_thread,
        role="user",
        content=prompt
    )


    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.main_thread,
        assistant_id=assistant_id_step,
        
        
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

    msg_id = messages.data[0].id
    check_step = messages.data[0].content[0].text.value
    print(check_step)

    deleted_message = client.beta.threads.messages.delete(
        message_id=msg_id,
        thread_id=st.session_state.main_thread,
    )


    print('step')
    
    
    if '1' in check_step:
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.main_thread,
            assistant_id=assistant_id_졸업,
            #instructions="제공된 자료를 검색해서 답변해",
            #tools=[{"type": "file_search"}]
            
        )

        # Check if the run is completed every 0.5 seconds
        while run.status != "completed":
            print("status 확인 중", run.status)
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.main_thread,
                run_id=run.id
            )

        
        print('1')


    else:
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.main_thread,
            assistant_id=assistant_id_CDR,
            #instructions="제공된 자료를 검색해서 답변해",
            #tools=[{"type": "file_search"}]
            
        )

        # Check if the run is completed every 0.5 seconds
        while run.status != "completed":
            print("status 확인 중", run.status)
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.main_thread,
                run_id=run.id
            )

        print('2')
        

   
    # Retrieve and display the last message
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.main_thread
    )

    # Display all messages in reverse order
    for msg in reversed(messages.data):
        with st.chat_message(msg.role):
            st.write(msg.content[0].text.value)

    
    
