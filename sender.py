#!/usr/bin/env python

import struct, sys, time, socket

# 0. Usage and Argument initialization
if ( len( sys.argv ) != 5 ):
	sys.exit( "Usage: " + sys.argv[0] + " <emulator hostname> <UDP port to send data to> <UDP port to receive ACKs from> <file to transfer>" )

emu_hostname = sys.argv[1]
emu_port = int( sys.argv[2] )
emu = ( emu_hostname, emu_port )

sender_port = int( sys.argv[3] )
filename = open( sys.argv[4], "r" )
seqnum_log = open( "seqnum.log", "w" )
ack_log = open( "ack.log", "w" )

senderSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
senderSocket.bind( ( '', sender_port ) )
senderSocket.setblocking( 0 ) # Our socket must not block on recvfrom()!

timeoutpd = 0.050 # 50ms, change as needed
timer_running = False # Flag variable :( 

eot_ready = False # Flag variable 2 :((
eot = '' # Just forward declaring it

empty_case = True # Flag variable 3 :(((

win_max = 10
base = 0
nextseqnum = 0
packetbuffer = [] # Will hold up to 32 packets for potential retransmission
for i in range(0, 32):
	packetbuffer.append(i) # Allows for direct assignment into packetbuffer[ index ]
# for 


# 1. Begin the loop of creating & sending packets, receiving ACKs, and timeouts
while True:
	try: # Check if you received an ACK packet
		ack, addr = senderSocket.recvfrom( 512 )
		ptype, pseqnum, plength, pdata = struct.unpack( '!iii500s', ack )
		ack_log.write( str( pseqnum ) + '\n' ) # Log the packet's ACK seqnum
		base = (pseqnum + 1) % 32 # Update sender window's base

		if ( base == nextseqnum ):
			timer_running = False # Stop the timer
			if ( eot_ready == True ): # If this was the final ACK:
				senderSocket.sendto( eot, emu ) # Send EOT packet
				seqnum_log.write( str( nextseqnum ) + '\n' ) # Log the packet seqnum
				break # Move to section 2. and wait for rcvr EOT.
			# if
		else:
			timer = time.time()
			timer_running = True # Restart the timer
		# if
		continue # Do not check timeout/room-in-window ifs
	except socket.error: # If there was nothing to receive,
		# Continue to check the timeout if and the room-in-window elif.
		pass
	# try

	if ( timer_running and time.time() - timer > timeoutpd ): # If timeout:
		timer = time.time() # Restart the timer

		# Resend all packets in the window:
		tempbase = base
		while ( tempbase != nextseqnum ):
			senderSocket.sendto( packetbuffer[ tempbase ], emu )
			seqnum_log.write( str( tempbase ) + '\n' ) # Log the resent seqnum
			tempbase = (tempbase + 1) % 32
		# while
	elif ( nextseqnum < base + win_max ): # If there is room in the sender window:
		filedata = filename.read( 500 )

		if len( filedata ) == 0: # If you've read everything in the file:
			eot = struct.pack( '!iii500s', 2, nextseqnum, len( filedata ), filedata )
			eot_ready = True # Prepare to send EOT upon receipt of final ACK (above)

			if ( empty_case ): # ONLY TO SOLVE THE EMPTY FILE CASE
				# In this case, send the EOT immediately.
				senderSocket.sendto( eot, emu )
				seqnum_log.write( str( nextseqnum ) + '\n' ) # Log the packet seqnum
				break
		else:
			empty_case = False

			packet = struct.pack( '!iii500s', 1, nextseqnum, len( filedata ), filedata )
			senderSocket.sendto( packet, emu ) # Send data packet
			seqnum_log.write( str( nextseqnum ) + '\n' ) # Log the packet's seqnum
			packetbuffer[ nextseqnum ] = packet
			if ( base == nextseqnum ):
				timer = time.time() # Restart the timer
				timer_running = True
			# if
			nextseqnum = (nextseqnum + 1) % 32
		# if
	# if
# while


# 2. Wait to receive EOT packet from emulator
senderSocket.setblocking( 1 ) # NOW set our socket to block on recvfrom()
eot, addr = senderSocket.recvfrom( 512 ) # Receive the EOT packet.
# As EOT packets are never lost and we have received all ACKs,
# this is guaranteed to be EOT.
ptype, pseqnum, plength, pdata = struct.unpack( '!iii500s', eot )


# 3. Cleanup
senderSocket.close()
filename.close()
seqnum_log.close()
ack_log.close()
