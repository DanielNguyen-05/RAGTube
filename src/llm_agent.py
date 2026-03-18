# src/llm_agent.py
import os
import json
import numpy as np
import faiss
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

class CourseAssistant:
    def __init__(self, gemini_api_key, metadata_file="data/processed/chunks_metadata.json", index_file="data/vector_db/course_index.index"):
        genai.configure(api_key=gemini_api_key)
        self.llm = genai.GenerativeModel('gemini-flash-latest')
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load Data
        self.index = faiss.read_index(index_file)
        with open(metadata_file, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
    def ask(self, query, top_k=5):
        query_vector = self.embed_model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        
        context_text = ""
        sources = []
        
        for i in range(top_k):
            idx = indices[0][i]
            meta = self.metadata[idx]
            video_url = f"https://youtu.be/{meta['video_id']}?t={meta['start_time']}"
            context_text += f"[Nguồn {i+1} - {video_url}]:\n{meta['text']}\n\n"
            sources.append(video_url)
            
        prompt = f"""Bạn là một giáo sư phụ trách giải đáp thắc mắc cho khóa học này. 
Hãy trả lời câu hỏi chi tiết, dễ hiểu, CHỈ DỰA TRÊN các nội dung bài giảng dưới đây.

QUY TẮC:
- Nếu thông tin nằm ngoài bài giảng, hãy nói: "Dựa theo nội dung khóa học, tôi không tìm thấy thông tin này..."
- Luôn trích dẫn [Nguồn X] ngay sau ý đó.

[CÁC ĐOẠN TRÍCH TỪ BÀI GIẢNG]:
{context_text}

[CÂU HỎI]: {query}
"""
        response = self.llm.generate_content(prompt)
        return response.text, sources