import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Back, Style
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
os.environ["LANG"] = "en_US.utf8"

# load values from the .env file if it exists
load_dotenv()


# configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = prompt = """Vastaa 
kysymyksiin 
koodista 
ja 
luo 
koodia 
annetuilla
ohjeilla"""

TEMPERATURE = 0.5
MAX_TOKENS = 2000
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": new_question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content
    


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None
def kysymys():
    kys = input(Fore.LIGHTMAGENTA_EX + Style.BRIGHT +"Haluatko kysyä? k/e: " + Style.RESET_ALL)
    if kys == "k":

    
        with open("chatgpt_question.txt", "w" , encoding="utf-8") as f:
            f.write("")

        try:
            # Open the nano editor with the question prompt
            nano_process = subprocess.Popen(["nano", "+1", "-c","-u",  "chatgpt_question.txt"],)

            nano_process.communicate()
        finally:
            # Close the file
            if 'f' in locals():
                f.close()

            # Terminate the nano process if it's still running
            if nano_process.poll() is None:
                nano_process.terminate()

        # Read the user's input from the file
        with open("chatgpt_question.txt", "r" , encoding="utf-8") as f:
            input_text = f.read().strip()

        return input_text
    elif kys == "e":
        print(Fore.RED + Style.BRIGHT + "Heippa rakas <3 "  + Style.RESET_ALL)
        exit()






def main():
    os.system("cls" if os.name == "nt" else "clear")
    # keep track of previous questions and answers
    previous_questions_and_answers = []
    while True:
        # ask the user for their question
        new_question = kysymys()

        try:
            # check the question is safe
            errors = get_moderation(new_question)
            if errors:
                print(
                    Fore.RED
                    + Style.BRIGHT
                    + "Sori tos oli jotain törkeetä"
                )
                for error in errors:
                    print(error)
                print(Style.RESET_ALL)
                continue

            # get response from GPT-3
            response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)

        except Exception as e:
            print(Fore.RED + Style.BRIGHT + "Jotain meni vikaan: " + str(e) + Style.RESET_ALL)
            continue

        # add the new question and answer to the list of previous questions and answers
        previous_questions_and_answers.append((new_question, response))

        # print the response
        print(Fore.CYAN + Style.BRIGHT + "Vastaukseni " + Style.NORMAL + response)



if __name__ == "__main__":
    main()
