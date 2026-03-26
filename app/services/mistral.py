import json
import logging
import requests
from mistralai import Mistral

from app.config import settings
from app.tools import call_tool, get_tools

logger = logging.getLogger(__name__)

def list_mistral_models():
    try:
        logger.info("Fetching Mistral models...")
        url = f"{settings.mistral_base_url}/models"
        headers = {
            "Authorization": f"Bearer {settings.mistral_api_key}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        models = result.get("data", [])
        ids = sorted([m["id"] for m in models])
        model_list = []

        for mid in ids:
            model_list.append(mid)

        return model_list
    
    except Exception as e:
        logger.error(f"Error fetching Mistral models: {e}")
        raise


def mistral_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with Mistral model: {model}")
        with Mistral(
            api_key=settings.mistral_api_key,
        ) as mistral:
            res = mistral.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                stream=False
            )

            response = res.choices[0].message.content

        return response

    except Exception as e:
        logger.error(f"Error generating content with Mistral: {e}")
        raise


def tools_service(model: str, prompt: str):
    """
    Generate content using Mistral with tool calling support.
    """
    try:
        logger.info(f"Starting tool-enabled chat with Mistral model: {model}")
        
        # Prepare tools (standard OpenAI-like schema)
        tool_schemas = get_tools()
        messages = [{
            "role": "user", 
            "content": prompt
        }]

        with Mistral(
            api_key=settings.mistral_api_key
        ) as client:
            for _ in range(10):
                response = client.chat.complete(
                    model=model,
                    messages=messages,
                    tools=tool_schemas,
                    tool_choice="auto",
                    temperature=0.1,
                )
                
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls
                if not tool_calls:
                    return response_message.content

                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    logger.info(f"Executing Mistral tool: {function_name} with {function_args}")
                    try:
                        result = call_tool(function_name, **function_args)
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(result),
                        })
                    except Exception as e:
                        logger.error(f"Mistral tool execution failed: {function_name} -> {e}")
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Error: {str(e)}",
                        })
        
        return "Error: Maximum tool-calling iterations reached."

    except Exception as e:
        logger.error(f"Error in Mistral tools_service: {e}")
        raise