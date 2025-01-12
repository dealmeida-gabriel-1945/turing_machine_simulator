# This class will hold all Touring Machine's data
import parameters
import util.parameter_util as parameter_util


class TuringMachine:
    def __init__(self, steps, blocks=None):
        if blocks is None:
            blocks = list()
        self.blocks = blocks
        self.index = 0
        self.tape = list()
        self.steps = steps

    def get_final_tape_content(self):
        return ''.join(self.tape)

    def accept(self, original_tape):
        main_block = list(filter(
            lambda block: block.id == 'main',
            self.blocks
        ))[0]
        self.tape = [char for char in original_tape]
        self._accept(
            self.tape,
            main_block
        )

    def _accept(
            self, tape, current_block
    ):
        current_state = current_block.initial_state

        while current_state != 'pare' and current_state != 'retorne':
            self.steps -= 1
            if self.steps < 0:
                self._open_terminal()

            # verbose
            self._check_verbose(current_block, current_state, tape)

            symbol_read = tape[self.index]
            commands_from_state = list(
                filter(
                    lambda watched_command: watched_command.current_state == current_state,
                    current_block.commands
                )
            )

            current_command = commands_from_state[0]

            if len(commands_from_state) == 1 and current_command.is_another_block_call:

                if current_command.is_breakpoint:
                    self._open_terminal()

                self._accept(
                    tape,
                    list(filter(
                        lambda block: block.id == current_command.block_id,
                        self.blocks
                    ))[0]
                )
                current_state = current_command.return_state

            else:

                star_commands = list(
                    filter(
                        lambda watched_command:
                        watched_command.current_symbol == '*',
                        commands_from_state
                    )
                )

                non_star_commands = list(
                    filter(
                        lambda watched_command:
                        watched_command.current_symbol == symbol_read,
                        commands_from_state
                    )
                )
                command = None
                try:
                    command = star_commands[0] if len(non_star_commands) == 0 else non_star_commands[0]
                except:
                    print(f'An error appeared: symbol: {symbol_read}; '
                          f'state: {current_state}; block: {current_block.id}')

                if command.is_breakpoint:
                    self._open_terminal()

                tape[self.index] = command.new_symbol if command.new_symbol != '*' else tape[self.index]
                current_state = command.new_state if command.new_state != '*' else current_state

                if command.movement != 'i':
                    if self.index == 0 and command.movement == 'e':
                        tape.insert(0, parameters.blank_char)
                        self.index += 1
                    if self.index == (len(tape) - 1) and command.movement == 'd':
                        tape.append(parameters.blank_char)
                    self.index += 1 if command.movement == 'd' else -1

        self._check_verbose(current_block, current_state, tape)

    def _check_verbose(self, current_block, current_state, tape):
        if current_state != 'retorne' and parameters.run_verbose:
            self._print_verbose(current_block, current_state, tape)

    def _print_verbose(self, current_block, current_state, original_tape):
        bloco = '.' * (16 - len(current_block.id)) + current_block.id
        estado = '0' * (4 - len(current_state)) + current_state

        print(f'{bloco}.{estado}: {self._generate_right_and_left_queues(original_tape)}')

    def _generate_right_and_left_queues(self, original_tape):
        tape_with_max_blank_chars = f'{parameters.blank_char * (parameters.max_left_blank_sequence - 1)}' \
                     + ''.join(original_tape) + \
                     f'{parameters.blank_char * (parameters.max_right_blank_sequence - 1)}'
        left_index = self.index
        center_index = self.index + parameters.max_right_blank_sequence
        right_index = self.index + ((2 * parameters.max_right_blank_sequence) - 1)

        result_str = ''
        current_index = left_index
        while current_index < right_index:
            if current_index + 1 == center_index:
                result_str = f'{result_str}{parameters.head_start}{tape_with_max_blank_chars[current_index]}' \
                             f'{parameters.head_end}'
            else:
                result_str = f'{result_str}{tape_with_max_blank_chars[current_index]}'
            current_index += 1

        return result_str

    def _open_terminal(self):
        new_instructions = input('Novas intruções (enter para repetir as anteriores): ').split(' ')
        if new_instructions[0] == '':
            new_instructions = parameters.last_new_instructions
        else:
            parameters.last_new_instructions = new_instructions
        parameter_util.handle_args(new_instructions)
        self.steps = parameters.steps * 1

