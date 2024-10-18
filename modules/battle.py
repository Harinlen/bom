import secrets
import math
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlmodel import select, func
from core import conf
from modules import admin, database, template, player, user


router = APIRouter()

@router.get("/war")
async def page_holy_war(_: UUID = Depends(user.must_extract_uid)):
    return template.render('war.html')


def choose_players(my_uid: UUID, session: database.SessionDep) -> List[player.Player]:
    player_candidates = session.exec(select(database.Player)).all()
    num_of_players = len(player_candidates)
    players = []
    if num_of_players < conf.WAR_MAX_PLAYERS:
        # Need to add AIs.
        for db_player in player_candidates:
            players.append(player.get_player(db_player.uid, session))
        # Create AIs between these candidates.
        while len(players) < conf.WAR_MAX_PLAYERS:
            players.append(player.create_ai())
    else:
        # Random choose 7 servants.
        candidates = session.exec(select(database.Player).order_by(func.random())).fetchmany(conf.WAR_MAX_PLAYERS)
        my_uid_is_in = False
        for db_player in candidates:
            if db_player.uid == my_uid:
                my_uid_is_in = True
            players.append(player.get_player(db_player.uid, session))
        # Check whether my uid is in players.
        if not my_uid_is_in:
            players.pop(0)
            players.append(player.get_player(my_uid, session))
    # Double the HP.
    for p in players:
        p.hp *= 2
    return players


@router.post("/war_start")
async def holy_war(session: database.SessionDep, my_uid: UUID = Depends(user.must_extract_uid)):
    # Online calculate the war.
    # 1. Find 7 servants.
    players = choose_players(my_uid, session)
    player_max_hps = [p.hp for p in players]
    # 2. Simulate war.
    progress = []
    player_left = [[ii, players[ii]] for ii in range(conf.WAR_MAX_PLAYERS)]
    # Decide operation order.
    player_left.sort(key=lambda x: x[1].speed, reverse=True)
    # Keep battle.
    while len(player_left) > 1:
        # Each available player decide what to do.
        step_ops = []
        # Pop the first operated player.
        target = player_left.pop(0)
        # Choose the one to attack.
        to_target = secrets.choice(player_left)
        # Calculate the damage.
        src_player = target[1]
        dst_player = to_target[1]
        # Is critical?
        src_critical = player.is_lucky(int(src_player.luck))
        #dst_critical = player.is_lucky(int(dst_player.luck))
        # Calculate the damage.
        total_hit = src_player.attack * (src_player.random_with_luck(110, 150) / 100.0) if src_critical else src_player.attack
        #total_def = (dst_player.defense * (dst_player.random_with_luck(90, 120) / 100.0) if dst_critical else dst_player.defense) * 0.4
        total_def = dst_player.defense * 0.75
        # damage = math.ceil(max(0.0, (total_hit - total_def) * src_player.random_with_luck(-10, 11) / 10.0))
        damage = max(0.0, math.ceil(total_hit - total_def))
        # Can evasion?
        if damage > 0:
            if dst_player.random_with_luck(0, int(src_player.evasion + dst_player.evasion)) < dst_player.evasion:
                # Evasion success.
                damage = 0
        # Put the player back.
        player_left.append(target)
        if damage == 0:
            continue
        # Record the step ops.
        step_ops.append([target[0], to_target[0], damage])

        # Apply the damage.
        dead_player = []
        # Calculate the damage right now.
        players[to_target[0]].hp = max(0.0, players[to_target[0]].hp - damage)
        if players[to_target[0]].hp <= 0.0:
            dead_player.append(to_target[0])
            # Remove the player from left player.
            for ii, player_info in enumerate(player_left):
                if player_info[0] == to_target[0]:
                    del player_left[ii]
                    break
        # Update the player HP bar.
        hp_bar = []
        for ii, p in enumerate(players):
            hp_bar.append(p.hp / player_max_hps[ii])
        # Add the information to progress.
        progress.append({'steps': step_ops, 'death': dead_player, 'hp_bar': hp_bar})

    # Check the winner.
    winner = []
    if len(player_left) > 0:
        winner.append(player_left[0][0])
    # 3. Extract the player nicknames.
    player_info = []
    npc_counter = 1
    for p in players:
        if p.uuid is None:
            player_info.append('被抓来的路人' + str(npc_counter))
            npc_counter += 1
            continue
        user_info = session.exec(select(database.User).where(database.User.uid == p.uuid)).first()
        if user_info is None:
            raise RuntimeError('Unexpected error.')
        player_info.append(user_info.nickname if len(user_info.nickname) > 0 else user_info.username)
    # Construct the war result.
    return {
        'players': player_info,
        'progress': progress,
        'winner': winner
    }
