import os
import openai

# Create directories
os.makedirs('utils', exist_ok=True)
os.makedirs('results/part_2', exist_ok=True)

# Read the .env file and set variables manually
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value

# at least it works
API_URL = os.getenv("API_URL")

API_KEY = os.getenv("HUGGINGFACE_API_KEY")

headers = {"Authorization": f"Bearer {API_KEY}"}  # Optional for some models

class LLMClient:
    def __init__(self, model="HuggingFaceH4/zephyr-7b-beta", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        self.openai = openai

    def query(self, message):
        """
        Send a prompt to the OpenAI ChatGPT API.

        Args:
            message (str): The user's input prompt.

        Returns:
            str: The model's response.
        """
        if not self.openai.api_key:
            return "[Error] No API key found. Please set OPENAI_API_KEY."

        try:
            response = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": message}]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error] {str(e)}"

class LLMChatTool:
    """
    Wrapper class required by the autograder.
    Uses LLMClient internally.
    """
    def __init__(self, model="HuggingFaceH4/zephyr-7b-beta"):
        self.client = LLMClient(model=model)

    def get_response(self, prompt):
        return self.client.query(prompt)

def run_chat(model="HuggingFaceH4/zephyr-7b-beta"):
    """
    Run an interactive one-off chat session.
    Each input is treated independently (no memory).
    """
    client = LLMClient(model=model)

    print("One-Off Chat — type 'exit' to quit.")

    try:
        while True:
            try:
                user_input = input("\nYou: ").strip()
            except EOFError:
                print("\n[EOF received] Exiting...")
                break

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            response = client.query(user_input)
            print(f"ChatGPT: {response}")

    except KeyboardInterrupt:
        print("\n[Interrupted with Ctrl+C — exiting]")


def main():
    run_chat()

if __name__ == "__main__":
    main()