# streamlit_frontend_threading.py
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def new_chat():
    st.session_state['thread_id'] = generate_thread_id()
    add_chat_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_chat_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_chat_thread(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_chat_thread(st.session_state['thread_id'])

st.sidebar.title('LangGraph Chatbot')
st.sidebar.button('New Chat', on_click=new_chat)
st.sidebar.header('Chat History')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_chat_thread(thread_id)

        temp_messages = []
        for message in messages:
            temp_messages.append({'role': message.type, 'content': message.content})
        st.session_state['message_history'] = temp_messages

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

     # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})