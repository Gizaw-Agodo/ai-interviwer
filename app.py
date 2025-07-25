import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="OpenAI Chatbot", page_icon=":robot_face:")
st.title("Interview Chatbot")

st.session_state.setdefault("setup_complete", False)
st.session_state.setdefault("user_message_count", 0)
st.session_state.setdefault("feedback_shown", False)
st.session_state.setdefault("chat_completed", False)
st.session_state.setdefault("messages", [])

def complete_setup():
    st.session_state.setup_complete = True
def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete: 
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("experiance", "")
    st.session_state.setdefault("skills", "")
    st.session_state.setdefault("level", "Junior")
    st.session_state.setdefault("position", "Data Scientist")
    st.session_state.setdefault("company", "Amazon")
        

    st.subheader("personal information", divider = "rainbow")
    st.session_state.name = st.text_input("Name", max_chars = None , placeholder = "Enter your name here ...")
    st.session_state.experiance = st.text_area(label= "Experiance", value = "", height = None, max_chars = None, placeholder="Enter your experiance here...")
    st.session_state.skills = st.text_area(label= "Skills", value = "", height = None, max_chars = None, placeholder="Enter your skills here...")
    
    st.subheader("Company and Position Information", divider = "rainbow")
    col1, col2 = st.columns(2)
    with col1: 
        st.session_state.level = st.radio("Choose level", key = "visibility", options = ["Junior", "Mid-level", "Senior"])
    with col2:
        st.session_state.position = st.selectbox("Choose position", options = ["Data Scientist", "Data engineer", "ML Engineer ", "BI Analyst", "Financial Analyst"])
    st.session_state.company = st.selectbox("Choose company", options = ["Amazon", "Meta", "Udemy", "365 company", "Nestle", "Linkedin", "Spotify"])


if  not st.session_state.setup_complete and  st.button("Start interview", on_click=complete_setup) :
    st.write("Starting the interview...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_completed:
    st.info(""" Start by introducing yourself.""", icon="👋")
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if st.session_state.messages == []:  # type: ignore
        st.session_state.messages.append({ "role": "system", "content": ( f"You are an HR executive that interviewes an interviwee called {st.session_state['name']}" f"with experiance {st.session_state['experiance']} "  f"and slills {st.session_state['skills']}."  f"You should interview them for the position {st.session_state['position']} "  f"at the company {st.session_state['company']}" )})

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"

    for message in st.session_state.messages:  # type: ignore
        if message['role'] != "system":
            with st.chat_message(message["role"]): # type: ignore
                st.markdown(message["content"]) # type: ignore

    
    if st.session_state.user_message_count < 3 : 

        if prompt := st.chat_input("ask your question here...", max_chars = 1000):
            st.session_state.messages.append({ "role":"user" , "content" : prompt })  # type: ignore


            with st.chat_message("user"):
                st.markdown(prompt)
            
            if st.session_state.user_message_count < 2 : 
                with st.chat_message("assistant"):
                    st.markdown("...thinking...")
                    stream = client.chat.completions.create( # type: ignore
                        model=st.session_state.openai_model,
                        messages= [
                            { "role" : m["role"], "content" : m["content"] } for m in st.session_state.messages # type: ignore
                        ],
                        stream=True
                    )   
                    response = st.write_stream(stream) # type: ignore
                    st.session_state.messages.append({ "role":"assistant" , "content" : response })  # type: ignore
            st.session_state.user_message_count += 1
    if st.session_state.user_message_count >= 3:
        st.session_state.chat_completed = True
        st.success("Interview completed! Thank you for participating.", icon="✅")
        st.button("Show feedback", on_click=show_feedback)


if st.session_state.feedback_shown and st.session_state.chat_completed:
    st.subheader("Feedback", divider="rainbow")
    conversation_history = "\n".join(
        f"{message['role']}: {message['content']}" for message in st.session_state.messages  # type: ignore
    )

    st.write("generating feedback...")
    feedback_cleint = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    feedback_response = feedback_cleint.chat.completions.create(  # type: ignore
        model=st.session_state.openai_model,
        messages=[
            {"role": "system", "content": """
             You are an expert HR executive providing feedback on an interview.
             before the feedback , give a score of 1 to 10. 
             follow this format : 
             Overall Score: [score]
             Feedback: [feedback]
             Give only the feedback do not ask any additional question 
             """
            ""},
            {"role": "user", "content": f"Provide feedback on the following interview conversation:\n\n{conversation_history}"}
        ]
    )
    
    st.write(feedback_response.choices[0].message.content)  # type: ignore