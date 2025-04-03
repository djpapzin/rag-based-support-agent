from typing import List, Dict, Any
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from src.config import config

class RAGSystem:
    def __init__(self):
        print("Initializing embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDINGS_MODEL
        )
        
        # Ensure the persist directory exists
        print(f"Creating persist directory at {config.VECTOR_STORE_PATH}")
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        
        # Initialize the vector store with persistence
        print("Initializing vector store...")
        try:
            self.vector_store = Chroma(
                persist_directory=config.VECTOR_STORE_PATH,
                embedding_function=self.embeddings,
                collection_name="support_tickets"
            )
            print("Vector store initialized successfully")
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            raise
        
        print("Initializing LLM...")
        try:
            self.llm = ChatOpenAI(
                openai_api_key=config.OPENROUTER_API_KEY,
                openai_api_base=config.OPENROUTER_API_HOST,
                model_name=config.LLM_MODEL,
                temperature=0.7,
                max_tokens=1000
            )
            print("LLM initialized successfully")
        except Exception as e:
            print(f"Error initializing LLM: {str(e)}")
            raise

        print("Initializing text splitter...")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        print("Text splitter initialized successfully")

    def process_tickets(self, tickets: List[Dict[str, Any]], comments: List[Dict[str, Any]], zendesk_client: Any) -> None:
        """Process tickets and their comments to create the knowledge base."""
        documents = []
        
        # Get support user IDs
        support_ids = zendesk_client.get_support_user_ids()
        
        for ticket in tickets:
            # Get comments from support agents
            ticket_comments = [
                c for c in comments 
                if c["author_id"] in support_ids
            ]
            if not ticket_comments:
                continue
                
            # Get the first comment as the question
            question = ticket.get("description", "")
            
            # Get the support team's responses
            answers = [c["body"] for c in ticket_comments]
            
            # Create a document for each Q&A pair
            doc = Document(
                page_content=f"Question: {question}\nAnswer: {' '.join(answers)}",
                metadata={
                    "ticket_id": ticket["id"],
                    "status": ticket["status"]
                }
            )
            documents.append(doc)
        
        if documents:
            # Split documents if needed
            split_docs = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(split_docs)
            
            # Persist the changes
            self.vector_store.persist()

    def generate_response(self, question: str, k: int = 3) -> str:
        """Generate a response for a new question using RAG."""
        try:
            # Search for similar questions
            similar_docs = self.vector_store.similarity_search(question, k=k)
            
            if not similar_docs:
                return "I apologize, but I don't have enough context to provide a specific answer. Could you please provide more details about your question?"
            
            # Create context from similar documents
            context = "\n\n".join([doc.page_content for doc in similar_docs])
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful customer support agent. Use the following similar support 
                conversations to help answer the new question. Keep your response professional and concise.
                If the context doesn't contain relevant information, acknowledge that and ask for more details.
                
                Similar conversations:
                {context}
                """),
                ("user", "{question}")
            ])
            
            # Generate response
            chain = prompt | self.llm
            try:
                response = chain.invoke({
                    "context": context,
                    "question": question
                })
                if response and hasattr(response, 'content'):
                    return response.content
                else:
                    return "I apologize, but I encountered an error while generating the response. Please try again."
            except Exception as e:
                print(f"Error in LLM response: {str(e)}")
                return "I apologize, but I encountered an error while generating the response. Please try again."
                
        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try again."

    def clear_knowledge_base(self) -> None:
        """Clear the existing knowledge base."""
        try:
            # Delete the existing collection
            self.vector_store.delete_collection()
            
            # Reinitialize the vector store
            self.vector_store = Chroma(
                persist_directory=config.VECTOR_STORE_PATH,
                embedding_function=self.embeddings,
                collection_name="support_tickets"
            )
            
            # Persist the changes
            self.vector_store.persist()
        except Exception as e:
            print(f"Error in clear_knowledge_base: {str(e)}")
            raise 