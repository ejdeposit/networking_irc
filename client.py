#client
import asyncio
import sys
import ast
import sounds

sound = 1
#turn sound off by setting to 0
room_len = int()
myrooms = []
chat_room_dict = {}
codes = ['u!', 's!', 't!', 'l!', 'q!', 'b!', 'j', 'c', 's', 'b']
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

def make_broadcastGram(line):
    global myrooms
    if len(myrooms) == 1: 
        print('Please type(b) to enter the broadcast menu. Remember, you must join (j) a room first!')
        return 0
    else:
        broadcastGram = {}
        broadcastGram['broadcast rooms'] = []
        rooms = []
        room_num = line[2:]
        for i, char  in enumerate(room_num): 
            if char == '!':
                end = i
                break
        b_rooms = '['+room_num[:end]+']'
        msg = room_num[end+1:].lstrip()
        is_list = True
        try:
            b_rooms = ast.literal_eval(b_rooms)
        except: 
            is_list = False
        if is_list and type(b_rooms) == list:
            #print(b_rooms)
            valid_rooms = False
            for room_num in b_rooms: 
                x = str(room_num)
                for i in x:
                    x = (ord(i)-48) 
                    if x <= 9 and x >= 0:
                        valid_room = True    
                    else:
                        valid_room = False
                        break
                if not valid_room:
                    print('Invalid room number in list!')
                    return 0
                else:
                    room_num = int(room_num)
                    if room_num <= len(myrooms)-1:
                        broadcastGram['message'] = msg
                        broadcastGram['broadcast rooms'].append(myrooms[room_num])
                        print(f'Sending {msg} to {myrooms[room_num]}!')
                    else:
                        print('Room number is out of range or you didn\'t type \'b\' before selecting!')
                        return 0
        else: 
            print('Something went wrong, did you separate your numbers with commas?\n')
            return 0

    return str(broadcastGram)

async def send_to_server(reader, writer, username, loop):
    global sound
    connStatus= True
    while (not writer.is_closing()) and connStatus:
        line= await loop.run_in_executor(None, sys.stdin.readline)
        print()
        #exit command
        line=line[:-1:]
        if line == 'exit()':
            connStatus= False
        if line and line != 'exit()':
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
                    connStatus = False
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
                line = None
                if switchGramStr != 0:
                    if sound:
                        sounds.switch()
                    writer.write(switchGramStr.encode())
            elif line[0:2] == 'b!': 
                broadcastGramStr = make_broadcastGram(line)
                line = None
                if broadcastGramStr != 0: 
                    if sound: 
                        sounds.login()
                    writer.write(broadcastGramStr.encode())
            elif line:
                #make msgObj
                msgObj=new_msgObj(line, username)
                msgStr=str(msgObj)
                writer.write(msgStr.encode())
            await writer.drain()
            line=None
    writer.close()
    await shut_down()
    
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
    
    while not reader.at_eof(): 
        
        data = await reader.read(1000)
        test = data.decode()

        #if test is 'exit()':
        if test == 'exit()':
            writer.close()
            print('received exit code')
            await shut_down()
            
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
                elif gramtype == 'broadcast':
                    myrooms = data['joined rooms']
                    room_len = data['length']
                    print(data['prompt'])
                    for i, room in enumerate(myrooms):
                        print(f'Send to {room}: {i}')                        
            data = None
        if data:
            print(data.decode())
            if sound:
                sounds.message()
            print()
            await asyncio.sleep(0)
    await shut_down()

async def main():
    global sound
    #sound = 1
    if sound:
        sounds.login()
    #opens connection to server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    
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

async def shut_down():
    taskList= asyncio.all_tasks(asyncio.get_running_loop())
    for task in taskList:
        task.cancel()


#try:
#    asyncio.run(main())
#except:
#    print('connection gracefully lost')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
