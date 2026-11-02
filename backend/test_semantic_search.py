from services.semantic_search import search_lectures

question = input("Ask a question about your DBMS lecture: ")

results = search_lectures(question, limit=5)

print("\nTop matching lecture passages:\n")

if not results:
    print("No matching passages found.")
else:
    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Lecture:", result["lecture_title"])
        print("Chunk index:", result["chunk_index"])
        print("Similarity:", result["similarity"])
        print("Content:", result["chunk_text"][:500])
        print("-" * 70)