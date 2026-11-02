
from services.embedding_service import generate_embedding

sample_text = "Database management systems organize and manage data."

embedding = generate_embedding(sample_text)

print("Embedding generated successfully!")
print("Number of dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
