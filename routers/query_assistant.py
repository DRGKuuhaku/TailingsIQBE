from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx
from .auth import get_current_user

# Create router for AI Query Assistant
router = APIRouter(prefix="/api/query-assistant", tags=["query-assistant"])

# Models for request and response
class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[dict]] = []

class QueryResponse(BaseModel):
    response: str
    
# Sample tailings management knowledge base
tailings_knowledge = [
    {
        "question": "What are tailings?",
        "answer": "Tailings are the materials left over after the process of separating the valuable fraction from the uneconomic fraction of an ore. They consist of a mixture of water, sand, clay, and residual minerals and chemicals from the extraction process."
    },
    {
        "question": "What is GISTM?",
        "answer": "GISTM stands for Global Industry Standard on Tailings Management. It was developed through a collaborative process involving the International Council on Mining and Metals (ICMM), the United Nations Environment Programme (UNEP), and the Principles for Responsible Investment (PRI). It aims to prevent catastrophic failures and improve the safety of tailings facilities worldwide."
    },
    {
        "question": "What are the key risks associated with tailings facilities?",
        "answer": "Key risks include structural failure leading to dam breaches, seepage of contaminated water into groundwater, dust emissions affecting air quality, long-term stability issues, and impacts on local communities and ecosystems. Climate change factors like increased rainfall or drought can exacerbate these risks."
    },
    {
        "question": "How often should tailings facilities be inspected?",
        "answer": "According to best practices and standards like GISTM, tailings facilities should undergo routine inspections daily to weekly (depending on risk classification), formal inspections monthly to quarterly, comprehensive reviews annually, and independent reviews every 3-5 years. High-risk facilities require more frequent monitoring."
    },
    {
        "question": "What monitoring technologies are used for tailings facilities?",
        "answer": "Modern monitoring technologies include piezometers for measuring water pressure, inclinometers for detecting movement, satellite InSAR for surface deformation, drone surveys, real-time sensors, automated data collection systems, water quality monitoring, and weather stations. These technologies enable early detection of potential issues."
    }
]

@router.post("/query", response_model=QueryResponse)
async def query_assistant(
    request: QueryRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Process a query to the AI assistant and return a response.
    In production, this would call an external LLM API like OpenAI.
    """
    try:
        # Simple keyword matching from knowledge base (for demo purposes)
        response = "I don't have specific information about that topic yet. In a production environment, this would connect to an LLM API like OpenAI's GPT to provide more comprehensive answers. Would you like to know about tailings management best practices or GISTM standards instead?"
        
        # Basic keyword matching
        user_query = request.query.lower()
        
        for item in tailings_knowledge:
            # Check if question keywords match
            question_keywords = item["question"].lower().split(' ')
            answer_keywords = item["answer"].lower().split(' ')
            
            matches_question = any(
                keyword.lower() in user_query 
                for keyword in question_keywords 
                if len(keyword) > 3
            )
            
            matches_answer = any(
                keyword.lower() in user_query 
                for keyword in answer_keywords 
                if len(keyword) > 3
            )
            
            if matches_question or matches_answer:
                response = item["answer"]
                break
        
        # In production, replace with actual LLM API call:
        # async with httpx.AsyncClient() as client:
        #     llm_response = await client.post(
        #         "https://api.openai.com/v1/chat/completions",
        #         headers={
        #             "Content-Type": "application/json",
        #             "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        #         },
        #         json={
        #             "model": "gpt-4",
        #             "messages": [
        #                 {"role": "system", "content": "You are a helpful assistant specializing in tailings management."},
        #                 *[{"role": msg["role"], "content": msg["content"]} for msg in request.conversation_history],
        #                 {"role": "user", "content": request.query}
        #             ],
        #             "temperature": 0.7
        #         },
        #         timeout=30.0
        #     )
        #     response_data = llm_response.json()
        #     response = response_data["choices"][0]["message"]["content"]
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
