import logging
import json
import requests

from app.config import settings
from app.tools import call_tool, get_tools

logger = logging.getLogger(__name__)

def list_openrouter_models():
    try: 
        logger.info("Fetching OpenRouter models...")
        URL = f"{settings.openrouter_base_url}/models"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
        }
        res = requests.get(URL, headers=headers)
        if res.status_code != 200:
            logger.error("Failed to fetch models: %s", res.text)
            res.raise_for_status()

        models = res.json().get("data", [])
        free_models = sorted([m["id"] for m in models if m["id"].endswith(":free")])
        model_list = []
        for mid in free_models:
            model_list.append(mid)
        
        return model_list
    
    except Exception as e:
        logger.error(f"Error fetching OpenRouter models: {e}")
        raise


def openrouter_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with OpenRouter model: {model}")
        response = requests.post(
            url=f"{settings.openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

            })
        )

        data = response.json()

        # 1. Check for explicit API error first
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown OpenRouter error")
            logger.error(f"OpenRouter API error: {error_msg}")
            raise Exception(f"OpenRouter API error: {error_msg}")

        # 2. Validate choices exist and are not empty
        choices = data.get("choices")
        if not choices:
            logger.error(f"OpenRouter API returned no choices: {data}")
            raise Exception("OpenRouter API did not return choices")

        # 3. Safely extract content
        try:
            output = choices[0]["message"]["content"]
            logger.info("OpenRouter content generation successful")
            return output
        except (KeyError, IndexError) as e:
            logger.error(f"Malformed OpenRouter response structure: {e}")
            raise Exception(f"Could not parse content from OpenRouter response: {e}")

    except Exception as e:
        logger.error(f"Error in OpenRouter service: {e}")
        raise


def tools_service(model: str, prompt: str):
    """
    Generate content using OpenRouter with tool calling support.
    """
    try:
        logger.info(f"Starting tool-enabled chat with OpenRouter model: {model}")
        
        # Prepare tools (standard OpenAI schema)
        tool_schemas = get_tools()
        messages = [
            {"role": "user", "content": prompt}
        ]
        url = f"{settings.openrouter_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json"
        }

        # Tool Loop
        for _ in range(10):
            payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "tool_choice": "auto",
                "temperature": 0.1,
            }
            response = requests.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise Exception(f"OpenRouter error: {data['error']}")
                
            choice = data["choices"][0]
            response_message = choice["message"]
            tool_calls = response_message.get("tool_calls")
            
            if not tool_calls:
                return response_message.get("content", "")

            # Add assistant message to history
            messages.append(response_message)
            
            # Execute tools
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                try:
                    function_args = json.loads(tool_call["function"]["arguments"])
                    if not isinstance(function_args, dict):
                        raise ValueError("Tool arguments must decode to an object")

                    logger.info("Executing OpenRouter tool: %s", function_name)
                    result = call_tool(function_name, **function_args)
                    messages.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    })
                except Exception as e:
                    logger.error(f"OpenRouter tool execution failed: {function_name} -> {e}")
                    messages.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": f"Error: {str(e)}",
                    })
        
        raise RuntimeError("Maximum OpenRouter tool-calling iterations reached")
    except Exception as e:
        logger.error(f"Error in OpenRouter tools_service: {e}")
        raise