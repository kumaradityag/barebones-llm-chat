# What even is this?

This is a simplistic interface for hosting chatbots. It comes with the following components:

- "Home server"
    - Hosts an API to query the chats, create chats, delete chats, send messages to chats. Also handles authentifications.
    - Hosts a web interface to allow humans to debug the API and/or send messages and/or create/delete chats.
    - Hosts a socketio endpoint to emit events to the chatbot when the user sends messages
    - Hosts a socketio endpoint to update the web interface when the chatbot responds to the user
    - Downloads user-provided images and hashes them (the LLM only receives the hashes).
- LLM listener
    - A socketio listener that listens for message events from the "Home server"
    - A class that wraps around huggingface LLMs to do multimodal chat completion.
    - Methods to download the images stored in the server.
- Python interface
    - An interface for python
    - A work-in-progress CLI interface. (But I gave up because ChatGPT can't properly generate this stuff. I'm not about to code that stuff by hand lol. If you can help finish it (i.e. know better prompting techniques for python Curses let me know.))

# How do I use it?

### First option: tunnels

If you have access to a node that has a GPU, you can tunnel into the node where the LLM will run.
From your local computer, run

```
ssh -R 5000:localhost:5000 <node address>
```

This makes it so queries to `localhost:5000` on the node actually go to your local computer.

Then, just run `api.py` on your computer and open up `index.py` in your browser.

### Second option: port forwarding

Otherwise, you need to open a port in your local network, 
host the server there (probably at home because whatever schooling institution or 
corporation you are at probably won't allow you to have such a port, probably), and point the chatbot to the IP and port 
that you are using.

# What LLMs are supported?

Only `Molmo` lol. But the class it uses (`molmo_bot.py`) is very generic so it should be easy to add new LLMs, if need to. PR's welcome.

