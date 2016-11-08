"""
Functions for manipulation of the Score Matrix for the iterated prisoner's dilemma:
( P1 score is on the left, P2 on the right )
        P1
        C        D
P2  C [ 3, 3 ] [ 5, 0 ]
    D [ 0, 5 ] [ 1, 1 ]
"""

SCORE_CC = 3 # myChoice = c, theirChoice = d
SCORE_CD = 0 # myChoice = c, theirChoice = d
SCORE_DD = 1 # myChoice = d, theirChoice = d
SCORE_DC = 5 # myChoice = d, theirChoice = c

""" The energy loss of a cell per simulation tick """
LOSS_PER_TICK = 2

def getScore(myChoice, theirChoice):
    """
    return the corresponding scores for the 2 choices.
    Consider using a named tuple or dictionary for this method?
    :param choice1: The choice of player 1
    :param choice2: The choice of player 2
    :return: An integer value which is the score for the two choices
    """
    if 'c' == myChoice and 'c' == theirChoice:
        return SCORE_CC
    if 'c' == myChoice and 'd' == theirChoice:
        return SCORE_CD
    if 'd' == myChoice and 'c' == theirChoice:
        return SCORE_DC
    else:
        return SCORE_DD
