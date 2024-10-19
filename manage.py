from uuid import UUID
from sqlmodel import select
from modules import database

def main():
    while True:
        command = input('> ')
        if command == 'list':
            with database.Session(database.engine) as session:
                result = session.exec(select(database.User)).all()
                for user in result:
                    print('{} \t {}'.format(user.uid, user.username))
        elif command == 'admin':
            uid = input('uid? ')
            try:
                user_id = UUID(uid)
            except ValueError:
                print('Invalid user id')
                continue
            with database.Session(database.engine) as session:
                result = session.exec(select(database.User).where(database.User.uid == user_id)).first()
                if result is None:
                    print('User {} does not exist'.format(user_id))
                    continue
                session.add(database.Admin(uid=result.uid))
                session.commit()
        elif command == 'luck':
            uid = input('admin uid? ')
            try:
                user_id = UUID(uid)
            except ValueError:
                print('Invalid user id')
                continue
            luck_value = input('luck value? ')
            try:
                luck = int(luck_value)
            except ValueError:
                print('Invalid luck value')
                continue
            with database.Session(database.engine) as session:
                result = session.exec(select(database.Player).where(database.Player.uid == user_id)).first()
                if result is None:
                    print('User {} does not have a player'.format(user_id))
                    continue
                result.v_luk = luck
                session.add(result)
                session.commit()
                session.refresh(result)
        elif command == 'init_items':
            pass
        elif command == 'exit':
            break
        else:
            print('unknown command')

if __name__ == '__main__':
    main()
