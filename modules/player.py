import math
import random
import secrets
from core import conf
from datetime import datetime
from uuid import UUID
from sqlmodel import select
from modules import database


LEVEL_NAMES = [
    ['', 0, 1.00, False], ['凡人', 932, 0.20, True],
    ['炼气境一层', 932   , 0.20, True], ['炼气境二层', 932   , 0.20, False], ['炼气境三层', 932   , 0.20, False], ['炼气境四层', 932   , 0.20, False], ['炼气境五层', 932   , 0.20, False], ['炼气境六层', 932   , 0.15, False], ['炼气境七层', 932   , 0.15, False], ['炼气境八层', 932   , 0.15, False], ['炼气境九层', 932   , 0.15, False], ['炼气境十层', 932   , 0.15, False], ['炼气境十一层', 932   , 0.10, False], ['炼气境十二层', 932   , 0.10, False],
    ['筑基境初期·一重境', 1864  , 0.10, True], ['筑基境初期·二重境', 1864  , 0.10, False], ['筑基境初期·三重境', 1864  , 0.10, False], ['筑基境中期·一重境', 1864  , 0.08, False], ['筑基境中期·二重境', 1864  , 0.10, False], ['筑基境中期·三重境', 1864  , 0.10, False], ['筑基境后期·一重境', 1864  , 0.08, False], ['筑基境后期·二重境', 1864  , 0.10, False], ['筑基境后期·三重境', 1864  , 0.10, False], ['筑基境大圆满·一重境', 1864  , 0.08, False], ['筑基境大圆满·二重境', 1864  , 0.08, False], ['筑基境大圆满·三重境', 1864  , 0.08, False],
    ['结丹境初期·一重境', 3728  , 0.05, True], ['结丹境初期·二重境', 3728  , 0.10, False], ['结丹境初期·三重境', 3728  , 0.10, False], ['结丹境中期·一重境', 3728  , 0.08, False], ['结丹境中期·二重境', 3728  , 0.10, False], ['结丹境中期·三重境', 3728  , 0.10, False], ['结丹境后期·一重境', 3728  , 0.08, False], ['结丹境后期·二重境', 3728  , 0.10, False], ['结丹境后期·三重境', 3728  , 0.10, False], ['结丹境大圆满·一重境', 3728  , 0.08, False], ['结丹境大圆满·二重境', 3728  , 0.08, False], ['结丹境大圆满·三重境', 3728  , 0.08, False],
    ['元婴境初期·一重境', 7456  , 0.05, True], ['元婴境初期·二重境', 7456  , 0.10, False], ['元婴境初期·三重境', 7456  , 0.10, False], ['元婴境中期·一重境', 7456  , 0.08, False], ['元婴境中期·二重境', 7456  , 0.10, False], ['元婴境中期·三重境', 7456  , 0.10, False], ['元婴境后期·一重境', 7456  , 0.08, False], ['元婴境后期·二重境', 7456  , 0.10, False], ['元婴境后期·三重境', 7456  , 0.10, False], ['元婴境大圆满·一重境', 7456  , 0.08, False], ['元婴境大圆满·二重境', 7456  , 0.08, False], ['元婴境大圆满·三重境', 7456  , 0.08, False],
    ['化神境初期·一重境', 14912 , 0.05, True], ['化神境初期·二重境', 14912 , 0.10, False], ['化神境初期·三重境', 14912 , 0.10, False], ['化神境中期·一重境', 14912 , 0.08, False], ['化神境中期·二重境', 14912 , 0.10, False], ['化神境中期·三重境', 14912 , 0.10, False], ['化神境后期·一重境', 14912 , 0.08, False], ['化神境后期·二重境', 14912 , 0.10, False], ['化神境后期·三重境', 14912 , 0.10, False], ['化神境大圆满·一重境', 14912 , 0.08, False], ['化神境大圆满·二重境', 14912 , 0.08, False], ['化神境大圆满·三重境', 14912 , 0.08, False],
    ['炼虚境初期·一重境', 29824 , 0.05, True], ['炼虚境初期·二重境', 29824 , 0.10, False], ['炼虚境初期·三重境', 29824 , 0.10, False], ['炼虚境中期·一重境', 29824 , 0.08, False], ['炼虚境中期·二重境', 29824 , 0.10, False], ['炼虚境中期·三重境', 29824 , 0.10, False], ['炼虚境后期·一重境', 29824 , 0.08, False], ['炼虚境后期·二重境', 29824 , 0.10, False], ['炼虚境后期·三重境', 29824 , 0.10, False], ['炼虚境大圆满·一重境', 29824 , 0.08, False], ['炼虚境大圆满·二重境', 29824 , 0.08, False], ['炼虚境大圆满·三重境', 29824 , 0.08, False],
    ['合体境初期·一重境', 59648 , 0.05, True], ['合体境初期·二重境', 59648 , 0.10, False], ['合体境初期·三重境', 59648 , 0.10, False], ['合体境中期·一重境', 59648 , 0.08, False], ['合体境中期·二重境', 59648 , 0.10, False], ['合体境中期·三重境', 59648 , 0.10, False], ['合体境后期·一重境', 59648 , 0.08, False], ['合体境后期·二重境', 59648 , 0.10, False], ['合体境后期·三重境', 59648 , 0.10, False], ['合体境大圆满·一重境', 59648 , 0.08, False], ['合体境大圆满·二重境', 59648 , 0.08, False], ['合体境大圆满·三重境', 59648 , 0.08, False],
    ['大乘境初期·一重境', 119296, 0.05, True], ['大乘境初期·二重境', 119296, 0.10, False], ['大乘境初期·三重境', 119296, 0.10, False], ['大乘境中期·一重境', 119296, 0.08, False], ['大乘境中期·二重境', 119296, 0.10, False], ['大乘境中期·三重境', 119296, 0.10, False], ['大乘境后期·一重境', 119296, 0.08, False], ['大乘境后期·二重境', 119296, 0.10, False], ['大乘境后期·三重境', 119296, 0.10, False], ['大乘境大圆满·一重境', 119296, 0.08, False], ['大乘境大圆满·二重境', 119296, 0.08, False], ['大乘境大圆满·三重境', 119296, 0.08, False],
    ['真仙境初期·一重境', 238592, 0.05, True], ['真仙境初期·二重境', 238592, 0.10, False], ['真仙境初期·三重境', 238592, 0.10, False], ['真仙境中期·一重境', 238592, 0.08, False], ['真仙境中期·二重境', 238592, 0.10, False], ['真仙境中期·三重境', 238592, 0.10, False], ['真仙境后期·一重境', 238592, 0.08, False], ['真仙境后期·二重境', 238592, 0.10, False], ['真仙境后期·三重境', 238592, 0.10, False], ['真仙境大圆满·一重境', 238592, 0.08, False], ['真仙境大圆满·二重境', 238592, 0.08, False], ['真仙境大圆满·三重境', 238592, 0.08, False],
    ['金仙境初期·一重境', 477184, 0.05, True], ['金仙境初期·二重境', 477184, 0.10, False], ['金仙境初期·三重境', 477184, 0.10, False], ['金仙境中期·一重境', 477184, 0.08, False], ['金仙境中期·二重境', 477184, 0.10, False], ['金仙境中期·三重境', 477184, 0.10, False], ['金仙境后期·一重境', 477184, 0.08, False], ['金仙境后期·二重境', 477184, 0.10, False], ['金仙境后期·三重境', 477184, 0.10, False], ['金仙境大圆满·一重境', 477184, 0.08, False], ['金仙境大圆满·二重境', 477184, 0.08, False], ['金仙境大圆满·三重境', 477184, 0.08, False],
]

for ii, info in enumerate(LEVEL_NAMES):
    LEVEL_NAMES[ii][1] /= conf.SPEED_UP_RATIO


def random_int(v_min: int, v_max: int) -> int:
    if v_min == v_max:
        return v_min
    return secrets.choice(range(v_min, v_max))


def is_lucky(v_luck: int) -> bool:
    if v_luck < 1 or v_luck > 300:
        # This is a fake value.
        return False
    # Generate a random value from 0 to 254.
    guess = random_int(0, 254)

    # If the guess is in the luck range, then success.
    return guess < v_luck


def random_with_luck(v_min: int, v_max: int, v_luck: int) -> int:
    # If you are the most lucky people, give the max.
    if v_luck >= 255.0:
        return v_max
    # The most bad luck will always get the lowest value.
    if v_luck <= 0.0:
        return v_min

    # Reset the seed.
    random.seed(datetime.now().timestamp())
    # Guess the base.
    v_range = v_max - v_min
    v_center = v_min + v_range / 2
    v_patch = 1.0 + (v_luck - 127.0) / 255.0
    v_raw = math.ceil(random.gauss(v_center * v_patch, v_range / 6))

    # Make sure the raw is in the range.
    return max(v_min, min(v_raw, v_max))


class Player:
    def __init__(self):
        self.uuid: UUID | None = None
        self.hp: float = 0
        self.lv: int = 0
        self.exp: float = 0
        self.attack: float = 0
        self.defense: float = 0
        self.evasion: float = 0
        self.speed: float = 0
        self.luck: float = 0
        self.last_mod: datetime = datetime.min

    def random_with_luck(self, v_min: int, v_max: int) -> int:
        return random_with_luck(v_min, v_max, int(self.luck))

    def level_info(self):
        return LEVEL_NAMES[self.lv] if self.lv < len(LEVEL_NAMES) else LEVEL_NAMES[-1]

    def level_text(self) -> str:
        return self.level_info()[0]

    def save(self, session: database.SessionDep):
        if self.uuid is None:
            raise RuntimeError('Player UUID is unset.')

        player: database.Player | None = session.get(database.Player, self.uuid)
        if player is None:
            player = database.Player(uid=self.uuid)
        # Update the player information.
        player.v_hp = self.hp
        player.v_lv = self.lv
        player.v_exp = self.exp
        player.v_atk = self.attack
        player.v_def = self.defense
        player.v_eva = self.evasion
        player.v_spd = self.speed
        player.v_luk = self.luck
        # Update the player update time.
        player.date_modified = datetime.now()
        # Save the player information.
        session.add(player)
        session.commit()
        session.refresh(player)
        # Update the last mod time.
        self.last_mod = player.date_modified


def set_init_values(player: Player):
    # Init the fixed values.
    player.lv = 1
    player.exp = 0
    # Determine the luck.
    player.luck = random_int(1, 255)
    # Random generate value.
    player.hp = player.random_with_luck(100, 255)
    player.attack = player.random_with_luck(100, 255)
    player.defense = player.random_with_luck(100, 255)
    player.evasion = player.random_with_luck(100, 255)
    player.speed = player.random_with_luck(100, 255)


def create_ai() -> Player:
    player = Player()
    # Init the player values.
    set_init_values(player)
    return player


def create_player(uuid: UUID, session: database.SessionDep) -> Player:
    player = Player()
    # Set the player uid.
    player.uuid = uuid
    # Init the player values.
    set_init_values(player)
    # Save the player.
    player.save(session)
    return player


def get_player(uid: UUID, session: database.SessionDep) -> Player:
    # Load the player from database.
    db_player = session.exec(select(database.Player).where(database.Player.uid == uid)).first()
    # Check whether we have the player.
    if db_player is None:
        return create_player(uid, session)
    # Construct the player from the database object.
    player = Player()
    # Set the user data to the player.
    player.uuid = uid
    player.last_mod = db_player.date_modified
    # Copy the player database info.
    player.hp = db_player.v_hp
    player.lv = db_player.v_lv
    player.exp = db_player.v_exp
    player.attack = db_player.v_atk
    player.defense = db_player.v_def
    player.evasion = db_player.v_eva
    player.speed = db_player.v_spd
    player.luck = db_player.v_luk

    return player


ATTR_CAN_INC = ['hp', 'attack', 'defense', 'evasion', 'speed']


def add_exp(player: Player, session: database.SessionDep):
    # Increase the experience.
    player.exp += player.random_with_luck(1, 2)
    # Decide the increase attribute.
    val_inc = player.random_with_luck(1, 2) if player.lv < 2 else player.random_with_luck(2, 4)
    # Choose one attribute to add.
    attr_name = secrets.choice(ATTR_CAN_INC)
    setattr(player, attr_name, getattr(player, attr_name) + val_inc)

    # Save the player information.
    player.save(session)


def level_up(player: Player, session: database.SessionDep):
    # Check should up to next level.
    current_lv_info = player.level_info()

    def apply_success():
        # Clear the exp, increase the level.
        player.exp = 0
        player.lv += 1
        # Adding values to all attribute.
        player.hp += player.random_with_luck(1, int(player.hp / 4))
        player.attack += player.random_with_luck(1, int(player.attack / 4))
        player.defense += player.random_with_luck(1, int(player.defense / 4))
        player.evasion += player.random_with_luck(1, int(player.evasion / 4))
        player.speed += player.random_with_luck(1, int(player.speed / 4))
        # Change the player luck to a new level.
        player.luck = int(player.random_with_luck(0, 255))
        player.save(session)

    def apply_fail():
        # Count the time of failed.
        failed_times = session.exec(select(database.FailedCounter).where(database.FailedCounter.uid == player.uuid)).first()
        if failed_times is None:
            # First time to fail.
            failed_times = database.FailedCounter(uid=player.uuid, fails=1)
            session.add(failed_times)
            session.commit()
            session.refresh(failed_times)
        else:
            # Check the times.
            if failed_times.fails >= 11:
                # Go back to level 1.
                player.lv = 1
                failed_times.fails += 1
                session.add(failed_times)
                session.commit()
                session.refresh(failed_times)
            elif failed_times.fails >= 5:
                # Failed 6 times, cut the level back to the first sub level.
                past_level = min(player.lv, len(LEVEL_NAMES))
                while not LEVEL_NAMES[past_level][3]:
                    past_level -= 1
                player.lv = past_level

        # Failed, cut the exp to 3/4.
        player.exp = int(player.exp * 0.75)
        # Remove amount of attributes.
        def lost_value(raw_value: float) -> float:
            max_value = raw_value * conf.LEVEL_UP_FAILED_RATIO
            return int(max_value - player.random_with_luck(0, int(max_value)))

        player.hp = int(player.hp - lost_value(player.hp))
        player.attack = int(player.attack - lost_value(player.attack))
        player.defense = int(player.defense - lost_value(player.defense))
        player.evasion = int(player.evasion - lost_value(player.evasion))
        player.speed = int(player.speed - lost_value(player.speed))
        player.save(session)

    # If the exp is less than expected, must fail.
    if player.exp <= current_lv_info[1]:
        apply_fail()
        return

    # Calculate the pass score.
    # Base score.
    success_score = 100 - current_lv_info[2] * 100
    # Calculate how many exp are overflow.
    overflow_exp = player.exp - current_lv_info[1]
    # Calculate the exp score, when overflow 2.5 times, it must be success.
    exp_score = overflow_exp / (current_lv_info[1] * conf.EXP_OVERFLOW_RATIO) * 100
    success_score = max(0.5, success_score - exp_score)

    # Roll a number, check whether he can level up.
    if player.random_with_luck(0, 100) > success_score:
        apply_success()
    else:
        apply_fail()
