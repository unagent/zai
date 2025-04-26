
# zAI - Zero Integration AI writing plugin for minimalists.

AI made efficient and controllable -- in any text editor,


## Goals:
- 🎯🤖 **Precise control over what the AI is doing**. No need for elaborate natural language 🗣️ descriptions. Control AI precisely with a few ⌨️ macros typed directly in the editor.
- 🌍 **Works for any editor**, supporting almost any unique specific text editor (neovim, Obsidian, Kile, or whatever you need). The editor just needs to support file reloading 🔄.
- 🎓 **Learn once, use anywhere** 🌍 - since it works in any editor, master it once and apply it everywhere.
- ⚡ **Automating text editing with AI** 🤖 - enabling fast, precise workflows 🎯 for tasks like proofreading, refactoring, or correction ✍️.
- 🔑 **Bring your own API** - works with any OpenAI-compatible API, including locally hosted ones 🏠 (e.g., using vLLM).
- **Bring your own prompt** - develop own commands easily, without programming. [TODO]
- 💾 **Store your LLM calls** - save your usage data to potentially finetune your own LLM later 🌱🧠 [TODO]
- 🆓 **Fully free and open-source** 🔓❤️.


Inspirations: Aider Chat file watch mode www.aider.chat

## How to run:

# Installation 

You need Python (I used 3.10 version).
Please do following
```
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


