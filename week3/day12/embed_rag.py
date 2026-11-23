import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")
text ="Machine learning is fun."

def cosine_similarity(a , b):
    return np.dot(a , b) /(
        np.linalg.norm(a) * np.linalg.norm(b)
    )

# embedding= model.encode(text)
# print(embedding.shape)
# print(embedding[:10])



t1 = "there are 25 paid leaves"
t2 = "there are 24 vacation leaves"

v1 = model.encode(t1)
v2 = model.encode(t1)
print(cosine_similarity(v1 , v2))