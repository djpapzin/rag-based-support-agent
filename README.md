# RAG-based Support Agent

A RAG (Retrieval-Augmented Generation) based support agent that learns from resolved Zendesk tickets to provide accurate responses to new support queries.

## Features

- Fetches resolved tickets from Zendesk
- Builds a knowledge base using RAG
- Processes open tickets and suggests responses
- Interactive mode for testing responses
- Environment variable configuration for sensitive data

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/djpapzin/rag-based-support-agent.git
   cd rag-based-support-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration values.

## Usage

1. Process resolved tickets to build knowledge base:
   ```bash
   python -m src.main
   ```

2. Enter interactive mode to test responses:
   ```bash
   python -m src.main --interactive
   ```

## Configuration

The following environment variables can be configured in `.env`:

- `ZENDESK_API_URL`: Your Zendesk API URL
- `ZENDESK_API_KEY`: Your Zendesk API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `HUGGINGFACE_API_KEY`: Your Hugging Face API key
- `VECTOR_STORE_PATH`: Path to store vector embeddings (default: "data/vector_store")

## License

MIT License 