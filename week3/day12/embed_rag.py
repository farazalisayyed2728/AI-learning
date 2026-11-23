import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

import numpy as np
from sentence_transformers import Sentence_Transformer

model = Sentence_Transformer("all-MiniLM-L6-v2")