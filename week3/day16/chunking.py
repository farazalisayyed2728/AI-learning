from  langchain_text_splitters import(
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter
)

text = """
One evening, a young boy named Arjun was walking through a quiet forest when he noticed a small golden light shining beneath an old tree. Curious, he moved closer and discovered a tiny glowing lantern. 

As soon as he touched it, a mysterious voice whispered, "Your greatest wish will come true if you help someone in need." Arjun looked around and saw an injured bird lying near the tree. He gently picked it up, 

carried it home, and cared for it until it could fly again. The next morning, the lantern had disappeared, but Arjun felt something magical inside his heart. He realized that helping others was more rewarding than receiving any wish.
"""

#fixed sized chunk

fixed = CharacterTextSplitter(
    separator = "",
    chunk_size=100,
    chunk_overlap = 0
)

print("\n========== FIXED SIZE ==========")

for i , chunk in enumerate(fixed.split_text(text) , 1):
    print(f"\nChunk {i}: ")
    print(chunk)
    print("--------------------")




# 2.paragraph chunking

paragraph = CharacterTextSplitter(
    separator = "\n\n",
    chunk_size=100,
    chunk_overlap = 0
)

print("\n========== PARAGRAPH ==========")

for i , chunk in enumerate(paragraph.split_text(text) , 1):
    print(f"\nChunk {i}: ")
    print(chunk)
    print("--------------------")


# 3.RECURSIVE CHUNKING

recursive = CharacterTextSplitter(
    
    chunk_size=100,
    chunk_overlap = 20
)

print("\n========== RECURSIVE ==========")

for i , chunk in enumerate(recursive.split_text(text) , 1):
    print(f"\nChunk {i}: ")
    print(chunk)
    print("--------------------")
