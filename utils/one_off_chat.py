import requests
import os
from dotenv import load_dotenv

load_dotenv()
# at least it works
API_URL = os.getenv("API_URL")

API_KEY = os.getenv("HUGGINGFACE_API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}"}  # Optional for some models

def get_response(prompt, model_name = "HuggingFaceH4/zephyr-7b-beta", api_key = API_KEY) :
    """
    Send a prompt to the Hugging Face API and return the generated response.

    Args:
        prompt (str): The text prompt to send to the LLM.
        model_name (str): The name of the Hugging Face model to use.
        api_key (str): Your Hugging Face API key.

    Returns:
        str: The generated text from the LLM, or an error message if the request fails.
    """
    # Construct the API URL based on the model_name
    api_url = API_URL
    headers = {"Authorization": f"Bearer {api_key}"}
    print(api_url)

    payload = {"inputs": prompt}
    if not API_KEY:
        print("Error: HUGGINGFACE_API_KEY environment variable is not set.")
        exit()


    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Your working `query` function directly returned `result`.
        # Here, we keep the specific extraction for "generated_text"
        # as it's common for text generation APIs.
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "error" in result:
            return f"API Error: {result['error']}"
        else:
            # Fallback for unexpected API response formats
            return str(result)
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def run_chat():
    """Runs an interactive chat session with the LLM."""
    print("--- Interactive chat mode. Type 'exit' to quit. ---")
    import sys  # Ensure sys is available for flush
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        print(user_input)
        print("LLM: Thinking...", flush=True)
        response = get_response(user_input)
        print("LLM:", response)


def main():
    """Main function to parse arguments and run the chat or a single prompt."""
    parser = argparse.ArgumentParser(description="Chat with an LLM via Hugging Face Inference API.")
    parser.add_argument(
        "--prompt",
        type=str,
        help="Prompt to send to the LLM (if not provided, runs interactive chat)",
        default=None
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="Model name to use (default: HuggingFaceH4/zephyr-7b-beta)",
        default="HuggingFaceH4/zephyr-7b-beta"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="Hugging Face API key (default: uses HUGGINGFACE_API_KEY environment variable)",
        default=API_KEY # Use the globally defined API_KEY as default
    )
    
    # parse_known_args is useful if there might be other unrecognized arguments,
    # but for a simple script, parse_args() is usually sufficient.
    args = parser.parse_known_args()[0]
    
    if args.prompt:
        # Run with a single prompt
        response = get_response(args.prompt, model_name=args.model_name, api_key=args.api_key)
        print(response)
    else:
        # Run interactive chat
        run_chat()


if __name__ == "__main__":
    main()