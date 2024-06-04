import os
import sys
import time
import json
import ollama
import requests
import argparse
import re
import operator
import traceback

from ollama import Client


class Simulatar:
    time_created = time.time_ns()

    def __init__(
            self,
            name: str,
            rules: [],
            instructions: [],
            sim_log_path: str,
            temperature: float,
            batch=True,
            model=None,
            template=None
    ):
        self.name = name
        self.template = template or ""
        self.model = model
        self.sim_log_path = sim_log_path
        self.log_path = r'd:\docs\vault14'
        self.sim_id = str(time.time_ns()) + f'_{os.getpid():08x}'
        self.programm_instructions = [rules] + instructions
        self.programm_current_instruction = 0
        self.programmed = batch
        self.max_line_chars = 190
        self.num_ctx = 8192
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
        with open(log_file, "ab") as log_file_handle:
            full_msg = (msg + end).encode(encoding='utf-8', errors='ignore')
            log_file_handle.write(full_msg)

    def read_context(self):
        with open('context.ids', 'r') as file:
            context = file.read()
            n_context = context.split(' ')
            context = [int(str.strip(x)) for x in context.split(' ') if
                       len(str.strip(x)) > 0]
        return context, n_context

    def execute(self):
        client = Client(host='127.0.0.1')

        write_this = 'n'

        self.log(
            f'> temp: {self.temperature} ctx: {self.num_ctx} sim_id: {self.sim_id}')

        try:
            models = client.list()
            selected_model_idx = 0
            input_text = '> select model: '
            sm = []
            for m in models['models']:
                name = m["name"]
                sm.append(name)
                modified = m['modified_at']
                size_mb = float(m['size']) / 1024.0 / 1024.0
                family = m['details']['family']
                parameters = m['details']['parameter_size']

                self.log(
                    f'[{selected_model_idx:-2d}] {size_mb:-6.2f}M '
                    f'{parameters:<4} {name:_<52} {family:<12} {modified}'
                )
                selected_model_idx += 1

            if self.model is None:
                selected_model_idx = int(input(input_text))
                model = sm[selected_model_idx]
            else:
                try:
                    selected_model_idx = int(input(input_text))
                except ValueError:
                    model = self.model
                else:
                    model = sm[selected_model_idx]

            self.log(f'> model: {model} [selected]')
            inf = client.show(model)
            # self.log(' stop=' + inf['parameters']['stop'])
            # if self.template:
            #     self.log(' custom template=' + self.template)
            # else:
            #     self.log(' template=' + inf['template'])
            self.log('\t> family=' + inf['details']['family'])
            self.log('\t> parameter_size=' + inf['details'][
                'parameter_size'])
            self.log('\t> quantization_level=' + inf['details'][
                'quantization_level'])
            context = None

            if self.programmed:
                self.log(f'> auto-remove of context')
                if os.path.exists('context.ids'):
                    os.unlink('context.ids')

            while True:
                current_chars = 0
                if os.path.exists('context.ids') and write_this != 'y':
                    context, n_context = self.read_context()
                    if self.programmed is False:
                        delete = input(
                            f'delete context? ({len(context)} ids) Y/n ')
                        if delete == 'y':
                            self.log('√ ', end='')
                            os.unlink('context.ids')

                try:
                    with open('context.ids', 'r') as file:
                        context = file.read()
                        context = [int(str.strip(x)) for x in
                                   context.split(' ') if len(str.strip(x)) > 0]
                        self.log(
                            f'> continue with previous context of {len(context)} ids')
                except FileNotFoundError:
                    context = []
                    self.log('> new empty context')
                except Exception as e:
                    self.log(f"! loading error: {e}")

                if self.programmed:
                    if self.programm_current_instruction > len(
                            self.programm_instructions) - 1:
                        self.programmed = False
                        self.log('■ end if program')
                        prompt = input("< enter the prompt: ")
                        # return
                    else:
                        step_engine = 'setup' if (
                                self.programm_current_instruction == 0
                                and
                                self.programmed) else 'prompt'
                        self.log(
                            f'> going via program, instruction: '
                            f'{self.programm_current_instruction + 1}'
                            f'/{len(self.programm_instructions)}\n'
                            f'> {step_engine}: '
                            f'{self.programm_instructions[self.programm_current_instruction]}'
                        )
                        prompt = self.programm_instructions[
                            self.programm_current_instruction]
                else:
                    prompt = input("< enter the prompt: ")

                self.log(f'> {model} thinking ...')

                options = {
                    'temperature': self.temperature,
                    # 'num_ctx': self.num_ctx,
                    'use_mmap': True,
                    'num_thread': 10,
                    'use_mlock': True,
                    # 'mirostat_tau': 1.0,
                    'stop': [
                        'Grut',
                        'user:',
                        'assistant:',
                        '"',
                        '<|end|>',
                        '<|user|>',
                        "<|start_header_id|>",
                        '<|end_header_id|>',
                        '<|eot_id|>',
                        '<|bot_id|>',
                        '<|reserved_special_token>'
                        # 'repeat_penalty': 1.5,
                    ],
                    #'num_predict': -1
                }
                # 'num_predict': 50000,
                # Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)

                # 'repeat_penalty': 0.5
                # penalize_newline

                response = None
                for response in client.generate(
                        model=model,
                        prompt=prompt,
                        # system='You are research assistant helping deploy '
                        #        'any idea to decomposed detailed response',
                        stream=True,
                        options=options,
                        context=context,
                        template=self.template
                ):
                    current_chars += len(response['response'])

                    if "\n" in response['response']:
                        current_chars = 0
                        self.log(response['response'], end='', flush=True)
                    elif current_chars >= self.max_line_chars:
                        self.log("-")
                        current_chars = 0
                        self.log(str.strip(response['response']), end='',
                                 flush=True)
                    else:
                        resp = response['response'].replace('\'', '')
                        if len(resp):
                            self.log(resp, end='', flush=True)

                scontext = b''

                if 'context' in response:
                    num_context = len(response['context'])
                    scontext = ' '.join(
                        (str(x) for x in response['context'])).encode(
                        'utf-8',
                        'ignore'
                    )
                    scontext += b' '
                else:
                    num_context = -2

                if self.programmed is False and len(scontext):
                    write_this = input(
                        f"\nadd to memory {len(scontext)} ids? Y/n ")
                    if write_this == 'y' and 'context' in response and len(
                            scontext) > 0:
                        self.log('∜ ', end='')
                        with open('context.ids', 'ab') as file:
                            file.write(scontext)
                            self.log(f"context {len(scontext)} bytes added")
                    else:
                        if os.path.exists('context.ids'):
                            context, n_context = self.read_context()
                        else:
                            context = []
                else:
                    with open('context.ids', 'ab') as file:
                        file.write(scontext)
                        self.log(
                            f"\n\n< context {num_context} ids auto-added"
                        )
                    if os.path.exists('context.ids'):
                        context, n_context = self.read_context()
                    else:
                        context = []

                self.log(f"> resulted context: {len(context)} ids")

                if self.programmed:
                    self.programm_current_instruction += 1

        except Exception as e:
            self.log('\n\n--')
            self.log(f"! ∓inal error: {e}")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process the simulation.')
    parser.add_argument('--scene', help='scene dir')

    args = parser.parse_args()

    if args.scene is None:
        parser.error('scene dir is required')

    print(f'< scene: {args.scene}')
    scenario_file = os.path.join('scenes', args.scene, 'scenario.json')

    with open(scenario_file, 'rt') as f:
        data = f.read().encode('utf-8')
        program_data = json.loads(data)

        print(
            '> loaded "' + program_data["name"] +
            f'", {len(data)} bytes scenario from {scenario_file}'
        )

    program_name = program_data['name']
    program_rules = program_data['init'] + program_data['rules']
    program_instruction = program_data['instructions']
    program_int_biases = program_data['biases']
    program_sim_log_path = program_data['sim_log_path']
    program_rules = program_rules.replace(
        '%source_biases%',
        program_int_biases
    )
    program_temperature = program_data['temperature']
    program_model = program_data['model']
    program_model_template = program_data['template']

    process = Simulatar(
        name=program_name,
        rules=program_rules,
        template=program_model_template,
        instructions=program_instruction,
        sim_log_path=program_sim_log_path,
        temperature=program_temperature,
        model=program_model,
        batch=True
    )

    try:
        sys.exit(process.execute())
    except KeyboardInterrupt:
        process.log('! Ctrl-∠')
