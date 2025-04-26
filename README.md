
# zAI - Zero Integration AI writing plugin for minimalists and vimmers

AI made efficient and controllable in any text editor,


## TLDR:
- *Precise control what AI is doing*. No need to write elaborate commands. Fine grained control of context.
- *Works for any editor*, including vim and any simple lightweight editor. 
- *Automating text editing with AI* - fast, precise workflow for proofreading, refactoring or correction.
- *Bring your own API* - works for any OpenAI compatible API including locally hosted with e.g. vLLM. 
- *Fully free and open-source* 

Inspirations: Aider Chat file watch mode. 

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


