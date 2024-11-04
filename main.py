import os
import uuid
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import chromadb

# Load environment variables
load_dotenv()

# Streamlit app title
st.title("Cold Email Generator")

# Input fields
user_name = st.text_input("Enter your name")
url_input = st.text_input("Enter the job posting URL:")
submit_button = st.button("Submit")

# Load portfolio data
try:
    portfolio_data = pd.read_csv("resource/my_portfolio.csv")
except FileNotFoundError:
    st.error("Portfolio data file not found.")
    st.stop()

# Initialize JSON parser
json_parser = JsonOutputParser()

# Set up LLM with Groq API
groq_api = os.getenv('GROQ_API_KEY')
if not groq_api:
    st.error("Groq API key not found. Make sure it's set in the environment.")
    st.stop()

llm = ChatGroq(
    temperature=0,
    groq_api_key=groq_api,
    model_name="llama-3.1-70b-versatile",
)

# Function to generate cold email
def generate_cold_email(url, user):
    try:
        # Load job page content
        loader = WebBaseLoader(url)
        page_data = loader.load().pop().page_content

        # Define prompt for extracting job information
        prompt_extract = PromptTemplate.from_template(
            """
            ###SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ###INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format with fields such as role, experience, skills, and description.
            Only return valid JSON.
            """
        )

        # Extract job data in JSON format
        chain_extract = prompt_extract | llm
        res = chain_extract.invoke(input={'page_data': page_data})
        job_data = json_parser.parse(res.content)
    except Exception as e:
        st.error(f"Failed to extract job data: {e}")
        return None

    # Connect to ChromaDB and get relevant links
    client = chromadb.PersistentClient('vectorstore')
    collection = client.get_or_create_collection(name="portfolio")

    # Add portfolio data to the collection if it's not already added
    if not collection.count():
        for _, row in portfolio_data.iterrows():
            collection.add(
                documents=row["Techstack"],
                metadatas={"links": row["Links"]},
                ids=[str(uuid.uuid4())]
            )

    # Query for relevant portfolio links
    links = collection.query(query_texts=["Experience in Python"], n_results=2).get('metadatas', [])

    # Define prompt for generating cold email
    prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}
        
        ### INSTRUCTION:
        You are {user}, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
        the seamless integration of business processes through automated tools. 
        Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
        process optimization, cost reduction, and heightened overall efficiency. 
        Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
        in fulfilling their needs.
        Also add the most relevant ones from the following links to showcase AtliQ's portfolio: {link_list}
        Remember you are {user}, BDE at AtliQ. 
        Do not provide a preamble.
        ### EMAIL (NO PREAMBLE):
        """
    )

    # Generate the cold email
    chain_email = prompt_email | llm
    email_response = chain_email.invoke({
        "job_description": str(job_data),
        "link_list": links,
        "user": user
    })
    
    return email_response.content

# When the "Submit" button is clicked
if submit_button:
    if not url_input or not user_name:
        st.warning("Please fill out both the URL and your name.")
    else:
        with st.spinner("Generating cold email..."):
            # Generate and display cold email
            email_content = generate_cold_email(url_input, user_name)
            if email_content:
                st.subheader("Generated Cold Email")
                st.code(email_content, language="markdown")
