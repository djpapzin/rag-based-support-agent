from typing import List, Dict, Any
import time
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.zendesk_client import ZendeskClient
from src.rag_system import RAGSystem

def process_resolved_tickets(zendesk: ZendeskClient, rag: RAGSystem) -> None:
    """Process resolved tickets to build the knowledge base."""
    print("Fetching resolved tickets from Zendesk...")
    tickets = zendesk.get_resolved_tickets()
    print(f"Found {len(tickets)} resolved tickets")
    
    # Get comments for each ticket
    all_comments = []
    print("\nFetching comments for each ticket...")
    for i, ticket in enumerate(tickets, 1):
        print(f"Processing ticket {i}/{len(tickets)} (ID: {ticket['id']})...")
        try:
            comments = zendesk.get_ticket_comments(ticket["id"])
            all_comments.extend(comments)
            print(f"Found {len(comments)} comments for ticket {ticket['id']}")
        except Exception as e:
            print(f"Error processing ticket {ticket['id']}: {str(e)}")
    
    print(f"\nTotal comments collected: {len(all_comments)}")
    print("Processing tickets and comments into knowledge base...")
    
    # Process tickets and comments
    rag.process_tickets(tickets, all_comments)
    print("Knowledge base updated successfully!")

def process_open_tickets(zendesk: ZendeskClient, rag: RAGSystem) -> None:
    """Process open tickets and add recommended responses."""
    print("\nFetching open tickets from Zendesk...")
    tickets = zendesk.get_open_tickets()
    print(f"Found {len(tickets)} open tickets")
    
    for i, ticket in enumerate(tickets, 1):
        print(f"\nProcessing open ticket {i}/{len(tickets)} (ID: {ticket['id']})...")
        # Generate response using RAG
        question = ticket.get("description", "")
        if not question:
            print(f"Skipping ticket {ticket['id']} - no description found")
            continue
            
        try:
            print("Generating response...")
            response = rag.generate_response(question)
            print("Adding response as comment...")
            # Add response as non-public comment
            zendesk.add_comment(ticket["id"], response, public=False)
            print(f"Response added to ticket {ticket['id']}")
        except Exception as e:
            print(f"Error processing ticket {ticket['id']}: {str(e)}")

def main():
    """Main application entry point."""
    print("\nInitializing Zendesk client and RAG system...")
    zendesk = ZendeskClient()
    rag = RAGSystem()
    
    try:
        # Clear existing knowledge base
        print("\nClearing existing knowledge base...")
        rag.clear_knowledge_base()
        print("Knowledge base cleared successfully!")
        
        # Process resolved tickets
        print("\nProcessing resolved tickets...")
        process_resolved_tickets(zendesk, rag)
        
        # Process open tickets
        print("\nProcessing open tickets...")
        process_open_tickets(zendesk, rag)
        
        print("\nSuccessfully completed processing all tickets!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Stack trace:")
        import traceback
        traceback.print_exc()

def interactive_mode():
    """Interactive mode for testing the RAG system."""
    print("\nInitializing RAG system...")
    rag = RAGSystem()
    
    # Check if we have data in the vector store
    try:
        # Try to get a sample document to check if we have data
        sample_docs = rag.vector_store.similarity_search("test", k=1)
        if sample_docs:
            print(f"\nFound existing knowledge base!")
        else:
            print("No existing knowledge base found. Loading historical data...")
            zendesk = ZendeskClient()
            process_resolved_tickets(zendesk, rag)
    except Exception as e:
        print(f"Warning: Could not access vector store: {str(e)}")
        print("The system will continue with limited knowledge.")
    
    print("\nWelcome to the Support Assistant!")
    print("Type 'exit' to quit")
    
    while True:
        question = input("\nEnter your question: ")
        if question.lower() == 'exit':
            break
            
        try:
            print("\nGenerating response...")
            response = rag.generate_response(question)
            print("\nResponse:", response)
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            print("Stack trace:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()