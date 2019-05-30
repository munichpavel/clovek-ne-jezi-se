from random import randint

class BaseAgent:

    def roll(self):
        res = self._get_roll_value
        if self._roll_is_valid(res):
            return res
        else:
            raise ValueError('Roll value must be between 1 and 6')
        
    def _get_roll_value(self):
        return randint(1,6)

    def _roll_is_valid(self, roll_value):
        return 1 <= roll_value <= 6
    