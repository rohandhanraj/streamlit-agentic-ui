import streamlit as st
import httpx
from uuid import uuid4
from datetime import datetime
from audio_recorder_streamlit import audio_recorder
from read_transcribe import *
from streamlit_float import *



# Float feature initialization
float_init()


def listen(audio_bytes):
    # Write the audio bytes to a file
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.wav"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = transcribe(webm_file_path)
    print(f'Transcript :: {transcript}')
    os.remove(webm_file_path)
    return transcript

def read_aloud(message):
    # Create mp3 file
    mp3_audio_path = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp3'
    gen_speech(message, mp3_audio_path)
    # Play mp3 file
    speak(mp3_audio_path)
    os.remove(mp3_audio_path)

def respond(llm, agent, query=None, file=None):
    
    url = "http://localhost:8000/stream_chat"
    data = {
                'user_id': 'UserId',
                'session_id': 'SessionId',
                'conversation_id': 'ConversationId',
                'llm': llm,
                'agent_name': agent,
                'query':  query,
            }
    
    headers = {
                # 'Content-Type': 'multipart/form-data',
                'accept': 'application/json'
              }
    
    request_kwargs = {
        'method': 'POST',
        'url': url,
        'headers': headers,
        'data': data,
        'timeout': 60
    }
    if file:
        request_kwargs |= {
            'files': {'file': (file.name, file.getvalue())}
        }


    with httpx.stream(**request_kwargs) as r:
        response = ""
        tool_calls = ""
        for chunk in r.iter_text():
            if '🛠️' in chunk or '🔵🔴🟡🟢' in chunk:
                yield chunk
                tool_calls += f'\n{chunk}'
            else:
                yield chunk
                response += chunk
        if tool_calls:
            st.session_state.messages.append({"role": "Tool Call", "avatar": "🛠️", "content": tool_calls})
        st.session_state.messages.append({"role": "ai", "content": response})
        st.session_state['generated'].append(response)


def stream_response(llm, agent, query=None, file=None):
    st.chat_message("ai").write_stream(respond(llm, agent, query, file))
    

def end_session():
    st.session_state.pop('messages')
    st.session_state.pop("generated")

def init_session():
    st.session_state['messages'] = []
    st.session_state['generated'] = []


st.logo(image='https://omodore.com/logo/home.png', link='https://omodore.com/')
st.header('Omodore Agent Chatbot')
st.caption("🚀 A Streamlit chatbot developed by Rohan Dhanraj Yadav.")


with st.sidebar:
    user_id = st.text_input(
        "Enter your name"
    )
    conversation_id = uuid4()
    session_id = f'{conversation_id}_{datetime.now()}'
    llm = st.selectbox(
        "Select a LLM",
        (
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "ollama/llama3.2"
            "ollama/llama3.2:1b",
            "ollama/llama3.2-vision",
            "ollama/nemotron-mini",
            "ollama/phi3:mini",
        )
    )

    agent = st.selectbox(
        "Select an Agent",
        (
            "Omodore Web Chat",
            "Health Care",
            "Sales",
            "Sales Analyst",
            "Hospitality",
            "Sales-cum-Hospitality",
            "Teaching",
            "Web Explorer"
        )
    )
    if st.button('Apply'):
        end_session()
        st.rerun()


if not 'messages' in st.session_state:
    init_session()
    welcome_note = ''.join(respond(llm, agent))


chat_container = st.container()

with chat_container:
    col1, col2 = st.columns([.94, .06])

with col1:
    query = st.chat_input(placeholder="Type your message and press Enter to send.")
                    
                    
with col2:
    audio_bytes = audio_recorder(
                                    text='',
                                    icon_size='2x',
                                    # auto_start=True,
                                    # key=f'speak_{st.session_state["input_message_key"]}'
                                )
file = st.file_uploader('📎', label_visibility='hidden')

if audio_bytes:
    query = listen(audio_bytes)


if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)
    stream_response(llm, agent, query, file)
    st.rerun()


for message in st.session_state.messages:
    st.chat_message(name=message['role'], avatar=message.get('avatar')).write(message['content'])

if st.button('🔊'):
    with st.spinner("Generating audio response..."):
        read_aloud(st.session_state['generated'][-1])

chat_container.float("bottom: 0rem;")