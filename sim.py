import os
import sys
import time
import json
import requests
import argparse
import re
import operator
import traceback

from ollama import Client


# L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L*(%$)L

class Simulatar:
    def __init__(
            self,
            name: str,
            rules: [],
            instructions: [],
            sim_log_path: str,
            temperature: float,
            batch=True,
            model=None,
    ):
        self.name = name
        self.model = model
        self.sim_log_path = sim_log_path
        self.log_path = r'E:\docs\vault14'
        self.sim_id = str(time.time_ns()) + f'_{os.getpid():08x}'
        self.programm_instructions = [rules] + instructions
        self.programm_current_instruction = 0
        self.programmed = batch
        self.max_line_chars = 190
        self.num_ctx = 2048
        self.temperature = temperature
    
    def log(self, msg, end='\n', flush=True):
        print(f'{msg}', end=end, flush=flush)
        
        name = re.sub(r'[^0-9a-zA-Z_\-.]', '_', self.name)
        name = name.replace("__", "_")
        
        log_file = os.path.join(
            self.log_path,
            self.sim_log_path,
            'sim_' + f"{name}_" + str(self.sim_id) + ".md"
        )
        with open(log_file, "at") as log_file_handle:
            full_msg = (msg + end).encode(encoding='utf-8', errors='replace')
            log_file_handle.write(str(full_msg))
    
    def read_context(self):
        with open('context.ids', 'r') as file:
            context = file.read()
            context = [int(str.strip(x)) for x in context.split(' ') if len(str.strip(x)) > 0]
        return context
    
    def execute(self):
        client = Client(host='127.0.0.1')
        
        write_this = 'n'
        
        self.log(f'∠ temp: {self.temperature} ctx: {self.num_ctx} war_id: {self.sim_id}')
        
        try:
            
            models = [
                'dolphin-phi:2.7b-v2.6-q6_K',
                'gfg/solar-10.7b-instruct-v1.0-uncensored',
                'gurubot/llama3-guru-uncensored',
                'mannix/dolphin-2.9-llama3-8b:q5_k_m',
                'mistral:7b',
                'sunapi386/llama-3-lexi-uncensored:8b',
                'dolphin-phi:2.7b-v2.6-q8_0',
                'gurubot/llama3-guru:latest',
                'wizardlm2',
                'war-resolver',
                'llama3:8b-text-q8_0',
                'wizardlm-uncensored:13b-llama2-q5_K_M',
                'wizard-vicuna-uncensored:13b',
                'phi3',
                'impulse2000/dolphincoder-starcoder2-7b:q8_0'
            ]
            
            selected_model_idx = 0
            input_text = '> select model: '
            
            for m in models:
                self.log(f' [{selected_model_idx:-2d}] {m}')
                selected_model_idx += 1
            
            if self.model is None:
                selected_model_idx = int(input(input_text))
                model = models[selected_model_idx]
            else:
                try:
                    selected_model_idx = int(input(input_text))
                except ValueError:
                    model = self.model
                else:
                    model = models[selected_model_idx]
            
            self.log(f'⋤ model: {model} [selected]')
            
            context = None
            
            if self.programmed:
                self.log(f'∐ auto-remove of context')
                if os.path.exists('context.ids'):
                    os.unlink('context.ids')
            
            while True:
                current_chars = 0
                if os.path.exists('context.ids') and write_this != 'y':
                    context = self.read_context()
                    if self.programmed is False:
                        delete = input(f'delete context? ({len(context)} ids) Y/n ')
                        if delete == 'y':
                            self.log('√ ', end='')
                            os.unlink('context.ids')
                
                try:
                    with open('context.ids', 'r') as file:
                        context = file.read()
                        context = [int(str.strip(x)) for x in context.split(' ') if len(str.strip(x)) > 0]
                        self.log(f'œ continue with previous context of {len(context)} ids')
                except FileNotFoundError:
                    context = []
                    self.log('ㆆ new empty context')
                except Exception as e:
                    self.log(f"x loading error: {e}")
                
                if self.programmed:
                    if self.programm_current_instruction > len(self.programm_instructions) - 1:
                        self.programmed = False
                        self.log(f'■ end if program')
                        return
                    else:
                        step_engine = 'setup' if self.programm_current_instruction == 0 and self.programmed else 'prompt'
                        self.log(
                            f'◰ going via program, instruction: {self.programm_current_instruction + 1}/{len(self.programm_instructions)} ...\n'
                            f'⤵ {step_engine}: {self.programm_instructions[self.programm_current_instruction]}'
                        )
                        prompt = self.programm_instructions[self.programm_current_instruction]
                else:
                    prompt = input("Œ Enter the prompt: ")
                
                self.log(f'⅁ {model} linking embeddings relations ...')
                
                options = {
                    'temperature': self.temperature,
                    # 'num_ctx': self.num_ctx,
                    'use_mmap': True,
                    'num_thread': 10,
                    'use_mlock': True,
                    'mirostat_tau': 2.0
                    # 'stop': [
                    #     '<|end|>',
                    #     '<|user|>',
                    #     'user:',
                    #     'assistant:',
                    #     "<|start_header_id|>",
                    #     '<|end_header_id|>',
                    #     '<|eot_id|>',
                    #     '<|reserved_special_token>'
                    # ]
                    # 'repeat_penalty': 1.5,
                    # 'num_predict': 500
                }
                # 'num_predict': 50000,
                # Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)
                
                # 'repeat_penalty': 0.5
                # penalize_newline
                
                prompt += "\n\nHere also 7 additional annotations for nicely tuning your output:"
                '1. Do not echo the input.\n'
                '2. Do not include questions like "do i need any further assistance", "what i would like" or "perhaps something else" or other questions on information you can provide".\n'
                '3. Exclude any questions in response.\n'
                '4. Do not print sources if not asked directly.\n'
                '5. Exclude any "pleases" in response.\n'
                '6. Exclude any proposals about response in response.\n'
                '7. Exclude any Disclaimer or notes in response.\n'
                
                response = None
                for response in client.generate(
                        model=model,
                        prompt=prompt,
                        stream=True,
                        options=options,
                        context=context,
                        # template='<|user|>{{ .Prompt }}<|end|>\n'
                        #          '<|assistant|>{{ .Response }}<|end|>'
                ):
                    current_chars += len(response['response'])
                    
                    if "\n" in response['response']:
                        current_chars = 0
                        self.log(response['response'], end='', flush=True)
                    elif current_chars >= self.max_line_chars:
                        self.log("-")
                        current_chars = 0
                        self.log(str.strip(response['response']), end='', flush=True)
                    else:
                        resp = response['response'].replace('\'', '')
                        if len(resp):
                            self.log(resp, end='', flush=True)
                
                scontext = b''
                if 'context' in response:
                    scontext = ' '.join((str(x) for x in response['context'])).encode('utf-8')
                    scontext += b' '
                
                if self.programmed is False:
                    write_this = input(f"\nadd to memory {len(scontext)} ids? Y/n ")
                    if write_this == 'y' and 'context' in response and len(scontext) > 0:
                        self.log('∜ ', end='')
                        with open('context.ids', 'ab') as file:
                            file.write(scontext)
                            self.log(f"⊫ context {len(scontext)} bytes added")
                    else:
                        if os.path.exists('context.ids'):
                            context = self.read_context()
                        else:
                            context = []
                elif self.programm_current_instruction == 0:
                    with open('context.ids', 'ab') as file:
                        file.write(scontext)
                        self.log(f"\n\n∧ context {len(scontext)} bytes auto-added")
                    if os.path.exists('context.ids'):
                        context = self.read_context()
                    else:
                        context = []
                else:
                    self.log(f'\n☺ context not modified')
                
                self.log(f"∄ resulted context: {len(context)} ids")
                
                if self.programmed:
                    self.programm_current_instruction += 1
        
        except Exception as e:
            self.log('\n\n--')
            self.log(f"x ∓inal error: {e}")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)


####################################################################################################################################################################################

qnum = 2
model_selector = []

####################################################################################################################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process the simulation.')
    parser.add_argument('--scene', help='scene dir')
    
    args = parser.parse_args()
    
    if args.scene is None:
        parser.error('scene dir is required')
    
    print(f'∠ scene: {args.scene}')
    scenario_file = os.path.join('scenes', args.scene, 'scenario.json')
    
    with open(scenario_file, 'rt') as f:
        data = f.read().encode('utf-8')
        program_data = json.loads(data)
        
        print(f'√ loaded "' + program_data["name"] + f'", {len(data)} bytes scenario from {scenario_file}')
    
    program_name = program_data['name']
    program_rules = program_data['init'] + program_data['rules']
    program_instruction = program_data['instructions']
    program_int_biases = program_data['biases']
    program_sim_log_path = program_data['sim_log_path']
    program_rules = program_rules.replace('%source_biases%', program_int_biases)
    program_temperature = program_data['temperature']
    program_model = program_data['model']
    
    process = Simulatar(
        name=program_name,
        rules=program_rules,
        instructions=program_instruction,
        sim_log_path=program_sim_log_path,
        temperature=program_temperature,
        model=program_model,
        batch=True
    )
    
    try:
        sys.exit(process.execute())
    except KeyboardInterrupt:
        process.log('∠ Ctrl-C')
