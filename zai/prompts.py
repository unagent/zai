prompt_translate = '''Please translate this text to <<lang>>.

Text:
<<text>>

Here is broader context, in which sentence appears.
Please use it to understand text meaning and context.

Context:
<<context>>


Format your response as:
<answer>
...
</answer>
'''



def get_prompt_paraphrase(text,req, context,num=1):

    what = ''
    
    if num > 1:
        what += f',please provide {num} distinct paraphrases '

    if req is not None and req != '':
        what += ' according to user requirements.'
        what += '\nRequirements:' + req

    prompt_paraphrase = '''Please paraphrase or improve
    this text <<what>>

    Text:
    <<text>>


    Here is broader context, in which sentence appears.
    Please refer to context to better understand text meaning.
    Use only text for processing.

    Context:
    <<context>>

    Please format your answers as follows:
    '''.replace('<<text>>',text).replace(
        '<<context>>', context
    ).replace('<<what>>', what)
    for i in range(num):
        prompt_paraphrase +='\n<answer>...</answer>'
    return prompt_paraphrase

def get_prompt_fim(context, instruction, num=1):
    """Generate FIM autocompletion prompt with specified context and instruction"""
    prompt = f'''Perform FIM autocompletion, writing text that should replace <FIM> tag in text according to instruction.

Instruction: {instruction}

Text:
{context}

Format your response as:'''
    
    for i in range(num):
        prompt += '\n<answer>...</answer>'
    return prompt
