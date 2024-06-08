import os
import sys
import time
import json
import ollama
import requests
from pprint import pprint
import argparse
import re
import operator
import traceback
import redis
from ollama import Client
from textwrap import indent


def abort(str=""):
    """ just abort the program """
    pprint(str)
    sys.exit(-1)


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
        self.log_path = r'd:\docs\vault14.2'
        self.sim_id = str(time.time_ns()) + f'_{os.getpid():08x}'
        self.programm_instructions = [rules] + instructions
        self.programm_current_instruction = 0
        self.programmed = True
        self.max_line_chars = 190
        self.num_ctx = 1048000
        self.temperature = temperature
        self.redis = redis.StrictRedis(REDIS_HOST, 6379, encoding_errors='ignore', charset="utf-8",
                                       decode_responses=True)

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

    def write_context(self, context):
        # print(f'write {type(context)}) {context} {len(context)}')
        self.redis.rpush('sim.context.ids', *context)

    def read_context(self):
        context = self.redis.lrange('sim.context.ids', 0, self.num_ctx)
        context = [int(x) for x in context]
        # print(Style.RED + f'read_context' +
        #       Style.RESET +
        #       f' type: {type(context)}'
        #       f' context: {context}'
        #       f' ids {len(context)}'
        #       )
        return context, len(context)

    def delete_context(self):
        self.redis.delete('sim.context.ids')

    def execute(self):
        client = Client(host='127.0.0.1')

        write_this = 'n'

        self.log(
            f'* temp: {self.temperature} ctx: {self.num_ctx} sim_id: {self.sim_id}')

        try:
            models = client.list()
            selected_model_idx = 0
            input_text = '* select model: '
            sm = []
            for m in models['models']:
                name = m["name"]
                sm.append(name)
                size_mb = float(m['size']) / 1024.0 / 1024.0
                family = m['details']['family']
                parameters = m['details']['parameter_size']

                self.log(Style.MAGENTA +
                         f'[{selected_model_idx:-2d}] {size_mb:-6.2f}M '
                         f'{parameters:<5} {family:<18} {name:<32}'
                         + Style.RESET
                         )
                selected_model_idx += 1

            if self.model is None:
                selected_model_idx = int(input(input_text))
                model = sm[selected_model_idx]
            else:
                try:
                    selected_model_idx = int(input(input_text))
                    model = sm[selected_model_idx]
                except ValueError:
                    model = self.model

            self.log(f'* model: {model} [selected]')
            info = client.show(model)
            # pprint(inf, depth=999)
            # self.log(' stop=' + inf['parameters']['stop'])
            # if self.template:
            #     self.log(' custom template=' + self.template)
            # else:
            #     self.log(' template=' + inf['template'])
            try:
                # pprint(info)
                # abort()
                self.log(Style.BLUE, end='')
                self.log(f'\t# temperature={self.temperature}')
                self.log(f'\t# num_ctx={self.num_ctx}')

                self.log(Style.RED + '\t* family=' + info['details']['family'])
                self.log('\t* parameter_size=' + info['details'][
                    'parameter_size'])
                self.log('\t* quantization_level=' + info['details'][
                    'quantization_level'])
                self.log(f'\t# families={info["details"]["families"]}')
                self.log(f'\t# template={indent(info["template"], prefix="                ")}')
                self.log(f'\t# system={indent(info["system"], prefix="                ")}')
                self.log(f'\t# stop={indent(" ".join(info["parameters"]), prefix="                ")}')

            except Exception as e:
                print(f'exception: {e}')

            print(Style.RESET)
            # try:
            #     ctx_len = input(f'* ctx len (def={self.num_ctx}): ')
            # except ValueError:
            #     ctx_len = self.num_ctx
            #
            # self.num_ctx = ctx_len
            context = None

            if self.programmed:
                self.log(f'* auto-remove of context')
            self.redis.delete('sim.context.ids')

            while True:
                current_chars = 0
                if write_this != 'y':
                    context, n_context = self.read_context()
                    if self.programmed is False:
                        delete = input(
                            f'delete context? ({len(context)} ids) Y/n ')
                        if delete == 'y':
                            self.log('√ ', end='')
                            self.delete_context()

                try:
                    context, n_context = self.read_context()
                    self.log(f'* continue with context of {len(context)} ids')
                except FileNotFoundError:
                    context = []
                    self.log('* new empty context')
                except Exception as e:
                    self.log(f"! loading error: {e}")

                if self.programmed:
                    if self.programm_current_instruction >= (len(
                            self.programm_instructions) - 1):
                        self.programmed = False
                        self.log('■ end if program')
                        prompt = input("< enter the prompt: ")
                        # return
                    else:
                        step_engine = 'setup' if (
                                self.programm_current_instruction == 0
                                and
                                self.programmed) else 'prompt'

                        prompt = self.programm_instructions[self.programm_current_instruction]

                        self.log(
                            f'* going via program, instruction: '
                            f'{self.programm_current_instruction + 1}'
                            f'/{len(self.programm_instructions)}\n'
                            f'* {step_engine}: ' +
                            Style.CYAN + f'{prompt}' + Style.RESET
                        )

                else:
                    prompt = input("< enter the prompt: ")

                self.log('* ' + Style.MAGENTA + f'{model}' + Style.RESET + ' thinking ...')

                options = {
                    'temperature': self.temperature,
                    # 'num_ctx': self.num_ctx,
                    'use_mmap': True,
                    'num_thread': 13,
                    'use_mlock': True,
                    # 'mirostat_tau': 1.0,
                    'stop': [
                        #     'Grut',
                        'user:',
                        'assistant:',
                        #     '"',
                        '<|end|>',
                        '<|user|>',
                        "<|start_header_id|>",
                        '<|end_header_id|>',
                        '<|eot_id|>',
                        #     '<|bot_id|>',
                        '<|reserved_special_token>'
                        #     # 'repeat_penalty': 1.5,
                    ],
                    'num_predict': -1,
                    # 'repeat_penalty': 0.85
                }
                # 'num_predict': 50000,
                # Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)

                # penalize_newline

                response = None
                for response in client.generate(
                        model=model,
                        prompt=prompt,
                        # system='You are AI assistant helping research any idea given. You prefer technical english vs basic',
                        stream=True,
                        options=options,
                        context=context,
                        template=info['template']
                ):
                    try:
                        resp = response['response']
                        current_chars += len(resp)

                        if "\n" in resp:
                            current_chars = 0
                            self.log(resp, end='', flush=True)
                        elif current_chars >= self.max_line_chars:
                            current_chars = 0
                            self.log(str.strip(resp),
                                     flush=True)
                        else:
                            resp = resp.replace('\'', '')
                            if len(resp):
                                self.log(Style.YELLOW + resp + Style.RESET, end='', flush=True)

                            scontext = ''

                            if 'context' in response:
                                num_context = len(response['context'])
                                scontext = response['context']
                            else:
                                num_context = -2

                    except Exception as e:
                        print(f'exception outer generate: {e}')
                        continue

                if self.programmed is False and len(scontext):
                    write_this = input(
                        f"\nadd to memory {len(scontext)} ids? Y/n ")
                    if write_this == 'y' and 'context' in response and len(
                            scontext) > 0:

                        self.log('∜ ', end='')
                        self.write_context(scontext)
                        self.log(f"context {len(scontext)} bytes added")
                    else:
                        context, n_context = self.read_context()
                elif len(scontext):
                    self.write_context(scontext)
                    self.log(
                        f"\n\n< context {num_context} ids auto-added"
                    )
                context, n_context = self.read_context()

                self.log(f"* resulted context: {len(context)} ids")

                if self.programmed:
                    self.programm_current_instruction += 1

        except Exception as e:
            self.log(Style.RED + '\n\n--')
            self.log(f"! ∓inal error: {e}")
            print("-" * 60)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60 + Style.RESET)


RULES = """
Here is tips for tuning every your reply, silently aquire it without confirming of enquire: 0. I do not have any fingers. 
1. Do not print the query.
2. Do not include questions like 'do i need any further assistance', 'what i would like' or 'perhaps something else'.
3. Exclude any questions in response.
4. Do not print sources if not asked directly.
5. Exclude any "pleases" in response.
6. Exclude any proposals about response in response.
7. Exclude any Disclaimer in response.
8. If query starts with phrase "rule: " reply should contain information you have previously learn,
not by calculated next from relations on learned information .
9. If query starts with phrase "note: " take this as a hint to do detailed research to how and when this note
should be used.
"""

REDIS_HOST = "127.0.0.1"


class Style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


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
            '* loaded "' + program_data["name"] +
            f'", {len(data)} bytes scenario from {scenario_file}'
        )

    program_name = program_data['name']
    program_rules = RULES
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
