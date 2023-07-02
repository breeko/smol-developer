EXTENSION_TO_SKIP = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".tif", ".tiff"]
DEFAULT_DIR = "generated"

# we recommend 'gpt-4' if you have it
# gpt3.5 is going to be worse at generating code so we strongly recommend gpt4.
# I know most people don't have access, we are working on a hosted version
DEFAULT_MODEL = "gpt-3.5-turbo"

# I wonder how to tweak this properly. we don't want it to be max length as it encourages verbosity of code.
# but too short and code also truncates suddenly.
DEFAULT_MAX_TOKENS = 2000
