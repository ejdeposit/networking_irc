#client
import asyncio
import sys

async def send_to_server(writer, loop):
    while True:
        line= await loop.run_in_executor(None, sys.stdin.readline)
        line=line[::]
        if line:
            print('Send: %r' % line)
            writer.write(line.encode())
            line=None

async def listen_to_server(reader):
    while True:
        data = await reader.read(100)
        print('Received: %r' % data.decode())
        await asyncio.sleep(0)


async def tcp_echo_client(loop):
    #opens connection to server
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888, loop=loop)

    await asyncio.gather(listen_to_server(reader), send_to_server(writer, asyncio.get_running_loop()))

    #closes connection
    print('Close the socket')
    writer.close()


#problem: this client sends message and then closes loop.  need to listen
loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
loop.close()
