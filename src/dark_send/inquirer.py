from InquirerPy import inquirer


async def display_list(chats, id_list):

    if chats:
        peers = [] 
        for chat in chats:
            if isinstance(id_list[chat], int):
                peers.append([ id_list[chat], None ])
            else: 
                topic_dict = {}
                for topic in id_list[chat][1]: 
                    topic_dict[ list(topic.keys())[0] ] = list(topic.values())[0]

                topic_list = await inquirer.fuzzy(
                message="Select Topic(s) from {}:".format(chat),
                choices=topic_dict,
                multiselect=True,
                validate=lambda result: len(result) >= 1,
                invalid_message="Select atleast one",
                instruction="(TAB to select)",
                max_height="50%",
                ).execute_async()
                for topic in topic_list: 
                    peers.append([ id_list[chat][0], topic_dict[topic] ] )

        return peers

    chat_names = []
    for key in id_list.keys():
        chat_names.append(key)

    answers = await inquirer.fuzzy(
    message="Select Chat(s):",
    choices=chat_names,
    multiselect=True,
    validate=lambda result: len(result) >= 1,
    invalid_message="Select atleast one",
    instruction="(TAB to select)",
    max_height="50%",
    ).execute_async()

    peers = []

    if answers:
        for answer in answers:
            if isinstance(id_list[answer], int):
                peers.append([ id_list[answer], None ]) 
            else: 
                topic_dict = {}
                for topic in id_list[answer][1]: 
                    topic_dict[ list(topic.keys())[0] ] = list(topic.values())[0]

                topic_list = await inquirer.fuzzy(
                message="Select Topic(s) from {}:".format(answer),
                choices=topic_dict,
                multiselect=True,
                validate=lambda result: len(result) >= 1,
                invalid_message="Select atleast one",
                instruction="(TAB to select)",
                max_height="50%",
                ).execute_async()

                for topic in topic_list: 
                    peers.append([ id_list[answer][0], topic_dict[topic] ] )

        return peers
    else:
        exit(1) 

