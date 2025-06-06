# utils/conversation.py

import requests
import argparse
from collections import deque

DEFAULT_API_TIMEOUT = 60

def get_response(prompt: str, history: deque = None, model_name: str = "HuggingFaceH4/zephyr-7b-beta", api_key: str = API_KEY, history_length: int = 3) -> str:
    """
    Get a response from the model using conversation history.

    Args:
        prompt (str): The current user prompt.
        history (deque): A deque (double-ended queue) of previous (user_prompt, llm_response) tuples.
                         Used for maintaining a limited conversation history.
        model_name (str): Name of the model to use on Hugging Face (e.g., "google/flan-t5-base").
        api_key (str): API key for authentication with Hugging Face.
        history_length (int): Number of previous exchanges (user_prompt, llm_response)
                              to include as context in the current prompt.

    Returns:
        str: The model's generated response, or an informative error message if the request fails.
    """
    # Initialize history as a deque if it's None or not already a deque.
    # The maxlen ensures the history stays within the specified length.
    if history is None or not isinstance(history, deque):
        history = deque(maxlen=history_length)

    # Construct the full API URL for the specified model.
    api_url = API_URL
    headers = {"Authorization": f"Bearer {api_key}"}

    context = ""
    for prev_user_prompt, prev_llm_response in history:
        context += f"User: {prev_user_prompt}\nAI: {prev_llm_response}\n"

    # Combine the historical context with the current user prompt.
    # The "AI:" at the end hints the model to complete the AI's turn.
    full_prompt = f"{context}User: {prompt}\nAI:"

    # Define the payload for the API request.
    # Parameters like max_new_tokens and temperature help control the LLM's output.
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 150, # Limit the length of the generated response
            "temperature": 0.7,    # Controls creativity (higher = more creative)
            "do_sample": True,     # Enables sampling from the model's output distribution
            "return_full_text": False # Instructs the API to only return the generated part
        }
    }

    try:
        # Send the POST request to the Hugging Face Inference API.
        # The timeout prevents the request from hanging indefinitely.
        response = requests.post(api_url, headers=headers, json=payload, timeout=DEFAULT_API_TIMEOUT)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx status codes)

        result = response.json()

        # Extract the generated text from the API response.
        if isinstance(result, list) and "generated_text" in result[0]:
            generated_text = result[0]["generated_text"].strip()
            # Clean up potential leading/trailing parts the model might generate
            if generated_text.startswith("User:"):
                # If the model hallucinates user turns, remove them
                generated_text = generated_text.split("AI:", 1)[-1].strip()
            elif generated_text.startswith("AI:"):
                # If the model explicitly starts with "AI:", remove it
                generated_text = generated_text.replace("AI:", "").strip()
            
            return generated_text
        elif isinstance(result, dict) and "error" in result:
            # Handle API-specific errors returned in the response body
            return f"API Error: {result.get('error', 'Unknown API Error')}"
        else:
            # Handle unexpected response formats from the API
            return f"Unexpected API response format: {str(result)}"
    except requests.exceptions.Timeout:
        # Catch specific timeout errors
        return f"Request failed: Read timed out after {DEFAULT_API_TIMEOUT} seconds. The model might be busy or your internet is slow."
    except requests.exceptions.HTTPError as http_err:
        # Catch HTTP errors (e.g., 401 Unauthorized, 404 Not Found, 500 Internal Server Error)
        return f"HTTP error occurred: {http_err} - Response: {http_err.response.text}"
    except requests.exceptions.RequestException as req_err:
        # Catch other requests-related exceptions (e.g., connection errors)
        return f"Request failed: {req_err}"
    except Exception as e:
        # Catch any other unexpected exceptions
        return f"An unexpected error occurred: {e}"

def run_chat():
    """Runs an interactive chat session with conversation history."""
    print("Welcome to the Contextual LLM Chat! Type 'exit' to quit.")
    print("-------------------------------------------------------")

    # Initialize conversation history using a deque to manage its length.
    # The maxlen is determined by the history_length argument passed to main.
    history = deque(maxlen=args.history_length) # Access args from the outer scope's main function

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break


        print("LLM: Thinking...", flush=True) # Use flush=True to ensure "Thinking..." appears immediately

        # Get response using the current user input and the conversation history.
        llm_response = get_response(
            prompt=user_input,
            history=history,
            model_name=args.model_name, # Use model_name from parsed arguments
            api_key=args.api_key        # Use api_key from parsed arguments
        )

        # Kindly reminder to add money
        if "402 Client Error: Payment Required" in llm_response:
            history.append((user_input, llm_response))
            llm_response = "\nIf you can't give me money, I don't wanna waste time on you."
            print(llm_response)
            break

        # Print the LLM's response.
        print("LLM:", llm_response)

def main():
    """Main function to parse command-line arguments and run the chat session."""
    parser = argparse.ArgumentParser(description="Chat with an LLM using conversation history.")
    parser.add_argument(
        "--prompt",
        type=str,
        help="A single prompt to send to the LLM (if not provided, runs interactive chat mode).",
        default=None
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Hugging Face model to use (default: HuggingFaceH4/zephyr-7b-beta).",
        default="HuggingFaceH4/zephyr-7b-beta" # Updated default model name
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="Your Hugging Face API key (defaults to HUGGINGFACE_API_KEY environment variable).",
        default=API_KEY # Uses the globally loaded API_KEY as default
    )
    parser.add_argument(
        "--history_length",
        type=int,
        help="Number of previous conversation exchanges to include as context (default: 3).",
        default=3
    )

    # Change to parse_known_args() to ignore unknown arguments (like Jupyter's --f argument)
    global args 
    args, unknown = parser.parse_known_args() # Modified line

    # Determine whether to run interactive chat or a single prompt execution.
    if args.prompt:
        # If a single prompt is provided, get a response and print it.
        # History is not managed for single prompt executions from CLI.
        print("LLM: Thinking...")
        response = get_response(
            prompt=args.prompt,
            model_name=args.model_name,
            api_key=args.api_key # Ensure API key is passed here
        )
        print("LLM:", response)
    else:
        # If no prompt, start the interactive chat session.
        run_chat()

if __name__ == "__main__":
    main()