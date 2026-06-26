import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate

from backend.backendConfig import CHROMA_DB_DIR

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.3,
)

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def generate_quiz_from_material(material_id: int, num_questions: int = 5):
    try:
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings_model
        )
        
        results = vectorstore.similarity_search(
            query="Key concepts, definitions, and main points from the course slides.", 
            k=15, 
            filter={"material_id": material_id}
        )
        
        if not results:
            return {"error": "No indexed texts found for this material. The file might be empty or not yet indexed by AI."}

        context_text = "\n\n".join([doc.page_content for doc in results])

        prompt_template = PromptTemplate.from_template(
            """
            You are an expert university professor. Based on the following extracted texts from course slides, 
            generate a multiple-choice quiz with {num_questions} questions.
            
            Your response MUST be ONLY valid JSON, with no markdown formatting like ```json, no intro, and no outro.
            Strictly follow this JSON array structure:
            [
                {{
                    "question": "The question text?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Brief explanation of why this is the correct answer based on the provided text."
                }}
            ]

            Reference Texts:
            {context}
            """
        )
        
        chain = prompt_template | llm
        response = chain.invoke({
            "num_questions": num_questions,
            "context": context_text
        })
        
        clean_json = response.content.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        quiz_data = json.loads(clean_json.strip())
        return quiz_data

    except Exception as e:
        print(f"[Quiz Generator Error]: {str(e)}")
        return {"error": f"An error occurred while generating the quiz: {str(e)}"}