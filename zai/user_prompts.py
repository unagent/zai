        
import glob,os, typing, re
from zai.processors import RegexFileProcessor, RegexMatcher, PREFIX, SUFFIX,\
extract_answers, call_llm

def list_prompts(directory):
    prompt_paths = glob.glob(directory + '/*txt')

    all_prompts = []
    for v in prompt_paths:
        with open(v,'r') as fp:
            content = fp.read()
        name = os.path.basename(v).replace('.txt','')
        all_prompts.append({'name': name, 'prompt': content})
    
    return all_prompts

args_braces =r'<<([^>]|>(?!>))*>>' 
def parse_prompt_metadata(prompt):
    meta = {}
    match_answer = re.search('<FORMAT_ANSWER>',prompt)
    meta['match_answer'] = match_answer
    optional_braces = r'<{([^}]|}(?!>))*}>'
    all_matches_for_optionals = list(re.finditer(optional_braces, prompt))
    meta['optional_args'] = {}
    for optional in all_matches_for_optionals:
        match_key = re.search(args_braces, optional.group())
        meta['optional_args'][match_key.group()] = optional
    
    meta['standard_args'] = {}

    args_matches = list(re.finditer(args_braces, prompt))
    for arg in args_matches:
        if arg.group() not in meta['optional_args']:
            meta['standard_args'][arg.group()] = arg
    
    args_all = [arg.group() for arg in args_matches]
    return meta, args_all

def sort_matches_reverse(matches: typing.List[re.Match]):
    matches = matches.sort(key=lambda m: m[1].start(), reverse=True)            
    return matches

def apply_matches(text, matches: typing.List[re.Match], replacements: typing.List[str]):
    if len(matches) != len(replacements):
        raise ValueError("Number of matches and replacements must be equal")
    matches_numbered = list(zip(range(len(matches)), matches))
    matches_numbered.sort(key=lambda m: m[1].start(), reverse=True)                                                                                                                                                                                                                                             
    for idx, match in matches_numbered:
        start = match.start()                                                                                                                                                                                                                                                                       
        end = match.end()                                                                                                                                                                                                                                                                           
        text = text[:start] + replacements[idx] + text[end:]     
    return text


def prepare_prompt(prompt, metadata, argument_values,mandatory_args=[]):
    text= prompt
    matches = [('optional', m) for m in metadata['optional_args'].values()]  \
    + [('arg',m) for m in metadata['standard_args'].values()] + [('answer',metadata['match_answer'])]
    matches.sort(key=lambda m: m[1].start(), reverse=True)            
    processed_args = []
    for typE, match in (matches):
        if typE == 'optional':
            txt = match.group()[2:-2]
            braces = list(re.finditer(args_braces, txt))
            is_considered = any([b.group() in argument_values for b in braces])
            if not is_considered:

                text= apply_matches(text, [match], [''])
                continue
            repl = [argument_values.get(b.group(),'') for b in braces]
            txt2=apply_matches(txt, braces, repl)
            text= apply_matches(text, [match], [txt2])
        if typE == 'answer':
            num_answers = argument_values.get('<<num>>', '1') 
            repl = 'Please format your answer as follows\n' + '<answer>...</answer>\n'*int(num_answers)

            text= apply_matches(text, [match], [repl])
        if typE == 'arg':
            text= apply_matches(text, [match], [argument_values.get(match.group(),'')])
    return text

match_braces = '(_\([^)]*\))?'

def get_regex_proofread():
    return RegexMatcher(
r'(<\{.*?\}>)' + PREFIX + r':?' + SUFFIX
,['content','prompt'], [lambda x:x[2:-2], lambda x:x[2:-1]],
['','']
)

def make_regex(annotated_prompt):
    key = annotated_prompt['key']
    regex= r'(<\{.*?\}>)' + PREFIX + r':' + key 
    for i in range(len(annotated_prompt['args'])-1):
        regex += match_braces
    regex += SUFFIX
    return regex

def parse_prompts(directory):
    prompts = list_prompts(directory)
    prompts_annotated = [{
        'key':p['name'], 'prompt': p['prompt'], 'meta': parse_prompt_metadata(p['prompt'])[0],'args':parse_prompt_metadata(p['prompt'])[1]
    } for p in prompts]
    prompts_filtered = []
    for p in prompts_annotated:
        if '<<text>>' not in p['prompt']:
            print('Warning: <<text>> tag not found in prompt',p)
            continue
        p['regex'] = make_regex(p)
        prompts_filtered.append(p)
    return prompts_filtered

    
class RegexMatcherAnyPrompt(object):
    def __init__(self, regex, prompt):
        self.regex = regex
        self.prompt = prompt
    def apply(self,text):
        p = self.prompt
        match = re.search(p['regex'], text)
        if match is None:
            return None, None
        groups = match.groups()
        named_args = {'<<text>>':groups[0]}
        unnamed_args=[]
        for g in groups[1:]:
            if g is None:
                continue
            name_match= re.match(r'_\(([a-z_\-]*)=([^)]*)\)', g)
            if name_match is not None:
                name1 = name_match.group(1)
                arg1 = name_match.group(2)
                if f'<<{name1}>>' in p['args']:
                    named_args[f'<<{name1}>>'] = arg1
                    continue
            unnamed_args.append(g[2:-1])
        unnamed_args_keys = [ar for ar in p['args'] if ar !='<<text>>' and ar not in named_args]
        for key, value in zip(unnamed_args_keys,unnamed_args):
            named_args[key] = value
        return named_args, match

class UserPromptProcessor(RegexFileProcessor):
    def __init__(self, prompt_annotated, config):
        super().__init__(config)
        self.regex = RegexMatcherAnyPrompt(
            prompt_annotated['regex'], prompt_annotated)
        self.p = prompt_annotated
        print('User prompt:', self.p)
    
    def apply(self, file=None):
        print('User prompt', self.p['key'], self.p['args'])
        with open(file, 'r') as fp:
            content = fp.read()

        result, match = self.regex.apply(content)
        print('Args are', result)
        if result is None:
            return None
        fr, to = match.start(), match.end()
        prompt = prepare_prompt(self.p['prompt'], self.p['meta'], result)
        
        response = call_llm([{'role': 'user', 'content': prompt}], self.config)
        answers = extract_answers(response)
        
        # Replace original text with answers
        new_content=content[:fr] + result['<<text>>'] \
        + '\n - ' + '\n - '.join(answers) + content[to:]
        self.write(file, new_content, content)
        




    
    

