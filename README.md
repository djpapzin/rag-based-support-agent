# RAG-based Support Agent

A support agent that uses RAG (Retrieval Augmented Generation) to provide contextual responses based on historical support tickets.

## Features

- Fetches resolved tickets from Zendesk
- Builds a knowledge base using RAG
- Processes open tickets and suggests responses
- Interactive mode for testing responses
- Dynamic support user ID handling

## Setup

1. Clone the repository:
```bash
git clone https://github.com/L.fanampe/rag-based-support-agent.git
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
Edit the `.env` file with your API credentials and configuration.

## Usage

### Process Tickets
```bash
python -m src.main
```

### Interactive Mode
```bash
python -m src.main --interactive
```

## Configuration

The following environment variables can be configured in the `.env` file:

- `ZENDESK_API_URL`: Your Zendesk API URL
- `ZENDESK_API_KEY`: Your Zendesk API key
- `SUPPORT_USER_ID`: Default support user ID
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_API_HOST`: OpenRouter API host
- `LLM_MODEL`: Language model to use
- `EMBEDDINGS_MODEL`: Embeddings model to use

## License

MIT License 