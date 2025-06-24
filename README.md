# reasoning-websearch

An AI reasoning agent that combines multiple Azure OpenAI models with web search capabilities to provide comprehensive answers to user queries. Built with LangGraph, LangChain, and Streamlit.

## Features

- **Multi-Model Reasoning**: Uses multiple Azure OpenAI models in parallel (GPT-4.1, Claude/Anthropic, Grok-3)
- **Web Search Integration**: Automatically generates search terms and retrieves relevant information from the web
- **Parallel Processing**: Processes multiple reasoning paths simultaneously for a comprehensive analysis
- **Secure Web Interface**: Streamlit-based UI with username/password authentication
- **Azure-Ready Deployment**: Includes scripts for easy deployment to Azure App Service

## Architecture

The agent uses a directed graph workflow with the following components:

1. **Input Processing**: The user query is analyzed to extract search terms
2. **Multiple Reasoning Paths**:
   - Direct reasoning with three different LLMs (o4-mini, o1, grok-3)
   - Web search using extracted search terms
3. **Information Synthesis**: Final integration of all reasoning paths into a comprehensive response

## Requirements

- Python 3.11+
- Azure OpenAI API access with the following deployments:
  - gpt-4.1
  - o4-mini (Claude models)
  - o1 (Claude models)
  - grok-3
- Google Custom Search API credentials

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file with the following variables:
   ```
   AZURE_OPENAI_API_KEY=your_azure_openai_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   ```

4. Configure authentication by editing secrets.toml (optional):
   ```toml
   [credentials]
   username = "your_username"
   password = "your_password"
   ```

## Running Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

The web interface will be available at http://localhost:8501

## Deploying to Azure App Service

The repository includes a deployment script that creates and configures an Azure App Service:

1. Package your application:
   ```bash
   zip -r ai.zip .
   ```

2. Run the deployment script:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

The script will:
- Create a resource group
- Create an App Service plan
- Create a Web App with Python runtime
- Configure startup command
- Deploy your application
- Restart the app

## Configuration

You can customize the following aspects:

- **LLM Models**: Change the Azure OpenAI deployments in the `init_chat_model` calls
- **System Prompts**: Modify the system prompts in each reasoning function
- **Authentication**: Update username/password in secrets.toml
- **UI**: Customize the Streamlit interface in the bottom section of app.py

## Project Structure

- app.py - Main application with LangGraph workflow and Streamlit UI
- gsearch.py - Google Search utility
- requirements.txt - Python dependencies

