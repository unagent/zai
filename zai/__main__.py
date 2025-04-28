import watchfiles
import re
from pathlib import Path
import argparse
import fnmatch
from zai.config import load_config
from typing import List
from zai.processors import TranslateFileProcessor, FileProcessor, ParaphraseFileProcessor, ProofreadProcessor, FimFileProcessor
from zai.user_prompts import UserPromptProcessor, parse_prompts

def handle_change(change_type, file_path, matchers: List[FileProcessor]):
    # try:
        print('Passed', file_path) 
        with open(file_path, 'r') as f:
            content = f.read()
        for m in matchers:
            if m.match(content=content):
                m.apply(file_path)



            # for line_number, line in enumerate(f, 1):
            #     if re.search(r'#foo\b', line):
            #         print(f"{file_path}:{line_number} - {line.strip()}")
    # except Exception as e:
    #     print(f"Error reading {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--patterns', nargs='+', default=['*.txt'],
                        help='File patterns to watch (e.g. "*.txt", "src/*.cpp")')

    parser.add_argument('--config', default='config.json')
    parser.add_argument('--prompts', default='user_prompts/')
    args = parser.parse_args()
    
    config = load_config(args.config)

    prompt_processors = [UserPromptProcessor(p, config) for p in parse_prompts(args.prompts)]
    matchers = [#TranslateFileProcessor(config), 
                ProofreadProcessor(config), ParaphraseFileProcessor(config), FimFileProcessor(config)] + \
        prompt_processors
    def file_filter(change_type, file_path):
        return (
            'deleted' not in str(change_type) and
            any(fnmatch.fnmatch(file_path, pattern) for pattern in args.patterns) and
            '.git' not in file_path
        )

    for changes in watchfiles.watch(
        '.', 
        watch_filter=file_filter,
    ):
        for change_type, path_str in changes:
            file_path = Path(path_str)
            handle_change(change_type, file_path, matchers)

if __name__ == '__main__':
    main()