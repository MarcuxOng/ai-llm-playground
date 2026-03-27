import logging
from google import genai
from google.genai import types

from app.config import settings
from app.tools import call_tool, get_tools

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.gemini_api_key)


def list_gemini_models():
    try:
        logger.info("Fetching Gemini models...")
        models = sorted(client.models.list(), key=lambda m: m.name)
        model_list = []
        for m in models:
            response = m.name.replace("models/", "")
            model_list.append(response)
    
        return model_list
    
    except Exception as e:
        logger.error(f"Error fetching Gemini models: {e}")
        raise


def gemini_service(model: str, prompt: str):
    try:
        logger.info(f"Generating content with Gemini model: {model}")
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful assistant.",
                temperature=0.2,
                # thinking_config=types.ThinkingConfig(
                #     thinking_level="high"
                # ),
            )
        )

        return response.text

    except Exception as e:
        logger.error(f"Error generating Gemini content: {e}")
        raise
    

def tools_service(model: str, prompt: str):
    """
    Generate content using Gemini with tool calling support using ChatSession.
    """
    try:
        logger.info(f"Starting tool-enabled chat with Gemini model: {model}")
        
        # Prepare tools from the registry
        tool_schemas = get_tools()
        gemini_tools = []
        if tool_schemas:
            function_declarations = [
                types.FunctionDeclaration(
                    name=ts['function']['name'],
                    description=ts['function']['description'],
                    parameters=ts['function']['parameters']
                ) for ts in tool_schemas
            ]
            gemini_tools = [types.Tool(function_declarations=function_declarations)]

        # Initialize ChatSession (handles history automatically)
        chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                tools=gemini_tools,
                system_instruction="You are a helpful assistant that uses tools when necessary.",
                temperature=0.1,
            )
        )

        # Tool Loop: Handle multi-turn tool calls robustly
        response = chat.send_message(prompt)
        for _ in range(10):
            # Extract all tool calls from the current response
            tool_calls = [
                part.function_call 
                for candidate in response.candidates 
                for part in candidate.content.parts 
                if part.function_call
            ]
            
            if not tool_calls:
                return response.text

            # Execute all tool calls in parallel (sequentially in this loop)
            tool_responses = []
            for call in tool_calls:
                logger.info("Executing tool: %s", call.name)
                try:
                    # Map result to a FunctionResponse Part
                    result = call_tool(call.name, **call.args)
                    tool_responses.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=call.name,
                                response={'result': result}
                            )
                        )
                    )
                except Exception as e:
                    logger.error(f"Tool execution failed: {call.name} -> {e}")
                    tool_responses.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=call.name,
                                response={'error': str(e)}
                            )
                        )
                    )
            response = chat.send_message(tool_responses)
        return "Error: Maximum tool-calling iterations reached."

    except Exception as e:
        logger.error(f"Error in tools_service: {e}")
        raise


async def gemini_stream_service(model: str, prompt: str):
    try:
        logger.info(f"Starting Gemini streaming generation with model: {model}")
        response = client.models.generate_content_stream(
            model=model, 
            contents=prompt
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Error in Gemini streaming service: {e}")
        raise