import asyncio
import ast
import re
import sounds
import time
import sys

sound = 1
#helper print functions
def pf(thing):
    thingStr = str(thing)
    print(thingStr, f' = {thing}, type = {type(thing)}')

def pfo(string, thing):
    print(string, f' = {thing}, type = {type(thing)}, len = {len(thing)}')

def pfct():
    pfo('CT', clientTracker)
    
#codes tell the server that client message is a command message or a special
#message 'gram'.
codes = ['u!','s!','t!','l!', 'q!', 'c', 'j', 's', 'b']
#addressList is list of all client port numbers(int)
addressList=[]

#mailbox is dictionary each client port number is key to list of their 
#undelivered messages
mailBox={}

#chatRooms is dictionary. name or number of chatroom is key to list of
#client ports in chatroom.  server will iterate through a chat room's list
#and deliver message to each mailbox of each client in list.  Clients will 
#have to maintain their own list of what rooms they are in on their side.
chatRooms={}

#clientTracker is a dictionary. because clients can join multiple rooms, 
#it is necessary to keep track of joined rooms as well as the 'current'
#room that any given client is in. 
clientTracker={}

disconnectQueue=[]

def is_connected():
    #need some way to determine if client is still connected.  if not 
    #terminate connection and cancel coroutines maybe.  probably a built 
    #in method for for checking.  Definitly build in method for canceling
    #coroutines
    pass

def delete_client(port):

    #remove client from chatRooms lists and addressList
    for room in chatRooms.keys():
        if port in chatRooms[room]:
            del chatRooms[room][port]
            print(f'{port} deleted!')
    del clientTracker[port]
    pfct()
    for i in addressList:
        if i == port:
            del addressList[i]

def delete_room(room):
    #This function was part of an earlier version that deleted rooms if everyone left.  
    if len(chatRooms[room]) == 0 and room != 'General':
        del chatRooms[room]
        print(f'{room} deleted!')

def alert_add_to_room(port, username):

    for room in chatRooms.keys():
        if clientTracker[port]['current'] == room:
            for other_port in chatRooms[room].keys():
                if port != other_port and clientTracker[other_port]['current'] == room: 
                    alert = '\n'+username+' has joined '+room+'! Say hello!'
                    mailBox[other_port][room].append(alert)
                elif port == other_port:
                    alert = {}
                    alert['gram type'] = 'welcome alert'
                    alert['prompt'] = '\nWelcome to \''+room+'\', '+username+'! Happy chatting! \n'
                    alert['rooms'] = chatRooms
                    alert['tracker'] = clientTracker
                    alert['welcome room'] = room
                    alertStr = str(alert)
                    echo(port, alertStr)

def alert_leave_room(port, room):
      
   for other_port in chatRooms[room].keys():
       if port != other_port and clientTracker[other_port]['current'] == room:
           alert = '\n'+chatRooms[room][port]+' has left the room!'
           mailBox[other_port][room].append(alert)

def leave_room(port):
   
   current_room = clientTracker[port]['current']
   if current_room == 'General':
       return 1
   else:
       current_room = clientTracker[port]['current']
       for i, room in enumerate(clientTracker[port]['joined rooms']):
           if room == current_room:
               del clientTracker[port]['joined rooms'][i]
       clientTracker[port]['current'] = 'General' 
       pfct()
       alert_leave_room(port, current_room)
       remove_from_room(port, current_room)
       #delete_room(room)
       return 0

def remove_from_room(port, room):
    #remove client from specificed chatroom list in chatroom dictionary 
    del chatRooms[room][port] 
    print(f'Removing {port} from {room}!')
    print(f'After remove {chatRooms}')
 
def add_to_room(port, username, room):
    #add client from specificed chatroom list in chatroom dictionary
    if room not in chatRooms.keys():
        chatRooms[room]={}
        msg = '\''+room+'\' created! You are automatically a member, but you\'ll need to switch (s) to start chatting.'
        echo(port, msg)
    chatRooms[room][port] = username
    if room not in clientTracker[port]['joined rooms']:
        clientTracker[port]['joined rooms'].append(room)
        mailBox[port][room] = []
        pfct()
    print(f'after add {chatRooms}')

def echo(port, msg):
   mailBox[port][clientTracker[port]['current']].append(msg)

def new_msgObj(msg):
    msgObj={}
    msgObj['contents']= msg
    return msgObj

def broadcast_msg(port, msgObj):
   
    room = clientTracker[port]['current']
    for other_port in addressList:
        #if other_port in chatRooms[room].keys():
        if room in clientTracker[other_port]['joined rooms']:
            if other_port != port: 
                msg=msgObj['contents']
                print(f'msg = {msg}')
                mailBox[other_port][room].append(msg)

def broadcast_msg_multiple_rooms(port, msgObj, rooms):
   
    for room in rooms:
        for other_port in addressList:
            #if other_port in chatRooms[room].keys():
            if room in clientTracker[other_port]['joined rooms']: 
                msg=msgObj['contents']
                print(f'msg = {msg}')
                mailBox[other_port][room].append(msg)

def check_mail(port):
    if(mailBox[port][clientTracker[port]['current']]):
        msg= mailBox[port][clientTracker[port]['current']].pop(0)
        print(f'retreiving: {msg!r}')
        return msg
    return None

async def listen_to_client(reader, addr, port, username):
    
    while True:
        data = await reader.read(100)
        msgStr = data.decode()
        pf(msgStr)
        #checking if command message
        if  msgStr.lower() in codes:
            print('command detected')
            if msgStr == codes[0]:
                echo_roomGram = {}
                echo_roomGram['gram type'] = 'echo rooms'
                echo_roomGram['rooms'] =chatRooms
                echo_roomGram['tracker'] = clientTracker
                echo_roomGramStr = str(echo_roomGram)
                echo(port, echo_roomGramStr)
            elif msgStr == codes[3]:
                general = leave_room(port)
                if general:
                    prompt = 'You\'re in the General room! Do you want to quit the chat box? (q!) \
                              \n(Do nothing to stay here.)'
                else: 
                    prompt = '\nYou\'ve returned to the General room. Say hello! \nMenu: (m!)'
                echo(port, prompt)
            elif msgStr == codes[4]:
                #delete_client_from_room(port) 
                break
            elif msgStr.lower() == 'j':
                room_chooseGram = {}
                room_chooseGram['gram type']= 'room choose'
                prompt = '\nTo join a room, type \'j!\' followed by the corresponding number of the room you wish to join:\n '
                room_chooseGram['prompt'] = prompt 
                room_chooseGram['rooms'] = chatRooms
                room_chooseGram['joined rooms'] = clientTracker[port]['joined rooms']
                room_len = len(chatRooms.keys())
                room_chooseGram['length'] = room_len
                room_chooseGramStr = str(room_chooseGram)
                echo(port, room_chooseGramStr)
            elif msgStr.lower() == 'c': 
                prompt = 'To create a room, type \'c!\' followed by the name of the room you\'d like to create.\
                          \nIf the room already exists, you will join that room.'
                echo(port, prompt)
            elif msgStr.lower() == 's':
                switchGram = {}
                switchGram['gram type'] = 'switch room'
                switchGram['joined rooms'] = clientTracker[port]['joined rooms']
                switchGram['current'] = clientTracker[port]['current']
                switchGram['prompt'] = 'To switch rooms, type \'s!\' followed by the corresponding number of the room you wish to join:\n'
                switchGramStr = str(switchGram)
                echo(port, switchGramStr)
            elif msgStr == 'b':
                broadcastGram = {}
                broadcastGram['gram type'] = 'broadcast'
                broadcastGram['joined rooms'] = clientTracker[port]['joined rooms']
                room_len = len(chatRooms.keys())
                broadcastGram['length'] = room_len 
                s0 = 'To broadcast, type \'b!\' followed by the numbers of the rooms you\'d '
                s1 = 'like to broadcast to from below (with commas), then type \'!\'. Then type your'
                s2 = 'message. For example, \'b! 1, 3, 5 ! Hello.\' (Sends to \'Hello\' to 3 selected rooms) :\n'
                broadcastGram['prompt'] = s0 + s1 + s2 
                broadcastGramStr = str(broadcastGram)
                echo(port, broadcastGramStr)
            msgStr = None
        #if message object
        if msgStr != None:
        #if msgStr != None and msgStr !='':
            print(f"Received {msgStr!r}")
            msgObj= ast.literal_eval(msgStr)
            #if isinstance(msgObj, dict): 
            if 'join' in msgObj.keys():
              room_name = msgObj['join']
              pf(room_name)
              add_to_room(port, username, room_name)
            elif 'create' in msgObj.keys():
              room_name = msgObj['create']
              pf(room_name)
              add_to_room(port, username, room_name)
            elif 'switch' in msgObj.keys():
              room = msgObj['switch']
              clientTracker[port]['current'] = msgObj['switch']
              alert_add_to_room(port, username) 
              pfct()
            elif 'broadcast rooms' in msgObj.keys():
              msg = msgObj['message']
              msg = chatRooms['General'][port]+': '+msg
              rooms = msgObj['broadcast rooms']
              msgObj = new_msgObj(msg)
              msgObj['from'] = port
              broadcast_msg_multiple_rooms(port, msgObj, rooms) 
            #adding port number to msgObj
            else:
                msgObj['from']= port
                print(f'msgObj = {msgObj!r}')
                broadcast_msg(port, msgObj)

async def send_to_client(writer, port):
    while True:
        msgOut= check_mail(port)
        if msgOut:
            writer.write(msgOut.encode())
            await writer.drain()
            msgOut=None
        await asyncio.sleep(0)

def new_client(port, username):
    if port not in addressList:
        print('adding port', port) 
        addressList.append(port)
    if port not in mailBox:
        mailBox[port]={}
        mailBox[port]['General'] = []
    if len(chatRooms) == 0:
        chatRooms['General'] = {}
    chatRooms['General'][port] = username
    print('call alert')
    alert_add_to_room(port, username)
    print(chatRooms)

async def disconnect_client(writer, port):
    global disconnectQueue

    while port not in disconnectQueue:
        
        await asyncio.sleep(0)

    exitCode='exit()'
    #delete_client(port)
    writer.write(exitCode.encode())
    writer.close()
    print('deleting client: ', port)

async def disconnect_input(port):
   global disconnectQueue
   loop= asyncio.get_running_loop()

   while True:
       line= await loop.run_in_executor(None, sys.stdin.readline)
       line=line[:-1:]

       if line:
           disconnectQueue=[]
           disconnectQueue.append(port)
       line=None

async def main(reader, writer):
    global addressList
    global chatRooms
    global clientTracker

    addr = writer.get_extra_info('peername')
    port = addr[1]
    username = await reader.read(100)
    username = username.decode()
      
    clientTracker[port] = {}
    clientTracker[port]['current'] = 'General'
    clientTracker[port]['joined rooms'] = []
    clientTracker[port]['joined rooms'].append('General')
    pfo('CT', clientTracker)
    
    new_client(port, username)
    #await asyncio.gather(listen_to_client(reader, addr, port, username), send_to_client(writer, port),
    #      disconnect_input(port), disconnect_client(writer, port))
    try:
        await asyncio.gather(listen_to_client(reader, addr, port, username), send_to_client(writer, port), 
        disconnect_input(port), disconnect_client(writer, port))
    except:
        print('Client ', port, 'has disconnected.')
        #delete_client(port)
        pass

    print("Close the client socket")
    writer.close()

#Create event loop, start server
if sound:
    sounds.login()
loop = asyncio.get_event_loop()
coro = asyncio.start_server(main, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Server started! Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
