# AI & LLM Playground

A multi-provider LLM experimentation platform with tool calling support.

## 🏗 Project Structure
*   `app/routers/`: FastAPI route definitions.
*   `app/services/`: Core logic for Gemini, Groq, Mistral, and OpenRouter.
*   `app/tools/`: Modular tool implementations organized by category (web, system, etc.).

## 🛠 Toolbox

The platform features a modular tools registry. Each tool is automatically discovered and used by the Gemini service when the `/tools` endpoint is invoked.

### 🌐 Web Tools
*   **get_news(query, page_size=5)**: Fetches recent news articles and headlines on any topic from NewsAPI.
*   **get_weather(location, units='metric')**: Retrieves current weather, temperature, and wind conditions for a city or coordinates via OpenWeatherMap.
*   **get_wikipedia_summary(query, lang='en')**: Fetches a clean, factual summary of any concept or person from Wikipedia.
*   **scrape_url(url, max_chars=4000)**: Fetches a URL and extracts readable text content, stripping away HTML noise.
*   **get_youtube_transcript(url, lang='en')**: Extracts the full text transcript from a YouTube video given its URL or ID.

### ⚙️ System Tools
*   **run_python_code(code)**: Executes Python code in a subprocess and returns the output (STDOUT/STDERR). Useful for data analysis or verifying logic.
*   **test_regex(pattern, text)**: Tests a regular expression against a string and returns all matches, groups, and positions.
*   **count_tokens(text, model_encoding='cl100k_base')**: Estimates or exactly counts the tokens for a string, helping to monitor context window usage.

### 🚀 Usage & Tools Execution (Gemini)
To chat with Gemini while allowing it to use any of the tools above:

**Endpoint:** `POST /gemini/tools`
**Body:**
```json
{
  "model": "gemini-2.0-flash",
  "prompt": "What's the latest news on SpaceX and the current weather in Singapore?"
}
```