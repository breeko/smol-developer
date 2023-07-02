import argparse
import os
from typing import Optional, Tuple

import modal
import ast

from ModalStub import decorator
from prompts.debugger_prompt import debugger_user_prompt, debugger_system_prompt
from prompts.filepaths_string_prompt import filepaths_string_prompt
from prompts.generate_file_prompt import generate_file_prompt
from prompts.generate_prompt import generate_prompt_prompt
from prompts.shared_dependencies import shared_dependencies_prompt
from utils.color_utils import green, teal
from utils.path_utils import clean_dir, write_file, walk_directory, fetch_prompt
from utils.openai_utils import generate_response
from constants import DEFAULT_DIR, DEFAULT_MODEL

# Argument parser
parser = argparse.ArgumentParser(
    description="This is a description of what this program does"
)
parser.add_argument(
    "ignore", nargs="*", help="A catch all for positional args so you can run modal"
)
parser.add_argument(
    "--prompt",
    type=str,
    default=None,
    help="Prompt string or a path to a .md file",
)
parser.add_argument(
    "--directory", type=str, default=DEFAULT_DIR, help="Path to a directory"
)
parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model name")
parser.add_argument(
    "--file", type=str, default=None, help="File name or a path to a file"
)
parser.add_argument(
    "--mode",
    choices=["generate", "debug", "prompt"],
    help="Whether to generate based on prompt, debug or generate prompt for an existing codebase",
)


args = parser.parse_args()


if len(args.ignore) > 0 and args.ignore[0] == "run":
    # yes we are recommending using Modal by default, as it helps with deployment. see readme for why.
    stub = modal.Stub("smol-developer-v1")
    function = stub.function
    local_entrypoint = stub.local_entrypoint
    openai_image = modal.Image.debian_slim().pip_install("openai", "tiktoken")
else:
    function = decorator
    local_entrypoint = decorator
    openai_image = None


generate_response_main = function(
    image=openai_image,
    secret=modal.Secret.from_dotenv(),
    retries=modal.Retries(
        max_retries=5,
        backoff_coefficient=2.0,
        initial_delay=1.0,
    ),
    # many users report rate limit issues (https://github.com/smol-ai/developer/issues/10)
    # so we try to do this but it is still inexact. would like ideas on how to improve
    concurrency_limit=5,
    timeout=120,
)(generate_response)


@function(
    image=openai_image,
    secret=modal.Secret.from_dotenv(),
)
def generate_file(
    filename: str,
    model: str = DEFAULT_MODEL,
    filepaths_string: Optional[str] = None,
    shared_dependencies: Optional[str] = None,
    prompt: Optional[str] = None,
) -> Tuple[str, str]:
    # call openai api with this prompt
    system_prompt, user_prompt = generate_file_prompt(
        prompt=prompt,
        filename=filename,
        filepaths_string=filepaths_string,
        shared_dependencies=shared_dependencies,
    )

    filecode = generate_response_main(
        model=model, system_prompt=system_prompt, user_prompt=user_prompt
    )

    return filename, filecode


@local_entrypoint()
def generate(
    prompt: str, directory=DEFAULT_DIR, model=DEFAULT_MODEL, file=None
) -> None:
    # read file from prompt if it ends in a .md filetype
    prompt = fetch_prompt(prompt)

    print("hi its me, 🐣the smol developer🐣! you said you wanted:")
    print(green(prompt))

    # call openai api with this prompt
    dir(generate_response_main)
    filepaths_string = generate_response_main.call(
        model, filepaths_string_prompt, prompt
    )
    print(filepaths_string)
    # parse the result into a python list
    try:
        list_actual = ast.literal_eval(filepaths_string)

        # if shared_dependencies.md is there, read it in, else set it to None
        shared_dependencies = None
        if os.path.exists("shared_dependencies.md"):
            with open("shared_dependencies.md", "r") as shared_dependencies_file:
                shared_dependencies = shared_dependencies_file.read()

        if file is not None:
            # check file
            print("file", file)
            filename, filecode = generate_file(
                file,
                model=model,
                filepaths_string=filepaths_string,
                shared_dependencies=shared_dependencies,
                prompt=prompt,
            )
            write_file(filename, filecode, directory)
        else:
            clean_dir(directory)

            # understand shared dependencies
            system_prompt = shared_dependencies_prompt(
                prompt=prompt, filepaths_string=filepaths_string
            )
            shared_dependencies = generate_response_main.call(
                model, system_prompt, prompt
            )
            print(shared_dependencies)
            # write shared dependencies as a md file inside the generated directory
            write_file("shared_dependencies.md", shared_dependencies, directory)

            # Iterate over generated files and write them to the specified directory
            for filename, filecode in generate_file.map(
                list_actual,
                order_outputs=False,
                kwargs=dict(
                    model=model,
                    filepaths_string=filepaths_string,
                    shared_dependencies=shared_dependencies,
                    prompt=prompt,
                ),
            ):
                write_file(filename, filecode, directory)

    except ValueError:
        print("Failed to parse result")


@local_entrypoint()
def debug(prompt: str, directory: str = DEFAULT_DIR, model=DEFAULT_MODEL):
    prompt = fetch_prompt(prompt)
    code_contents = walk_directory(directory)

    # Now, `code_contents` is a dictionary that contains the content of all your non-image files
    # You can send this to OpenAI's text-davinci-003 for help

    context = "\n".join(
        f"{path}:\n{contents}" for path, contents in code_contents.items()
    )
    user_prompt = debugger_user_prompt(context=context, prompt=prompt)
    res = generate_response_main.call(model, debugger_system_prompt, user_prompt)

    print(teal(res))


@local_entrypoint()
def generate_prompt(
    prompt: Optional[str] = None, directory=DEFAULT_DIR, model=DEFAULT_MODEL
):
    code_contents = walk_directory(directory)

    # Now, `code_contents` is a dictionary that contains the content of all your non-image files
    # You can send this to OpenAI's text-davinci-003 for help

    context = "\n".join(
        f"{path}:\n{contents}" for path, contents in code_contents.items()
    )

    system_prompt, user_prompt = generate_prompt_prompt(context=context, prompt=prompt)
    res = generate_response_main.call(model, system_prompt, user_prompt, model)
    # print res in teal
    print(teal(res))


if __name__ == "__main__":
    if args.mode == "debug":
        if not args.prompt:
            raise ValueError("Prompt required!")
        debug(
            prompt=args.prompt,
            directory=args.directory,
            model=args.model,
            file=args.file,
        )
    elif args.mode == "generate":
        if not args.prompt:
            raise ValueError("Prompt required!")
        generate(
            prompt=args.prompt,
            directory=args.directory,
            model=args.model,
            file=args.file,
        )
    elif args.mode == "prompt":
        generate_prompt(prompt=args.prompt, directory=args.directory, model=args.model)
