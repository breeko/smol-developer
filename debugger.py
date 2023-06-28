import argparse

import modal

from ModalStub import decorator
from constants import DEFAULT_DIR, DEFAULT_MODEL
from prompts.debugger import debugger_system_prompt, debugger_user_prompt
from utils.color_utils import teal
from utils.openai_utils import generate_response
from utils.path_utils import walk_directory


# Argument parser
parser = argparse.ArgumentParser(description='This is a description of what this program does')
parser.add_argument('--prompt', type=str, required=True, help='Prompt string or a path to a .md file')
parser.add_argument('--directory', type=str, default=DEFAULT_DIR, help='Path to a directory')
parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='Model name')
parser.add_argument('--modal', action='store_true', default=False, help='Whether to run the script with modal or not')


args = parser.parse_args()

if args.modal:
    # yes we are recommending using Modal by default, as it helps with deployment. see readme for why.
    stub = modal.Stub(
        "smol-developer-v1")
    function = stub.function
    local_entrypoint = stub.local_entrypoint
    openai_image = modal.Image.debian_slim().pip_install("openai", "tiktoken")
else:

    function = decorator
    local_entrypoint = decorator
    openai_image = None


generate_response_debugger = function(
    f=generate_response,
    image=openai_image,
    secret=modal.Secret.from_dotenv(),
    retries=modal.Retries(
        max_retries=3,
        backoff_coefficient=2.0,
        initial_delay=1.0,
    ),
    concurrency_limit=5,
    timeout=120,
)


@local_entrypoint()
def main(prompt: str, directory: str = DEFAULT_DIR, model="gpt-3.5-turbo"):
    code_contents = walk_directory(directory)

    # Now, `code_contents` is a dictionary that contains the content of all your non-image files
    # You can send this to OpenAI's text-davinci-003 for help

    context = "\n".join(f"{path}:\n{contents}" for path, contents in code_contents.items())
    user_prompt = debugger_user_prompt(context=context, prompt=prompt)
    res = generate_response_debugger.call(debugger_system_prompt, user_prompt, model)

    print(teal(res))


if __name__ == "__main__":
    prompt = args.prompt

    main(
        prompt=args.prompt,
        directory=args.directory,
        model=args.model,
    )
