def create(chatRooms, myport, username): 
    while True:
        room_name = input('')
        if room_name.lower() == 'j':
            huh = input('Join (j) existing room or create (c) a new room called \'j\'?:')
            if huh.lower()== 'j':
              chatRooms = join(chatRooms, myport, username, 0)
              return chatRooms
              break   
        sure = input(f'\nCreate a new room called {room_name}?  (y)  or  (n): ')
        if sure.lower() == 'y':
            #print(f'chatRooms = {chatRooms}')
            if room_name not in chatRooms.keys():
                chatRooms[room_name] = {} 
                print(f'\nOk! You are currently the sole member of {room_name}. If someone joins, you\'ll get an alert.\n')
                print('To leave, list active rooms or create a new room, enter (k)')
            elif room_name in chatRooms.keys():
                print(f'\nNot so fast! {room_name} already exists! Enter another name or (j) to join a room:\n')
                continue
            else:
                print(f'Welcome to {room_name}!')
            chatRooms[room_name][myport] = username
            return chatRooms
        elif sure.lower() == 'n':
            print('\nOk, just enter the name of the room you want to create:\n')
            continue
        else:
            print('Invalid input. Please re-enter the room name:\n')
            continue
    return        

def join(chatRooms, myport, username):    
    
    while True:
        print('\nWould you like to join a room from below? (j)\n')
        for room in chatRooms.keys():
            print(f'Chatting in {room}:')
            for number, user in chatRooms[room].items():
                print(user)
            print() 
        print('Otherwise, create a new room: (c)', end='')
        sel = input('') 
        if sel.lower() == 'j':
            while True:
                room_name = input('\nEnter the name of the room you wish to join: ') 
                if str(room_name) in chatRooms.keys():
                    print(f'\nOk, you\'ve joined {room_name}!\n')
                    print('To leave, list active rooms or create a new room, enter (k)')
                    chatRooms[room_name][myport] = username
                    return chatRooms
                elif room_name.lower() == 'r':
                    break
                else:
                    print('\nOops. Try entering the name of the room again or to return (r)')
                    continue 
        elif sel.lower() == 'c': 
            print('Ok, cool. Go ahead and enter the name of the room you want to create: ') 
            create(chatRooms, myport, username)
            break
        else: 
            print('Invalid input. Please re-enter your selection.\n')
            continue

