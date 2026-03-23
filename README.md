# AI & LLM Playground 🤖🚀

A comprehensive multi-provider LLM experimentation platform and agentic framework. This project allows you to interact with various Large Language Models (Gemini, Groq, Mistral, OpenRouter) and deploy specialized agents powered by **LangGraph** and **LangChain**.

## 🏗 Project Structure

- `app/agents/`: Core logic for LangGraph-powered agents.
    - `base.py`: Multi-provider LLM factory and agent builder.
    - `runner.py`: Orchestrates agent execution and handles response formatting.
    - `presets/`: Specialized agent configurations (`coder.py`, `research.py`).
- `app/routers/`: FastAPI route definitions.
    - `agents.py`: Endpoints for listing presets and running agents.
    - `gemini.py`, `groq.py`, `mistral.py`, `openrouter.py`: Direct LLM service endpoints.
- `app/services/`: Business logic for interacting with various LLM providers.
- `app/tools/`: A centralized registry for tools that agents can use.
    - `system/`: Tools for math, file I/O, Python execution, etc.
    - `web/`: Tools for web search, scraping, weather, etc.
- `app/config.py`: Configuration management using Pydantic Settings.

---

## 🤖 Agents & Presets

The platform includes specialized agents that can use the tool registry to solve complex tasks.

### 💻 Coder Agent
Expert Python developer assistant.
- **Tools**: `run_python_code`, `calculate`, `read_file`, `write_file`, `test_regex`, `count_tokens`.
- **Best for**: Writing code, debugging, and local file manipulations.

### 🔍 Research Agent
Web-enabled research assistant.
- **Tools**: `web_search`, `scrape_url`, `get_weather`, `get_datetime_info`, `get_news`, `get_wikipedia_summary`, `get_youtube_transcript`
- **Best for**: Fact-checking, gathering live data, and summarizing web content.

**Usage Endpoint:** `POST /agents/run`
**Example Body:**
```json
{
  "preset": "research",
  "question": "What is the current stock price of Google and what's the latest news?",
  "provider": "gemini",
  "model": "gemini-3.1-flash"
}
```

---

## 🛠 Centralized Tool Registry

The playground features a modular tools registry. Each tool is decorated with `@register` and can be automatically converted into a LangChain `BaseTool`.

### 🌐 Web Tools
- **`web_search(query)`**: Searches the web via DuckDuckGo (no API key required).
- **`scrape_url(url)`**: Fetches and extracts clean text content from any website.
- **`get_weather(location)`**: Live weather data via OpenWeatherMap.
- **`get_news(query)`**: Recent headlines and articles via NewsAPI.
- **`search_wikipedia(query)`**: Factual summaries from Wikipedia.
- **`get_youtube_transcript(url)`**: Full text transcripts from YouTube videos.

### ⚙️ System Tools
- **`run_python_code(code)`**: Executes Python code in a sandboxed subprocess.
- **`calculate(expression)`**: Safely evaluates mathematical expressions.
- **`read_file(path)` / `write_file(path, content)`**: Local filesystem interactions.
- **`get_datetime_info(timezone)`**: Precise date and time information.
- **`regex_search(pattern, text)`**: Regular expression testing and matching.
- **`count_tokens(text)`**: Token estimation for context window management.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.12+
- API Keys for your preferred providers (Gemini, Groq, Mistral, OpenRouter).

### 2. Installation
```bash
git clone <repository-url>
cd ai-llm-playground
pip install -r requirements.txt
# Additional agent dependencies:
pip install langgraph langchain-google-genai langchain-groq langchain-mistralai langchain-openai
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
MISTRAL_API_KEY=your_key
OPENROUTER_API_KEY=your_key
ALPHA_VANTAGE_API_KEY=your_key
OPENWEATHERMAP_API_KEY=your_key
NEWS_API_KEY=your_key
GOOGLE_SEARCH_API_KEY=your_key
GOOGLE_CSE_ID=your_cse_id
```

### 4. Run the Application
```bash
python -m app
```
The API will be available at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.