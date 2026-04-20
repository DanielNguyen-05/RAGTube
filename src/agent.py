import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent # Thư viện Agent hệ mới
from langchain_core.messages import SystemMessage

from configs.system_prompts import AUDIT_AGENT_SYSTEM_PROMPT
from src.rag_engine import get_retriever

load_dotenv()

current_retriever = None 

def get_llm():
    endpoint = os.getenv("FPT_AI_LLM_ENDPOINT")
    base_url = endpoint.replace("/chat/completions", "")
    
    return ChatOpenAI(
        openai_api_key=os.getenv("FPT_AI_LLM_KEY"),
        openai_api_base=base_url,
        model_name=os.getenv("FPT_AI_LLM_MODEL"),
        temperature=0.0,
        max_retries=2
    )

@tool
def search_audit_documents(query: str) -> str:
    """Sử dụng công cụ này ĐẦU TIÊN để tra cứu số liệu, điều khoản, ngày tháng trong chứng từ đã upload."""
    global current_retriever
    if not current_retriever:
        return "Lỗi: Chưa có tài liệu nào được nạp vào hệ thống."
    
    docs = current_retriever.invoke(query)
    results = "\n\n---\n\n".join([f"[Nguồn - Trang {d.metadata.get('page', 'N/A')}]: {d.page_content}" for d in docs])
    return results

@tool
def calculate_financial_ratio(expression: str) -> str:
    """Công cụ máy tính. Dùng để tính toán các phép toán cộng, trừ, nhân, chia (VD: 1500 * 0.1)."""
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return f"Kết quả tính toán: {result}"
    except Exception as e:
        return f"Lỗi tính toán: {e}"

def create_audit_agent(faiss_path: str):
    """Tạo Agent bằng LangGraph"""
    global current_retriever
    current_retriever = get_retriever(faiss_path)
    
    llm = get_llm()
    tools = [search_audit_documents, calculate_financial_ratio]
    
    # Tiêm prompt nghiệp vụ vào hệ thống
    system_message = SystemMessage(content=AUDIT_AGENT_SYSTEM_PROMPT)
    
    # Tạo Agent LangGraph
    agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)
    return agent_executor