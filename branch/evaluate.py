import json
import logging
import random
import re

# Incoming globals: definition, response, last_transition, previous_state

# Definition Example
#      {
#        "name": cardName, 
#        "scope": "player",
#        "mode": "random",
#        "branches": [{
#           "action": "node-1",
#           "action": "node-2",
#           "action": "node-3"
#        ], 
#        "type": "branch", 
#        "id": "branch-12345"
#      }, 

logger = logging.getLogger('db')


logger.info('DEF: ' + json.dumps(definition, indent=2))
logger.info('EXTRAS: ' + str(extras))

result['details'] = {}

result['actions'] = []
result['next_id'] = None

branch_variable = 'branch-' + definition["id"] + '-visits' 

past_branches = None

if definition["scope"] == "player":
    past_branches = extras['player'].fetch_variable(branch_variable)
elif definition["scope"] == "session":
    past_branches = extras['session'].fetch_variable(branch_variable)
else: # Game
    past_branches = extras['session'].game_version.game.fetch_variable(branch_variable)
    
if past_branches is None:
    past_branches = ''
    
visits = []

next_index = 0

if past_branches:
    visits = past_branches.split(';')
   
logger.info('VISITS: ' + str(visits))
 
if definition["mode"] == "random":
    next_index = random.randint(0, len(definition["branches"]) - 1)
elif definition["mode"] == "random-no-repeat":
    options = range(0, len(definition["branches"]))

    logger.info('OPTIONS 1: ' + str(options))
    
    for visit in sorted(visits, reverse=True):
        if int(visit) < len(options):
            del options[int(visit)]

    logger.info('OPTIONS 2: ' + str(options))
        
    if len(options) == 0:
        options = range(0, len(definition["branches"]))
        visits = []

    logger.info('OPTIONS 3: ' + str(options))
    
    next_index = random.choice(options)
else: # Sequential
    if len(visits) > 0:
        next_index = len(visits) % len(definition["branches"])
    else:
        next_index = 0

visits.append(str(next_index))

next_action = definition["branches"][next_index]["action"]
    
result['details']['selected_index'] = next_index
result['details']['selected_action'] = next_action
result['details']['past_visits'] = visits
result['next_id'] = next_action

if result['next_id'] is not None and ('#' in result['next_id']) is False:
    result['next_id'] = definition['sequence_id'] + '#' + result['next_id']
    
action = {
    'type': 'set-variable',
    'variable': branch_variable,
    'value': ';'.join(visits)
}

if 'scope' in definition:
    action['scope'] = definition['scope']

result['actions'] = [action]