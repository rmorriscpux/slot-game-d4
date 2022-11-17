import random
from . import slot_data

class Slot:
    def __init__(self, r1=0, r2=0, r3=0):
        self.game_result = {
            'reelstops' : [r1, r2, r3],
            'credits_played' : 0,
            'credits_won' : 0,
            'wins' : {},
            'top_award_hit' : False,
        }
        self.window = []
        self.build_window()

    def spin_reels(self):
        # Flush the previous result.
        self.game_result['reelstops'] = []

        # Get a random stop for each reel.
        for reel in slot_data.game_reels:
            self.game_result['reelstops'].append(random.randrange(0, len(reel)))

        return self

    def build_window(self):
        self.window.clear()
        # Set symbols to the spot on the window.
        for i in range(0, len(self.game_result['reelstops'])):
            reel = []
            for j in range(0, 3):
                reel.append(slot_data.game_reels[i][(self.game_result['reelstops'][i] + j) % len(slot_data.game_reels[i])])
            self.window.append(reel)
        
        return self

    def eval_lines(self, lines_played):
        # Input check.
        if lines_played > len(slot_data.lines):
            lines_played = slot_data.lines
        elif lines_played < 0:
            lines_played = 0

        # Initialize
        self.game_result['wins'] = {}
        self.game_result['credits_won'] = 0
        self.game_result['top_award'] = False

        # Evaluate line by line.
        for i in range(0, lines_played):
            line = slot_data.lines[i]
            wild_count = 0
            symbol_count = 0
            line_pay = 0
            symbols = []

            # Add the window position in each column specified by line to the symbols array.
            for j in range(0, len(self.window)):
                symbols.append(self.window[j][line[j]])

            # Do wild count. Wilds are any on a payline.
            for symbol in symbols:
                if symbol == slot_data.wild:
                    wild_count += 1

            # Do symbol count. Evaulates left-to-right.
            key_symbol = symbols[0]
            for symbol in symbols:
                # Ensure key_symbol matches first non-wild if applicable. I don't like the way I did this, but it works.
                if key_symbol == slot_data.wild and symbol != slot_data.wild:
                    key_symbol = symbol
                # Count symbols.
                if symbol == key_symbol or symbol == slot_data.wild:
                    symbol_count += 1

            # Get the line pay.
            if key_symbol in slot_data.line_pays.keys():
                line_pay = slot_data.line_pays[key_symbol][symbol_count]
                # Do wild multiplier for winning lines.
                if line_pay > 0:
                    for mult in range(0, wild_count):
                        line_pay *= 2
            # Check wild pays if the line_pay is 0. Based on the above, the key_symbol should only be wild if all symbols on the line were wild, therefore we'll only get here if 
            if line_pay == 0:
                line_pay = slot_data.line_pays[slot_data.wild][wild_count]

            # Add to line wins if pay is greater than 0.
            if line_pay > 0:
                self.game_result['wins']['Line ' + str(i + 1)] = line_pay
                self.game_result['credits_won'] += line_pay
                if line_pay == slot_data.top_award:
                    self.game_result['top_award'] = True

        return self

    def play(self, credits):
        # Quick input check.
        if not isinstance(credits, int):
            return self
        if credits <= 0 or credits > len(slot_data.lines):
            return self

        self.game_result['credits_played'] = credits
        self.spin_reels()
        self.build_window()
        self.eval_lines(credits)

        return self

    def print_window(self):
        # Get the longest window column.
        max_window_len = 0
        for reel in self.window:
            if len(reel) > max_window_len:
                max_window_len = len(reel)
        # Print the reel stop for the top row.
        row_str = "|"
        for stopval in self.game_result['reelstops']:
            row_str = row_str + str(stopval).center(10) + "|"
        print(row_str)
        # Print the reels one row at a time.
        for row in range(0, max_window_len):
            row_str = "|"
            for reel in self.window:
                if len(reel) > row:
                    row_str = row_str + reel[row][0:10].center(10) + "|"
                else:
                    row_str = row_str + "".center(10) + "|"
            print(row_str)
        
        return self


if __name__ == "__main__":
    test_game = Slot().play(5)
    test_game.print_window()
    print("Played: " + str(test_game.game_result['credits_played']))
    print("   Won: " + str(test_game.game_result['credits_won']))
    for line, win in test_game.game_result['wins'].items():
        print(line + " pays " + str(win))