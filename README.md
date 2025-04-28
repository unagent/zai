
# zAI - Zero Integration AI writing plugin for minimalists.

AI made efficient and controllable -- in any text editor (VSC, Obsidian et cetera). 

For best experience I recommend editor that automatically reloads files changed on the disk (as plugin edits files in the background).

## Goals:
- 🎯🤖 **Precise control over what the AI is doing**. No need for elaborate natural language 🗣️ descriptions. Control AI precisely with a few ⌨️ macros typed directly in the editor.
- 🌍 **Works for any editor**, supporting almost any unique specific text editor (neovim, Obsidian, Kile, or whatever you need). The editor just needs to support file reloading 🔄.
- 🎓 **Learn once, use anywhere** 🌍 - since it works in any editor, master it once and apply it everywhere.
- ⚡ **Automating text editing with AI** 🤖 - enabling fast, precise workflows 🎯 for tasks like proofreading, refactoring, or correction ✍️.
- 🔑 **Bring your own API** - works with any OpenAI-compatible API, including locally hosted ones 🏠 (e.g., using vLLM).
- **Bring your own prompt** - develop own commands and prompts easily.
- 💾 **Store your LLM calls** - save your usage data to potentially finetune your own LLM later 🌱🧠 [TODO]
- 🆓 **Fully free and open-source** 🔓❤️.


Inspirations: Aider Chat file watch mode www.aider.chat

## How to run:

# Installation 

You need Python (I used 3.10 version).
Please do following
```
pip install watchfiles
pip install https://github.com/unagent/zai.git
```
# Configuration
Please set your LLM API in config, saving config.json file in your working directory.

Such as 

```
{
    "OPENAI_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "OPENAI_API_URL": "https://api.yourprovider.here/v1",
    "OPENAI_API_MODEL": "google/gemma-3-27b-it",
}
```
Host your own LLM with vLLM/Ollama OpenAI compatible API locally or authenticate with any public API providers URL, with your account's secret key.  Tool was tested with gemma-3-27B.
Here are few provider's API URLs for reference
```
https://api.openai.com/v1
https://api.mistral.ai/v1
https://openrouter.ai/api/v1
https://api.deepinfra.com/v1/openai
```
## Run
Open Terminal or CMD and start tool in your working directory (where you have text files).

Specify your config as --config, 
and specify file paths formats with --patterns (here we use latex files and MD files). 
```
zai --config /home/user/zac/config.json --patterns '*tex' '*.md'
```
Done, now tool will watch for commands that you type in your editor when file is being saved. 


## Run - with user prompts
If you want use your own prompts, please call it as follows

```
zai --config /home/user/zac/config.json --patterns '*tex' '*.txt' --prompts user_prompts/
```
where `user_prompts` is directory with prompts. 
Please refer to `user_prompts/rhyme.txt` for example of user prompt.

## Commands

Here are examples of commands. You type command in the text, save file, and the tool finds edited file and reads all the relevant information.
LLM output will be put directly in your file.


Propose 3 simple short paraphrases of text
```
<{Your text goes here}>z_par_3_(short, simple)#
```

Perform autocomplete.
```
z_c_(elaborate, unexpected finish, up to 10 words)#
```

### User prompts
User prompt (please use `:` plus prompt name to execute it).
Keyword arguments are supported.

Here, using provided example we give 3 options of rhymed lines
for '...while being different from zero at the same time.'

name, req correspond to `<<name>>` and `<<req>>` in the prompt template. 
```
<{...while being different from zero at the same time.}>z_:rhyme_(num=3)_(req=eloquent, surprising)#
```

Commands generally start with chunk of text in <{...}> (if applicable) and z_ as prefix. They end with # suffix (this is to support editors that constantly save files,
like Obsidian).
