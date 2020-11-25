"""Constants for clovek_ne_jezi_se game setup"""


EMPTY_SYMBOL = '-'

MINIMUM_SECTION_LENGTH = 4

# TODO: Deprecate me, as this should not be a package-wide constant
PIECES_PER_PLAYER = 4


# TODO: Deprecate me, as this should not be a package-wide constant
NR_OF_DICE_FACES = 6

MOVE_KINDS = (
    'leave_waiting', 'space_advance', 'space_to_home',
    'home_advance', 'return_to_waiting'
)
