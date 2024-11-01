from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210552959")
page_data = loader.load().pop().page_content

print(page_data)