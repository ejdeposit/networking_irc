#client
import asyncio
import sys
import ast
import sounds

#sound = 1
#turn sound off by setting to 0
room_len = int()
myrooms = []
chat_room_dict = {}
codes = ['u!', 's!', 't!', 'l!', 'q!', 'j', 'c', 's']
#helper print function
def pf(thing):
    thingStr = str(thing)
    print(thingStr, f' = {thing}, type = {type(thing)}')

def pfo(string, thing):
    print(string, f' = {thing}, type = {type(thing)}, len = {len(thing)}')

def print_room_options():
    
    print('Join a room?                                    (j)')
    print('Create a new room:                              (c)')
    print('Switch rooms:                                   (s)')
    print('List all active users:                          (u!)')
    print('Send a message to other rooms:                  (b!)')
    print('Leave current room:                             (l!)')
    print('Turn off/on sound:                              (t!)')
    print('Quit the Chat Box:                              (q!)')
    print()

def print_switch_options(current_room):
    global myrooms
    for i, room in enumerate(myrooms):
        if room != current_room:
            print(room, f' ({i})')

def new_msgObj(msg, username):
    msgObj={}
    msgObj['contents']= username+': '+msg
    return msgObj

def make_createGram(line):

    createGram = {}
    room_name = line[2:] 
    room_name = room_name.strip()
    if room_name == '':
        print('Sorry, rooms cannot be named blank spaces.')
        return 0
    if len(room_name) > 25: 
        print('Sorry, that room name is too long.')
        return 0
    else: 
        createGram['create'] = room_name
    return str(createGram)

def make_joinGram(line):

    global myrooms
    global chat_room_dict
    if len(chat_room_dict) == 0: 
        print('If you want to join a room, please type \'j\' to enter the join room menu first')
        return 0
    joinGram = {}
    room_num = line[2:]
    room_num = room_num.strip()
    valid_room = False
    for i in room_num: 
        x = (ord(i)-48) 
        if x <= 9 and x >= 0:
            valid_room = True    
        else:
            valid_room = False
            break
    if not valid_room:
        print('Invalid room number')
        return 0
    else:
        room_num = int(room_num)
        
        if room_num <= room_len-1:
            if chat_room_dict[room_num] in myrooms:
                print(f'You are already a member of \'{chat_room_dict[room_num]}\'! To switch, type (s)')
                return 0
            else:
                print(f'You have joined {chat_room_dict[room_num]}! To switch to this room, type (s)')
                joinGram['join'] = chat_room_dict[room_num]
        else:
            print('The room you entered is out of range!')
            return 0
    chat_room_dict = {}
    return str(joinGram)
    
def make_switchGram(line):
    global myrooms
    if len(myrooms) == 1: 
        print('Please type (s) to enter the room switch menu. Remember, you must join (j) a room first!')
        return 0
    else: 
        switchGram = {}
        room_num = line[2:]
        room_num = room_num.strip()
        valid_room = False
        for i in room_num: 
            x = (ord(i)-48) 
            if x <= 9 and x >= 0:
                valid_room = True    
            else:
                valid_room = False
                break
        if not valid_room:
            print('Invalid room number')
            return 0
        else:
            room_num = int(room_num)
      
            if room_num <= len(myrooms)-1:
                switchGram['switch'] = myrooms[room_num]
                print(f'Switching to {myrooms[room_num]}!')
                print(f'--------------------{myrooms[room_num]}----------------------')
                return str(switchGram)
            else:
                print('Room number is out of range or you didn\'t type \'s\' before switching!')
                return 0 

async def send_to_server(reader, writer, username, loop):
    global sound
    while True:
        line= await loop.run_in_executor(None, sys.stdin.readline)
        print()
        if line:
            line=line[:-1:]
            if line.strip() == '':
                line = None
            elif line == 'm!':
                print_room_options()
            elif line.lower() in codes:
                if line == codes[2]: 
                    if sound:
                        sound = 0
                    else: 
                        sound = 1
                    line = None
                if line == codes[3]:
                    if len(myrooms) > 1:
                        if sound:
                            sounds.leave()
                        print('----------------------General----------------------')
                if line == codes[4]:
                    print('\n\nQuitting Chat Box! Seeya next time. :)\n\n')
                    if sound:
                        sounds.logout()
                    #this code doesn't work: it's more of an idea of how it could work?
                    writer.write(line.encode())
                    await writer.drain()
                    writer.close()
                    exit(0)
                if line:    
                    writer.write(line.encode())
            elif line[0:2] == 'j!':
                joinGramStr = make_joinGram(line)
                line = None 
                if joinGramStr != 0:
                    if sound:
                        sounds.join()
                    writer.write(joinGramStr.encode())
            elif line[0:2] == 'c!':
                createGramStr = make_createGram(line)
                line = None
                if createGramStr != 0:
                    if sound:
                        sounds.create()
                    writer.write(createGramStr.encode())
            elif line[0:2] == 's!':
                switchGramStr = make_switchGram(line)
                if switchGramStr != 0:
                    if sound:
                        sounds.switch()
                    writer.write(switchGramStr.encode())
            elif line:
                #make msgObj
                msgObj=new_msgObj(line, username)
                msgStr=str(msgObj)
                writer.write(msgStr.encode())
            await writer.drain()
            line=None

def show_active_users(myport, chatRooms, clientTracker, room_to_display):

    if room_to_display == 'all':
        print('These are the current active rooms and users:\n')
        for room in chatRooms.keys():
            print(f'Chatting in \'{room}\':')
            if len(chatRooms[room]) == 0: 
                print('Nobody is currently in this room.')
            for port, user in chatRooms[room].items():
                if clientTracker[port]['current'] == room:
                    print(user)
            print() 
    else: 
        print(f'Active users in \'{room_to_display}\':')
        if len(chatRooms[room_to_display]) == 1:
            print('You are the only person currently chatting in this room.') 
        else:
            for port, user in chatRooms[room_to_display].items():
                if clientTracker[port]['current'] == room_to_display and port != myport:
                    print(user)        
        print('\nMenu: (m!)') 

async def listen_to_server(reader, writer, myport, username):
    global room_len
    global chat_room_dict
    global myrooms
    
    while True:
        
        data = await reader.read(1000)
        
        test = data.decode()
        test = str(test)
        if '{' in test:
            for i, char in enumerate(test):
                if char == '{':
                    index = i
                    break
            test = test[i:]
            extra = test[:i]
            print(extra)
            test = ast.literal_eval(test)       
        if isinstance(test, dict):
            #print(f'dict from server = {data.decode()}')
            data = ast.literal_eval(data.decode())
            #check if chatRoom object
            if 'gram type' in data.keys():
                gramtype = data['gram type']
                if gramtype == 'echo rooms':   
                    chatRooms = data['rooms'] 
                    clientTracker = data['tracker']
                    show_active_users(myport, chatRooms, clientTracker, 'all') 
                elif gramtype == 'room choose': 
                    myrooms = data['joined rooms']
                    room_len = data['length']
                    print(data['prompt'])
                    for i, room in enumerate(data['rooms'].keys()):
                        chat_room_dict[i] = room
                        print(f'Join {room}: ({i})')
                    print() 
                elif gramtype == 'switch room':
                    myrooms = data['joined rooms']
                    current_room = data['current']
                    if len(myrooms) == 1:
                        print('You haven\'t joined any rooms yet! To join a room, type (j)')
                    else:
                        print(data['prompt'])
                        print_switch_options(current_room)
                elif gramtype == 'welcome alert':
                    chatRooms = data['rooms'] 
                    clientTracker = data['tracker']
                    room = data['welcome room']
                    print(data['prompt'])
                    show_active_users(myport, chatRooms, clientTracker, room)
            data = None
        if data:
            print(data.decode())
            if sound:
                sounds.message()
            print()
            await asyncio.sleep(0)


async def main(loop):
    global sound
    sound = 1
    if sound:
        sounds.login()
    #opens connection to server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888, loop=loop)
    
    print("\nWelcome to the chat box! What's your name, stranger?: ", end = '')
    username = input('')
    print(f'Hello, {username}, Enjoy!\n')
    if sound:
        sounds.switch()
    print('By the way, you begin in the \'General\' chat room. You can access the menu by typing (m!). \
         \nYou can join and leave rooms as you wish, but you can\'t leave \'General\' without quitting.')
    
    sock = writer.get_extra_info('socket')
    myport = sock.getsockname()
    myport = myport[1]
    writer.write(username.encode())
    await writer.drain()
    await asyncio.gather(listen_to_server(reader, writer, myport, username),
                         send_to_server(reader, writer, username, asyncio.get_running_loop()))

    #close connection
    print('Close the socket')
    writer.close()


#problem: this client sends message and then closes loop.  need to listen
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()

#loop.run_until_complete(tcp_echo_client(loop))
#try:
    #loop.run_forever()
#except KeyboardInterrupt:
#    pass
#loop.close()
