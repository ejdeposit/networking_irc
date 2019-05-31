import asyncio
import ast
import re
import sounds

#helper print function
def pf(thing):
    thingStr = str(thing)
    print(thingStr, f' = {thing}, type = {type(thing)}')

#codes tell the server that client message is a command
codes = ['m!', 'l!', 'q!', 'j', 'c']
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

def delete_room(room):
      
    if len(chatRooms[room]) == 0 and room != 'General':
        del chatRooms[room]
        print(f'{room} deleted!')

def alert_add_to_room(port, username):
    global chatRooms
    global mailBox

    for room in chatRooms.keys():
        pf(room)
        if port in chatRooms[room]:
            for other_port in chatRooms[room].keys():
                if port != other_port: 
                    alert = '\n'+chatRooms[room][port]+' has joined '+room+'! Say hello!\n'
                    mailBox[other_port].append(alert)
                elif port == other_port:
                    alert = '\nWelcome to '+room+' '+username+'! Happy chatting! \nMenu: (m!)'
                    mailBox[port].append(alert)

def alert_leave_room(port, room):
   global chatRooms
   global mailBox
      
   for other_port in chatRooms[room].keys():
       if port != other_port:
           alert = '\n'+chatRooms[room][port]+' has left the room!'
           mailBox[other_port].append(alert)

def leave_room(port, username):
   global chatRooms
   global mailBox

   for room in chatRooms.keys():
       if port in chatRooms[room].keys():
          if room == 'General':
              return 1
          else: 
              alert_leave_room(port, room)
              chatRooms['General'][port] = username 
              remove_from_room(port, room)
              delete_room(room)
              return 0

def remove_from_room(port, room):
    #remove client from specificed chatroom list in chatroom dictionary
    global chatRooms
    
    del chatRooms[room][port]
    print(f'Removing {port} from {room}!')
    print(f'After remove {chatRooms}')
 
def add_to_room(port, username, room):
    #add client from specificed chatroom list in chatroom dictionary
    global chatRooms

    f_room = {}
    for former_room in chatRooms.keys():
        if port in chatRooms[former_room]:
            f_room = former_room
            alert_leave_room(port, former_room)
            remove_from_room(port, former_room)
    if room not in chatRooms.keys():
        chatRooms[room]={}
        chatRooms[room][port] = username
    elif port not in chatRooms[room].keys():
        chatRooms[room][port] = username
    delete_room(f_room)
    alert_add_to_room(port, username)
    print(f'after add {chatRooms}')

def echo_chatRooms(port, echo_roomGram):
    #send back the chatRooms to clients when they ask for a room change
    global chatRooms
    global mailBox

    for room in chatRooms.keys():
         for key in chatRooms[room].keys():
             if port == key:
                 mailBox[key].append(echo_roomGram)                

def echo(port, msg):
   global mailbox
   mailBox[port].append(msg)

def new_msgObj(msg):
    #can add client name to msgObj on client side. server adds port number
    #on its side
    msgObj={}
    msgObj['contents']= msg
    return msgObj

def broadcast_msg(msgObj):
    global addressList
    global mailBox
    global chatRooms
     
    current_port = msgObj['from']
    for room in chatRooms.keys():
        for port in addressList:
            if port in chatRooms[room] and current_port in chatRooms[room]:
                #print(f'matching port = {port}')
                if port != current_port: 
                    msg=msgObj['contents']
                    print(f'msg = {msg}')
                    mailBox[port].append(msg)

def check_mail(port):
    global addressList
    global mailBox

    if(mailBox[port]):
        msg= mailBox[port].pop(0)
        print(f'retreiving: {msg!r}')
        return msg
    return None

async def listen_to_client(reader, addr, port, username):
    
    while True:
        global codes
        data = await reader.read(100)
        msgStr = data.decode()
        #checking if room message
        if  msgStr.lower() in codes:
            if msgStr == codes[0]:
                echo_roomGram = {}
                echo_roomGram['echo rooms'] = chatRooms
                echo_roomGramStr = str(echo_roomGram)
                echo_chatRooms(port, echo_roomGramStr)
            elif msgStr == codes[1]:
                general = leave_room(port, username)
                leave_Gram = {}
                if general:
                    leave_Gram['leave'] = 'You\'re in the General room. Do you want to quit the chat box? (q!) \
                                          \nDo nothing to stay here.'
                else: 
                    leave_Gram['leave'] = 'You\'ve returned to the General room. Say hello! \nMenu: (m!)'
                leave_GramStr = str(leave_Gram)
                echo(port, leave_GramStr)
            elif msgStr == codes[2]:
                delete_client(port) 
                break
            elif msgStr.lower() == 'j':
                room_chooseGram = {}
                room_chooseGram['room choose']= {}
                prompt = '\nTo join a room, type \'j!\' followed by the corresponding number of the room you wish to join:\n '
                room_chooseGram['room choose']['prompt'] = prompt 
                room_chooseGram['room choose']['rooms'] = chatRooms
                room_len = len(chatRooms.keys())
                room_chooseGram['room choose']['length'] = room_len
                room_chooseGramStr = str(room_chooseGram)
                echo(port, room_chooseGramStr)
            elif msgStr.lower() == 'c': 
                create_roomGram = {}
                create_roomGram['create room'] = {}
                prompt = 'To create a room, type \'c! \' followed by the name of the room you\'d like to create.\
                          \nIf the room already exists, you will join that room.'
                create_roomGram['create room']['prompt']  = prompt
                create_roomGramStr = str(create_roomGram)
                echo(port, create_roomGramStr)
            msgStr = None
        #if message object
        if msgStr != None:
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
            #adding port number to msgObj
            else:
                msgObj['from']=addr[1]
                print(f'msgObj = {msgObj!r}')
                broadcast_msg(msgObj)

async def send_to_client(writer, addr):
    while True:
        msgOut= check_mail(addr[1])
        if msgOut:
            writer.write(msgOut.encode())
            await writer.drain()
            msgOut=None
        await asyncio.sleep(0)

def new_client(port, username):
    global addressList
    global mailBox
    global chatRooms

    if port not in addressList:
        print('adding port', port) 
        addressList.append(port)
    if port not in mailBox:
        mailBox[port]=[]       
    if len(chatRooms) == 0:
        chatRooms['General'] = {}
    chatRooms['General'][port] = username
    print('call alert')
    alert_add_to_room(port, username)
    print(chatRooms)

async def main(reader, writer):
    
    global addressList
    global lobby
    global chatRooms

    addr = writer.get_extra_info('peername')
    port = addr[1]
    username = await reader.read(100)
    username = username.decode()
    new_client(port, username)

    await asyncio.gather(listen_to_client(reader, addr, port, username), send_to_client(writer, addr))
    if no data 
    print("Close the client socket")
    writer.close()

#127.0.0.1 is local host
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
