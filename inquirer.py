from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

# style = style_from_dict({
#     Token.Separator: '#96cdfb',
#     Token.QuestionMark: '#673ab7 bold',
#     Token.Selected: '#96cdfb',  # default
#     Token.Pointer: '#673ab7 bold',
#     Token.Instruction: '',  # default
#     Token.Answer: '#f44336 bold',
#     Token.Question: '',
# })


async def display_list(no_chats,chats,id_list):

    if not no_chats:
        no_chats = 15

    if chats:
        peers = [] 
        for chat in chats:
            peers.append(id_list[chat])

        return peers

    chat_names = []
    for key in id_list.keys():
        chat_names.append(key)

    answers = await inquirer.checkbox(
    message="Select a Chat:",
    choices=chat_names,
    validate=lambda result: len(result) >= 1,
    invalid_message="should be at least 1 selection",
    instruction="(select at least 1)",
    ).execute_async()

    peers = []

    if answers:
        for answer in answers:
            peers.append(id_list[answer]) 
        return peers
    else:
        exit(1) 

