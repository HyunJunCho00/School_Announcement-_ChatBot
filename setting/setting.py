import os ,requests, numpy as np, re, pytz, nltk, spacy, time
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pinecone import Pinecone
from concurrent.futures import ThreadPoolExecutor
from langchain import hub
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from langchain.vectorstores import FAISS
from datetime import datetime
from langchain.schema.runnable import Runnable
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA
from langchain.schema.runnable import RunnableSequence, RunnableMap
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from konlpy.tag import Okt
from collections import defaultdict
from IPython.display import display, HTML
from rank_bm25 import BM25Okapi
from difflib import SequenceMatcher
from langchain_core.runnables import RunnableLambda
from tabulate import tabulate  # 표 형태로 정리
from langchain.schema import SystemMessage, HumanMessage
import google.generativeai as genai
from google.colab import userdata


# 코랩 보안 비밀에서 GEMINI_API_KEY를 불러와 환경 변수에 설정
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Gemini API key loaded and configured successfully!")
    except Exception as e:
        print(f"❌ Error configuring Gemini API: {e}")
        print("Please ensure your API key is valid.")
else:
    print("⚠️ GEMINI_API_KEY environment variable not found in Colab secrets or environment.")
    print("Please set the GEMINI_API_KEY in Colab secrets.")


# Pinecone API 키와 인덱스 이름 선언
if "PINECONE_API_KEY" not in os.environ:
    os.environ["PINECONE_API_KEY"] = userdata.get("PINECONE_API_KEY")
PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")
index_name = 'info'
# Pinecone API 설정 및 초기화
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(index_name)

def get_korean_time():
    return datetime.now(pytz.timezone('Asia/Seoul'))
