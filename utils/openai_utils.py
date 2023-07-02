import os

from utils.color_utils import light_gray, green

DEFAULT_MAX_TOKENS = 2_000


def report_tokens(prompt: str, model: str):
    import tiktoken
    encoding = tiktoken.encoding_for_model(model)
    # print number of tokens in light gray, with first 50 characters of prompt in green.
    # if truncated, show that it is truncated
    print(light_gray(str(len(encoding.encode(prompt))) + " tokens") + " in prompt: " +
          green(prompt[:50] + "..." if len(prompt) > 50 else ""))


def generate_response(model: str, system_prompt: str, user_prompt: str, *args):
    # IMPORTANT: Keep import statements here due to Modal container restrictions
    # https://modal.com/docs/guide/custom-container#additional-python-packages
    import openai


    # Set up your OpenAI API credentials
    openai.api_key = os.environ["OPENAI_API_KEY"]

    messages = []
    messages.append({"role": "system", "content": system_prompt})
    report_tokens(prompt=system_prompt, model=model)
    messages.append({"role": "user", "content": user_prompt})
    report_tokens(prompt=user_prompt, model=model)
    # Loop through each value in `args` and add it to messages alternating role between "assistant" and "user"
    role = "assistant"
    for value in args:
        messages.append({"role": role, "content": value})
        report_tokens(value, model)
        role = "user" if role == "assistant" else "assistant"

    params = {
        "model": model,
        "messages": messages,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "temperature": 0,
    }

    # Send the API request
    response = openai.ChatCompletion.create(**params)

    # Get the reply from the API response
    reply = response.choices[0]["message"]["content"]
    return reply

