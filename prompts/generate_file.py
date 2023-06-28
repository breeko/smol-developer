def generate_file_prompt(prompt: str, filepaths_string: str, shared_dependencies: str, filename: str) -> (str, str):
    system_prompt = f"""You are an AI developer who is trying to write a program that will generate code for the user based on their intent.
          
      the app is: {prompt}
  
      the files we have decided to generate are: {filepaths_string}
  
      the shared dependencies (like filenames and variable names) we have decided on are: {shared_dependencies}
      
      only write valid code for the given filepath and file type, and return only the code.
      do not add any other explanation, only return valid code for that file type.
      """

    user_prompt = f"""
      We have broken up the program into per-file generation. 
      Now your job is to generate only the code for the file {filename}. 
      Make sure to have consistent filenames if you reference other files we are also generating.
      
      Remember that you must obey 3 things: 
         - you are generating code for the file {filename}
         - do not stray from the names of the files and the shared dependencies we have decided on
         - MOST IMPORTANT OF ALL - the purpose of our app is {prompt} - every line of code you generate must be valid code. Do not include code fences in your response, for example
      
      Bad response:
      ```javascript 
      console.log("hello world")
      ```
      
      Good response:
      console.log("hello world")
      
      Begin generating the code now.
  
      """

    return system_prompt, user_prompt
