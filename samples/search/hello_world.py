# coding=utf-8

from __future__ import print_function
import time, random
from simpleai.search import SearchProblem, astar, depth_first, breadth_first

GOAL = 'HELLO WORLD'

class HelloProblem(SearchProblem):
    def actions(self, state):
        if len(state) < len(GOAL):
            return list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['-']  # Add '-' for deletion

    def result(self, state, action):
        if action == '-':  # Handle deletion
            return state[:-1]
        return state + action

    def is_goal(self, state):
        return state == GOAL

    def heuristic(self, state):
        # how far are we from the goal?
        wrong = sum([1 if i < len(state) and state[i] != GOAL[i] else 0
                    for i in range(len(state))])
        missing = len(GOAL) - len(state)
        return wrong + missing

# Preprocess the initial state to remove the first problematic character and everything after it
def preprocess_initial_state(initial_state, goal):
    for i, char in enumerate(initial_state):
        if i >= len(goal) or char != goal[i]:
            return initial_state[:i]  # Remove the problematic character and everything after it
    return initial_state

initial_state = 'HXELLO WORLD'
preprocessed_state = preprocess_initial_state(initial_state, GOAL)

problem = HelloProblem(initial_state=preprocessed_state)
result = astar(problem)

start_time = time.time()
print(f"Start time: {start_time}")
print(f"End time: {time.time()}")
print(f"Elapsed time: {time.time() - start_time}")
print(f"Result state: {result.state}")
print(f"Result path: {result.path()}")
