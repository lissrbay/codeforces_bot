# -*- coding: utf-8 -*-
token = '461438069:AAG9IElm7TwFhLmheTpPmwYKn2xOqPWrLBw'
from enum import Enum

class States(Enum):
    S_START = 0
    S_LOGIN = 1
    S_GET_TASK = 2
    S_THEORY = 3
    S_THEORY_ADDING = 4


