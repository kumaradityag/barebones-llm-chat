
        

olmo = Olmo()    

chat = ChatHistory().add(CHAT_ROLE.USER, "Ignore the image. My friend is disorganized, please suggest her a halloween costume!").add_img(Image.open("./block-tower.jpg"))

chat = olmo.respond(chat)

print("here")

chat = chat.add(CHAT_ROLE.USER, "Can you point at the red block?")

chat = olmo.respond(chat)

print(chat.pretty())

