from zai.llm_client import call_llm 
from zai.config import load_config
from zai.prompts import prompt_translate, get_prompt_paraphrase, get_prompt_fim, get_prompt_proofread
import re

from typing import Optional, List
# config=load_config()
# print(config)

class FileProcessor(object):
    def apply(self, file: str):
        pass

    def match(self, content:str):
        pass

    def get_regex(self, ):
        return None

    def write(self, filename, new_content, old_content):
        with open(filename, 'r') as fp:
            reference_content = fp.read()
        if reference_content != old_content:
            print("Content changed while processing, aborting!")
            
        else:
            with open(filename, 'w') as fp:
                fp.write(new_content)


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
PREFIX='z_'
SUFFIX='#'
CONTEXT_BRACKET='<[',']>' 
def get_regex_translate():
    return RegexMatcher(
r'(<{(.*)}>' + PREFIX+ 'tr(_[A-Za-z]{2})?(_\([^)]*\))?' + SUFFIX
,['content','lang','prompt'], [None, lambda x: x[1:], lambda x:x[2:-1]],
['',1,'']
)

regex_check = RegexMatcher(
r'(<{([.\n]*)}>'+PREFIX+'check(_\([^)]*\))?' + SUFFIX
,['content','prompt'], [None, lambda x:x[2:-1]],
['',1,'']
)

def get_regex_paraphrase():
    return RegexMatcher(
r'<{(.*?)}>' + PREFIX + 'par(_[0-9]{1,2})?(_\([^)]*\))?' + SUFFIX
,['content','num','prompt'], [None,lambda x: x[1:], lambda x:x[2:-1]],
['',1,'']
)


def get_regex_fim():
    return RegexMatcher(
PREFIX + r'c(_[0-9]{1,2})?(_\([^)]*\))?' + SUFFIX
,['num','prompt'], [lambda x: x[1:], lambda x:x[2:-1]],
[1,'']
)

def get_regex_proofread():
    return RegexMatcher(
r'(<\{.*?\}>)' + PREFIX + 'proof(_\([^)]*\))?' + SUFFIX
,['content','prompt'], [lambda x:x[2:-2], lambda x:x[2:-1]],
['','']
)


regex_fim2 = RegexMatcher(
r'<{(.*?)' + PREFIX + 'cc(_[0-9]{1,2})?(_\([^)]*\))?([.\n]*?)' + SUFFIX
,['text_before','num','prompt','text_after'], [lambda x: x[1:], lambda x:x[2:-1]],
['',1,'','']
)

def extract_answers(text):
    matches = re.findall(r'<answer>(.*?)</answer>', text, re.DOTALL)
    return [match.strip() for match in matches]
    

map_right_to_left = {
    ')': '(',
    ']': '[',
    '}': '{',
    '>': '<'
}

class RegexFileProcessor(FileProcessor):
    def __init__(self, config):
        self.config = config
        self.context_padding = config.get('context_padding',150)

    def match(self, content):
        res, match= self.regex.apply(content)
        return res is not None
    def get_context(self, content, command_match,parsed_prompt):
        query_content= parsed_prompt['content']
        fr, to = command_match.span()
        if CONTEXT_BRACKET[0] in content[:fr] and CONTEXT_BRACKET[1] in content[to:]:
            ctx_fr = content[:fr].rfind(CONTEXT_BRACKET[0])
            ctx_to = to + content[to:].find(CONTEXT_BRACKET[1])
        else:
            ctx_fr = max(0, fr - self.context_padding)
            ctx_to=min(len(content), to + self.context_padding)

        context = '...'+content[ctx_fr:fr] + query_content+ content[to:ctx_to]+'...'
        return context


class TranslateFileProcessor(RegexFileProcessor):
    def __init__(self, config=None):
        self.context_padding = 150
        self.config=config


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
            self.write(file, new_content, content)
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


        
class ParaphraseFileProcessor(RegexFileProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.regex = get_regex_paraphrase()


    def apply(self,file=None):
        print('apply paraphrase')
        with open(file, 'r') as fp:
            content = fp.read()

        result, match=self.regex.apply(content)
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
        
        self.write(file, new_content, content)
        return True

class FimFileProcessor(RegexFileProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.regex = get_regex_fim()
        self.context_padding = 250

    def apply(self, file=None):
        print('Applying FIM processing')
        with open(file, 'r') as fp:
            content = fp.read()

        result, match = self.regex.apply(content)
        if result is None:
            return None

        fr, to = match.span()
        context = '...'+content[max(0, fr - self.context_padding) :fr] + \
                '<FIM>' +  content[to:min(len(content), to + self.context_padding)] + '...'

        num = int(result['num']) if result['num'] else 1
        instruction = result['prompt'] if result['prompt'] else ''
        prompt = get_prompt_fim(
            context=context,
            instruction=instruction,
            num=num
        )
  
        response = call_llm([{'role': 'user', 'content': prompt}], self.config)
        
        answers = extract_answers(response)
        answers_fmt =  answers[0] if len(answers)==1 else ('\n - ' + '\n - '.join(answers) + '\n')
        new_content = content[:fr] + answers_fmt + content[to:]
        self.write(file, new_content, content)
        return True

class ProofreadProcessor(RegexFileProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.regex = get_regex_proofread()
        self.context_padding = 250
    def apply(self, file=None):
        print('Applying proofread')
        with open(file, 'r') as fp:
            content = fp.read()

        result, match = self.regex.apply(content)
        if result is None:
            return None

        fr, to = match.span()
        context= self.get_context(content, match, result)
        prompt = get_prompt_proofread(result['content'], context,result['prompt'])
        print(prompt)
        print(result)
        response = call_llm([{'role': 'user', 'content': prompt}], self.config)
        answers = extract_answers(response)
        print(response)
        print(answers,'len', len(answers))
        new_content = content[:fr] + answers[0] + content[to:]
        self.write(file, new_content, content)
