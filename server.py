#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio, socket, json # socket library likely not necessary

#connections represent the active connections on the server, admin sockets is used for broadcasting the connections to the admins
connections = list()
adminSockets = []

async def handle_client(reader, writer):
  #connection here is address, port
  connection = writer._transport.get_extra_info('peername')
  #notifies all admin users of the current status of the connections
  def broadcast_to_admin():
  	for addressbc,readerbc,writerbc in adminSockets:
  		connectionsString = str(connections).strip('[]').encode('utf8')
  		writerbc.write(connectionsString)
  #disconnect_client removes the client from the lists and closes the connection
  def disconnect_client():
  	remove_disconnections(connection, connections)
  	remove_disconnections(connection, adminSockets)
  	broadcast_to_admin()
  	writer.close()

  while 1:
    try:
    	#reads the incoming package until ^ and erases the char
    	info = (await reader.readuntil(b'^')).decode('utf8').replace('^','')
    except:
    	#if it fails to read the package it will disconnect
    	disconnect_client()
    	break
    #the message is casted to a json and if it succeeds it adds the connection to the lists 
    infoJson = is_json(info)
    print(infoJson)
    if infoJson != False or infoJson != 'start':
      print(type(infoJson))
      connectionJson = {'address': ','.join(map(str,connection))}
      infoJson.update(connectionJson)
      connection_in(infoJson,connections)
      if infoJson["role"] == "admin":
       connection_in((connection,reader,writer),adminSockets)
      broadcast_to_admin()
    
    #if there's an expected disconnection a message with the content of !DISCONNECT is recieved
    if info == '!DISCONNECT':
    	disconnect_client()
    	break
    
    writer.write(f'ok, received {info}'.encode('utf8'))
    await writer.drain()
  writer.close()

async def run_server():
  port = 15555
  server = await asyncio.start_server(handle_client, 'localhost', port)
  #server = await asyncio.start_server(handle_client, '144.126.212.229', port)
  async with server:
    print(f'Listening on localhost {port}')
    await server.serve_forever()

def is_json(someJSON):
  try:
    json_object = json.loads(someJSON)
  except ValueError as e:
    return False
  return json_object

#due to dictionaries not being a hashable type casting a dict list into a set is not possible
#therefore this is not as efficient as doing so but it gets the job done
def connection_in(incoming, existingList):
	exists = False
	if not existingList:
		existingList.append(incoming)
	else:
		#listSet = set(existingList)
		for i in existingList:
			if incoming == i:
				exists = True
		if exists == False:
			return existingList.append(incoming)

def remove_disconnections(address, existingList):
	removed = -1
	addressStr = ','.join(map(str,address))
	for i, item in enumerate(existingList):
		if addressStr in item or addressStr: #== item["address"]:
			removed = i
			break
	if removed != -1:
		existingList.pop(removed)

asyncio.run(run_server())