debugger_system_prompt = \
    "You are an AI debugger who is trying to debug a program for a user based on their file system. " \
    "The user has provided you with the following files and their contents, finally followed by the " \
    "error message or issue they are facing."


def debugger_user_prompt(context: str, prompt: str):
    return f"My files are as follows: {context}\n\nMy issue is as follows: {prompt} \n\n" \
           f"Give me ideas for what could be wrong and what fixes to do in which files."
