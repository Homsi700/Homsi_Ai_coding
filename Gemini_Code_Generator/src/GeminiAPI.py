import google.generativeai as genai
import os
import datetime

# Define the output directory relative to this script's location or a fixed path
# For consistency, let's assume this script is in Gemini_Code_Generator/src
# So, output_dir will be ../output
# Ensure this path is correct based on your project structure and where you run main.py
# For now, using a path relative to the project root, assuming main.py is run from Gemini_Code_Generator or its src.
# It's safer to determine this path dynamically or configure it.
OUTPUT_DIR = "output" # This will be relative to where main.py is run.
                      # If main.py is in src/, then output/ is Gemini_Code_Generator/output/

# Replace with your actual API key or load from a secure source
API_KEY = "YOUR_API_KEY_HERE" # TODO: Move to config.py

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = None

def init_client(api_key: str = None):
    global model
    key_to_use = api_key if api_key else API_KEY
    if not key_to_use or key_to_use == "YOUR_API_KEY_HERE":
        print("API Key not configured. Please set it in GeminiAPI.py or pass it to init_client.")
        return False

    genai.configure(api_key=key_to_use)
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    print("Gemini API client initialized successfully.")
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"Created output directory: {os.path.abspath(OUTPUT_DIR)}")
        except OSError as e:
            print(f"Error creating output directory {OUTPUT_DIR}: {e}")
            return False # Or handle more gracefully
    else:
        print(f"Output directory already exists: {os.path.abspath(OUTPUT_DIR)}")
    return True

def generate_code(prompt: str) -> str:
    global model
    if not model:
        # Attempt to initialize with the default key if not initialized
        if not init_client():
             return "Error: API Client not initialized and failed to auto-initialize. Please configure an API Key."

    try:
        prompt_parts = [prompt]
        response = model.generate_content(prompt_parts)

        if response.parts:
            generated_text = response.text
            # TODO: Implement more sophisticated parsing if Gemini returns structured data (e.g., multiple files)
            # For now, save the entire response to a single file with a timestamp.
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Default filename, assuming Python code for now. Extension could be dynamic.
            filename = f"generated_code_{timestamp}.py"
            filepath = os.path.join(OUTPUT_DIR, filename)

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(generated_text)
                print(f"Successfully saved generated code to: {os.path.abspath(filepath)}")
                return f"Code generated and saved to {filename}\n\n{generated_text}"
            except IOError as e:
                print(f"Error saving generated code to file {filepath}: {e}")
                return f"Error saving file: {e}\n\n{generated_text}"

        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            return f"Error: Prompt blocked due to {response.prompt_feedback.block_reason_message}"
        else:
            # This case might indicate an issue or an empty response that's not an explicit block
            return "Error: No content generated. The prompt might have been blocked or an unknown error occurred (empty response)."

    except Exception as e:
        return f"An error occurred during code generation: {e}"

if __name__ == '__main__':
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please replace 'YOUR_API_KEY_HERE' with your actual API key in GeminiAPI.py to run this example.")
    else:
        if init_client():
            # Ensure the output directory exists for the example
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)

            example_prompt = "Write a Python function that calculates the factorial of a number and include a docstring."
            print(f"\nSending prompt: \"{example_prompt}\"")
            result_message = generate_code(example_prompt)
            print(f"\nAPI Response:\n{result_message}")

            example_prompt_2 = "Create a simple HTML button that says 'Click Me'."
            print(f"\nSending prompt: \"{example_prompt_2}\"")
            result_message_2 = generate_code(example_prompt_2)
            print(f"\nAPI Response:\n{result_message_2}")
        else:
            print("Failed to initialize the Gemini API client.")
