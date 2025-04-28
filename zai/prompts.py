prompt_translate = '''Please translate this text to <<lang>>. <<prompt>>

Text:
<<text>>

Here is broader context, in which Text appears.
Please use it only to undersand text meaning.
Translate only Text above, not context.

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

def get_prompt_fim(context, instruction='', num=1):
    what = ''
    if instruction != '':
        what = f' according to the instruction.\nInstruction: {instruction}\n'
    if num > 1:
        what += f'Please provide {num} distinct completion options.'
    prompt = f'''Perform FIM (fill in the middle) autocompletion, writing text that should replace <FIM> tag in text {what}

Text:
{context}

Format your response as:'''
    
    for i in range(num):
        prompt += '\n<answer>...</answer>'
    return prompt

prompt_proofread = '''
Perform proofreading of text, correcting any grammar error and typos. Please label errors by parentheses, showing text replacement 
to correct error. <<hint>>

Here is example:
Input: 
I am a firefihgter, but my fathr was an policeman.
Output: 
I am a (firefihgter|firefighter), but my (fathr|father) was (an|a) policeman.

Input:
I walking in the beach today.
Output:
I (|am) walking (in|on) the beach.

Here is text to proofread:
Text:
<<text>>

Here is context, use it to understand text better. Do not process it, process "Text:" only.
<<context>>



Please format your output as follows:
<answer>...</answer>
'''
def get_prompt_proofread(text, context,hint):
    if hint !='':
        'Also satisfy this hint:' + hint
    return prompt_proofread.replace('<<text>>',text).replace('<<context>>',context).replace('<<hint>>', hint)
    