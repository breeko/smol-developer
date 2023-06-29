from typing import Optional, Tuple


def generate_prompt_prompt(prompt: Optional[str], context: str) -> Tuple[str, str]:
    system = "You are an AI debugger who is trying to fully describe a program, in order for another AI program to reconstruct every file, data structure, function and functionality. The user has provided you with the following files and their contents:"
    user_prompt = f"""My files are as follows: "
        {context}
        

        {("Take special note of the following: " + prompt) if prompt else ""}
        Describe the program in markdown using specific language that will help another AI program reconstruct the given program in as high fidelity as possible.
      """
    return system, user_prompt
