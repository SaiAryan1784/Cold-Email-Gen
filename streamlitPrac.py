import streamlit as st

def hello():
    return "Hello"

st.title("Cold Email Generator")
url_input = st.text_input("Enter the job posting URL: ", value="https://jobs.nike.com/job/R-40212?from=job%20search%20funnel")
submit_button = st.button("Submit")

if submit_button:
    st.code(hello)

