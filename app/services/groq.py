import json
import logging
import requests
from groq import Groq
from groq.types.chat import ChatCompletionUserMessageParam

from app.config import settings
from app.tools import call_tool, get_tools

logger = logging.getLogger(__name__)
client = Groq(api_key=settings.groq_api_key)


def get_groq_models():
    try:
        logger.info("Fetching Groq models...")
        url = f"{settings.groq_base_url}/models"
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        model_ids = [model['id'] for model in data['data']]
        return sorted(model_ids)
    
    except Exception as e:
        logger.error(f"Error fetching Groq models: {e}")
        raise


def groq_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with Groq model: {model}")
        messages: list[ChatCompletionUserMessageParam] = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=True,
            stop=None
        )

        response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                response += content

        return response

    except Exception as e:
        logger.error(f"Error generating content with Groq: {e}")
        raise


def tools_service(model: str, prompt: str):
    """
    Generate content using Groq with tool calling support.
    """
    try:
        logger.info(f"Starting tool-enabled chat with Groq model: {model}")
        tool_schemas = get_tools()
        messages = [
            {"role": "system", "content": "You are a helpful assistant that uses tools when necessary."},
            {"role": "user", "content": prompt}
        ]

        # Tool Loop
        for _ in range(10):
            response = client.chat.completions.create(
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

            # Add the assistant's message (containing tool calls) to history
            messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Executing Groq tool: {function_name} with {function_args}")
                try:
                    result = call_tool(function_name, **function_args)
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    })
                except Exception as e:
                    logger.error(f"Groq tool execution failed: {function_name} -> {e}")
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": f"Error: {str(e)}",
                    })
        
        return "Error: Maximum tool-calling iterations reached."

    except Exception as e:
        logger.error(f"Error in Groq tools_service: {e}")
        raise