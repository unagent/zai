from llm_client import call_llm 
from config import load_config
import re

from typing import Optional
# config=load_config()
# print(config)

class FileProcessor(object):
    def apply(self, file: str):
        pass

    def match(self, content:str):
        pass

    def get_regex(self, ):
        return None


import re

class RegexMatcher(object):
    def __init__(self, regex, group_keys, postprocessors=None, defaults=None):
        self.regex = regex
        self.group_keys = group_keys
        if postprocessors == None:
            postprocessors = [None for k in group_keys]
        if defaults == None:
            defaults = [None for k in group_keys]

        self.postprocessors = postprocessors
        self.defaults = defaults
    def apply(self, text):
        match = re.search(self.regex, text,re.DOTALL)
        if match is None:
            return None, None
        else:
            result = dict(list(zip(self.group_keys,match.groups())))
            for i, k in enumerate(self.group_keys):
                if result[k] is not None and self.postprocessors[i] is not None:
                    result[k] = self.postprocessors[i](result[k])
                if result[k] is None:
                    result[k] = self.defaults[i]
            return result, match

regex_translate = RegexMatcher(
r'(<{(.*)}>#zai_tr(_[A-Za-z]{2})?(_\([^)]*\))?'
,['content','lang','prompt'], [None, lambda x: x[1:], lambda x:x[2:-1]],
['',1,'']
)

regex_check = RegexMatcher(
r'(<{([.\n]*)}>#zai_check(_\([^)]*\))?'
,['content','prompt'], [None, lambda x:x[2:-1]],
['',1,'']
)

regex_paraphrase = RegexMatcher(
r'<{(.*?)}>#zai_par(_[0-9]{1,2})?(_\([^)]*\))?'
,['content','num','prompt'], [None,lambda x: x[1:], lambda x:x[2:-1]],
['',1,'']
)


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

def extract_answers(text):
    matches = re.findall(r'<answer>(.*?)</answer>', text, re.DOTALL)
    return [match.strip() for match in matches]
    

map_right_to_left = {
    ')': '(',
    ']': '[',
    '}': '{',
    '>': '<'
}

class RegexMatcher(object):
    def __init__(self, regex, group_keys):
        self.regex = regex
        self.group_keys = group_keys

    


class TranslateFileProcessor(FileProcessor):
    def __init__(self, config=None):
        self.context_padding = 150
        self.config=config


    def match(self, content):
        return '#zai_tr' in content

    def exec_llm(self, lang, context, text):
        prompt = prompt_translate.replace(
            '<<lang>>', lang
        ).replace('<<context>>', context)\
        .replace('<<text>>',text)
        response = call_llm([{'role': 'user', 'content': prompt}], self.config)
        answer_match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL)
        return answer_match.group(1).strip() if answer_match else response.strip()

    def apply(self,file=None):
        with open(file, 'r') as fp:
            content = fp.read()

        regex_match =  \
            re.search("#zai_tr_[A-Za-z]{2}", content)
        if regex_match is None:
            return False
        
        fr, to = regex_match.span()
        print(regex_match)
        if fr >= 2 and \
             content[fr-2:fr] in ['}>'] and '<{' in content[:fr-2]:
            new_content = self.process_with_marks(regex_match, content)
            # print(new_content)
            with open(file, 'w') as fp:
                fp.write(new_content)
            return True
        return False
        
    def process_with_marks(self,command_match, content):
        fr, to = command_match.span()
        start_of_text = content[:fr-2].rfind('<{')
        text = content[start_of_text+2: fr-2]
        lang = command_match.group()[-2:]

        context = content[max(0,start_of_text+2 - self.context_padding)
        : min(len(content), fr-2+self.context_padding)]
        answer = self.exec_llm(lang, context, text)
        print(answer)

        return content[:start_of_text] + text +'\n' + answer + '\n' + content[to:]


class ParaphraseFileProcessor(TranslateFileProcessor):
    def __init__(self, config=None):
        super().__init__(config)

    def process_with_marks(self, command_match, content):
        return super().process_with_marks(command_match, content)
    def match(self, content):
        res, match= regex_paraphrase.apply(content)
        return res is not None

    def apply(self,file=None):
        print('apply paraphrase')
        with open(file, 'r') as fp:
            content = fp.read()

        result, match=regex_paraphrase.apply(content)
        print(result, match)
        if result is None:
            return None
        
        # Get context around the match
        fr, to = match.span()
        context = content[max(0, fr - self.context_padding)
                        : min(len(content), to + self.context_padding)]
        
        prompt = get_prompt_paraphrase(
            text=result['content'],
            req=result['prompt'],
            context=context,
            num=int(result['num']) if result['num'] else 1
        )
        
        response = call_llm([{'role': 'user', 'content': prompt}], self.config)
        answers = extract_answers(response)
        
        # Replace original text with answers
        new_content=content[:fr] + result['content'] \
        + '\n - ' + '\n - '.join(answers) + content[to:]
        
        with open(file, 'w') as fp:
            fp.write(new_content)
        return True
