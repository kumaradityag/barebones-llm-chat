# What even is this?


![image](https://github.com/user-attachments/assets/7fec763f-288b-4e9e-a015-b2302865a086)
*Here pictured: the human-readable interface. LLM backend based on https://molmo.allenai.org/blog*


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
    - A work-in-progress CLI interface. (But I gave up because ChatGPT can't properly generate this stuff. I'm not about to code that stuff by hand lol. If you can help finish it (i.e. know better prompting techniques for python Curses) let me know.)
 
# How do I install it?

Quick and easy: `pip3 install -e git+https://github.com/Velythyl/barebones-llm-chat.git#egg=barebonesllmchat`

You can also `git clone` and then `pip3 install -e .`

If you have a modern code editor (PyCharm, VSCode, etc.) you don't even need to install, the editor should finagle the python paths properly and you should be able to directly launch the scripts.

# How do I use it?

### First option: tunnels

If you have access to a node that has a GPU, you can tunnel into the node where the LLM will run.
From your local computer, run

```
ssh -R 5000:localhost:5000 <node address>
```

This makes it so queries to `localhost:5000` on the node actually go to your local computer.

Then, just run `api.py` on your computer and open up the IP address in your browser.

In this way, you could also just host everything on the same node, without the need for tunnels. You could run the LLM, the API, as well as some other in-training agent that now has access to the LLM.

### Second option: port forwarding

Otherwise, you need to open a port in your local network, 
host the server there (probably at home because whatever schooling institution or 
corporation you are at probably won't allow you to have such a port, probably), and point the chatbot to the IP and port 
that you are using.

If you go with this option, you might need to do some changes to the way the BASE_URL is set in `index.html`

# What LLMs are supported?

Only `Molmo` lol. But the class it uses (`molmo_bot.py`) is very generic so it should be easy to add new LLMs, if need to. PR's welcome.

# Is this secure? Does it support HTTPS? Is this usable in production?

No 

# Why this instead of Gradio/some other thing?

This allows very low level control of the LLM, all in non-obfuscated code.
So it's ideal for research.

If you need to do special stuff with your model, or if you want to add a weird API with multimodality or whatever, then you might want to use this.

# Citing

```
@software{barebones-llm,
  author = {Charlie Gauthier},
  title = {Barebones LLM Chat},
  url = {[http://github.com/google/brax}](https://github.com/Velythyl/barebones-llm),
  version = {0.0.0},
  year = {2024},
}
```

```
@article{Deitke2024MolmoAP,
  title={Molmo and PixMo: Open Weights and Open Data for State-of-the-Art Multimodal Models},
  author={Matt Deitke and Christopher Clark and Sangho Lee and Rohun Tripathi and Yue Yang and Jae Sung Park and Mohammadreza Salehi and Niklas Muennighoff and Kyle Lo and Luca Soldaini and Jiasen Lu and Taira Anderson and Erin Bransom and Kiana Ehsani and Huong Ngo and YenSung Chen and Ajay Patel and Mark Yatskar and Christopher Callison-Burch and Andrew Head and Rose Hendrix and Favyen Bastani and Eli VanderBilt and Nathan Lambert and Yvonne Chou and Arnavi Chheda and Jenna Sparks and Sam Skjonsberg and Michael Schmitz and Aaron Sarnat and Byron Bischoff and Pete Walsh and Christopher Newell and Piper Wolters and Tanmay Gupta and Kuo-Hao Zeng and Jon Borchardt and Dirk Groeneveld and Jennifer Dumas and Crystal Nam and Sophie Lebrecht and Caitlin Wittlif and Carissa Schoenick and Oscar Michel and Ranjay Krishna and Luca Weihs and Noah A. Smith and Hanna Hajishirzi and Ross Girshick and Ali Farhadi and Aniruddha Kembhavi},
  journal={ArXiv},
  year={2024},
  volume={abs/2409.17146},
  url={https://api.semanticscholar.org/CorpusID:272880654}
}
```

# License

This code is provided with no guarantees of any kind, and should be used at your own risk. This code is released under an MIT license, with the specificity that you must cite this software if you use it as part of the code for a reseach publication.

The underlying Molmo LLM has its own license, which you must ackowledge and contend with, if you use Molmo as the backend LLM. See *https://molmo.allenai.org/blog*
