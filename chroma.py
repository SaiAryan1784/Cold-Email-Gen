import chromadb #vector database

# client = chromadb.Client()
# collection = client.create_collection(name="my_collection")

# collection.add(
#     documents=[
#         "This document is about New York",
#         "This document is about New Delhi"
#     ],
#     ids = ['id1', 'id2']
# )

# # all_docs = collection.get(ids=["id1"])
# # print(all_docs)

# result = collection.query(
#     query_texts=["Query is about cholle bhature"],
#     n_results=2
# )
# print(result)

client = chromadb.PersistentClient('vectorstore')
collection = client.get_or_create_collection(name="portfolio")

if not collection.count():
    for _, row in portfolio_data.iterrows():
        collection.add(documents=row["Techstack"],
                       metadatas={"links": row["Links"]},
                       ids=[str(uuid.uuid4())])