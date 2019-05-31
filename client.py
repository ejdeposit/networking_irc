#client
import asyncio
import sys
import ast
import sounds

room_len = int()
chat_room_dict = {}
#helper print function
def pf(thing):
    thingStr = str(thing)
    print(thingStr, f' = {thing}, type = {type(thing)}')

codes = ['m!', 'l!', 'q!', 'j', 'c']

def join_general(chatRooms, myport, username):
    
    if len(chatRooms) == 0:
        chatRooms['General'] = {}  
    chatRooms['General'][myport] = username
    print('You are now in the \'General\' chat room. \nMenu: (m!)')
        
    return chatRooms

def new_msgObj(msg, username):
    msgObj={}
    msgObj['contents']= username+': '+msg
    return msgObj

def make_createGram(line):

    createGram = {}
    room_name = line[3:] 
    room_name = room_name.strip()
    if len(room_name) > 25: 
        print('Sorry, that room name is too long.')
        return 0
    else: 
        createGram['create'] = room_name
    return str(createGram)

def make_joinGram(line):

    global chat_room_dict
    if len(chat_room_dict) == 0: 
        print('If you want to join a room, please type \'j\' first')
        return 0
    joinGram = {} 
    room_num = line[3:]
    valid_room = False
    for i in room_num: 
        x = (ord(i)-48) 
        if x <= 9 and x >= 0:
            valid_room = True    
        else:
            print('break')
            valid_room = False
            break
    if not valid_room:
        print('Invalid room number')
    else:
        room_num = int(room_num)
        if room_num <= room_len-1:
            print(f'Joining {chat_room_dict[room_num]}!')
            joinGram['join'] = chat_room_dict[room_num]
        else:
            print('The room you entered is out of range!')
            return 0
    chat_room_dict = {}
    return str(joinGram)

async def send_to_server(reader, writer, username, loop):

    while True:
        line= await loop.run_in_executor(None, sys.stdin.readline)
        print()
        if line:
            line=line[:-1:]
            if line.lower() in codes:
                if line == codes[2]:
                    print('\n\nQuitting Chat Box! Seeya next time. :)\n\n')
                    sounds.logout()
                    #this code doesn't work: it's more of an idea of how it could work?
                    writer.write(line.encode())
                    await writer.drain()
                    writer.close()
                    exit(0)
                writer.write(line.encode())
            elif line[0:2] == 'j!':
    
                joinGramStr = make_joinGram(line)
                line = None 
                if joinGramStr != 0:
                    sounds.join()
                    writer.write(joinGramStr.encode())
            elif line[0:2] == 'c!':
                createGramStr = make_createGram(line)
                line = None
                if createGramStr != 0:
                    sounds.join()
                    writer.write(createGramStr.encode())
            else:
                #make msgObj
                msgObj=new_msgObj(line, username)
                msgStr=str(msgObj)
                writer.write(msgStr.encode())
            await writer.drain()
            line=None

def room_options(myport, username, chatRooms):
    
    print('These are the current active rooms and users:\n')
    for room in chatRooms.keys():
        print(f'Chatting in \'{room}\':')
        if len(chatRooms[room]) == 0: 
            print('Nobody is currently in this room.')
        for port, user in chatRooms[room].items():
            print(user)
        print() 
    print('Join a room from above?                         (j)')
    print('Create a new room:                              (c)')
    print('Leave a room:                                   (l!)')
    print()

async def listen_to_server(reader, writer, myport, username):
    global room_len
    global chat_room_dict
    while True:
        data = await reader.read(1000)
        
        test = data.decode()
        test = str(test)
        if '{' in test:
            test = ast.literal_eval(test)       
        if isinstance(test, dict):
            #print(f'dict from server = {data.decode()}')
            data = ast.literal_eval(data.decode())
            #check if chatRoom object
            if 'echo rooms' in data.keys():   
                chatRooms = data['echo rooms'] 
                chatRooms = room_options(myport, username, chatRooms) 
            elif 'room choose' in data.keys():
                room_choose = data['room choose']
                room_len = room_choose['length']
                print(room_choose['prompt'])
                for i, room in enumerate(room_choose['rooms'].keys()):
                    chat_room_dict[i] = room
                    print(f'Join {room}: {i}')
                    #print(chat_room_dict)
                print() 
            elif 'create room' in data.keys():
                print(data['create room']['prompt'])
            elif 'leave' in data.keys():
                print(data['leave'])
            data = None
        if data:
            print(data.decode())
            print()
            await asyncio.sleep(0)


async def main(loop):
    #opens connection to server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888, loop=loop)
    
    print("\nWelcome to the chat box! What's your name, stranger?: ", end = '')
    username = input('')
    print(f'Hello, {username}, happy chatting!\n')
    print('By the way, you\'re in the \'General\' chat room.')
    
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
sounds.login()
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()

#loop.run_until_complete(tcp_echo_client(loop))
#try:
    #loop.run_forever()
#except KeyboardInterrupt:
#    pass
#loop.close()
