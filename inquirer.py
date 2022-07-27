from PyInquirer import style_from_dict, Token, prompt

style = style_from_dict({
    Token.Separator: '#96cdfb',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#96cdfb',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})


async def display_list(no_chats,chats,id_list):

    if not no_chats:
        no_chats = 15

    if chats:
        peers = []
        for chat in chats:
            try:
                peers.append(id_list[chat])
            except:
                pass

        return peers

    dist = []
    for key in id_list.keys():
        tmp = {}
        tmp['name'] = key
        dist.append(tmp)

    questions = [
    {
    'type': 'checkbox',
    'message': 'Select chat',
    'name': 'Chats',
    'choices': dist,
    'validate': lambda answer: 'Choose atleast one chat' \
            if len(answer) == 0 else True
            }
    ]

    answers = prompt(questions,style=style)
    peers = []

    if answers:
        for val in answers.values():
            for answer in val:
                peers.append(id_list[answer]) 

            return peers
    else:
        exit(1) 

