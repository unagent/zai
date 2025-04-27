        
import glob,os, typing, re

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
    return meta

def sort_matches_reverse(matches: typing.List[re.Match]):
    matches = matches.sort(key=lambda m: m[1].start(), reverse=True)            
    return matches

def apply_matches(text, matches: typing.List[re.Match], replacements: typing.List[str]):
    matches.sort(key=lambda m: m.start(), reverse=True)                                                                                                                                                                                                                                             
    for match, replacement in zip(matches, replacements):                                                                                                                                                                                                                                           
        start = match.start()                                                                                                                                                                                                                                                                       
        end = match.end()                                                                                                                                                                                                                                                                           
        text = text[:start] + replacement + text[end:]     
    return text