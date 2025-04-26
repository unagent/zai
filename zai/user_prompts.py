import glob,os

def list_prompts(directory):
    prompt_paths = glob.glob(directory + '/*txt')

    all_prompts = []
    for v in prompt_paths:
        with open(v,'r') as fp:
            content = fp.read()
        name = os.path.basename(v).replace('.txt','')
        all_prompts.append({'name': name, 'content': content})
    
    return all_prompts
