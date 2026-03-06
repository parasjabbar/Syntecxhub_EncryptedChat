import socket
import threading
from encryption import Encryptor
import datetime

class ChatServer:
    def __init__(self, host='127.0.0.1', port=5555):
        """
        Initialize the chat server
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []  # List of client sockets
        self.usernames = {}  # Dictionary mapping socket -> username
        self.encryptor = Encryptor("server_shared_key")  # Pre-shared key
        
        # For logging messages
        self.log_file = f"chat_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        print(f"[Server] Encryptor initialized with pre-shared key")
    
    def log_message(self, message):
        """Log messages to file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass  # Silently fail if logging doesn't work
    
    def broadcast(self, message, sender_socket=None):
        """
        Send a message to all clients except the sender
        Message is already encrypted
        """
        for client in self.clients:
            if client != sender_socket:  # Don't send back to sender
                try:
                    client.send(message.encode('utf-8'))
                except:
                    # Remove dead clients
                    self.clients.remove(client)
                    if client in self.usernames:
                        del self.usernames[client]
    
    def handle_client(self, client_socket, address):
        """
        Handle individual client connection
        """
        print(f"[Server] New connection from {address}")
        
        # Ask for username
        try:
            # Send username request (plain text for initial handshake)
            client_socket.send("USERNAME_REQUEST".encode('utf-8'))
            
            # Receive username (plain for handshake)
            username = client_socket.recv(1024).decode('utf-8')
            self.usernames[client_socket] = username
            
            # Announce new user
            join_msg = f"🔵 {username} joined the chat!"
            print(f"[Server] {join_msg}")
            
            # Log the join
            self.log_message(f"USER JOINED: {username} from {address}")
            
            # Encrypt and broadcast join message
            encrypted_join = self.encryptor.encrypt_message(join_msg)
            self.broadcast(encrypted_join)
            
        except Exception as e:
            print(f"[Server] Error during username setup: {e}")
            client_socket.close()
            return
        
        # Main message loop
        while True:
            try:
                # Receive encrypted message from client
                encrypted_data = client_socket.recv(1024).decode('utf-8')
                
                if not encrypted_data:
                    break
                
                # Decrypt the message
                decrypted_msg = self.encryptor.decrypt_message(encrypted_data)
                
                if decrypted_msg:
                    # Format message with username
                    full_msg = f"{username}: {decrypted_msg}"
                    print(f"[Server] {full_msg}")
                    
                    # Log the message
                    self.log_message(f"{username}: {decrypted_msg}")
                    
                    # Encrypt for broadcasting
                    encrypted_broadcast = self.encryptor.encrypt_message(full_msg)
                    
                    # Broadcast to all clients except sender
                    for client in self.clients:
                        if client != client_socket:
                            try:
                                client.send(encrypted_broadcast.encode('utf-8'))
                            except:
                                pass
                
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[Server] Error: {e}")
                break
        
        # Client disconnected
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        
        if client_socket in self.usernames:
            username = self.usernames[client_socket]
            leave_msg = f"🔴 {username} left the chat."
            print(f"[Server] {leave_msg}")
            
            # Log the leave
            self.log_message(f"USER LEFT: {username}")
            
            # Encrypt and broadcast leave message
            encrypted_leave = self.encryptor.encrypt_message(leave_msg)
            self.broadcast(encrypted_leave)
            
            del self.usernames[client_socket]
        
        client_socket.close()
        print(f"[Server] Connection closed for {address}")
    
    def start(self):
        """
        Start the server
        """
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            print(f"[Server] Started on {self.host}:{self.port}")
            print(f"[Server] Logging to: {self.log_file}")
            print(f"[Server] Waiting for connections...\n")
            
            # Log server start
            self.log_message("SERVER STARTED")
            
            while True:
                # Accept new client connection
                client_socket, address = self.server_socket.accept()
                
                # Add to clients list
                self.clients.append(client_socket)
                
                # Create thread for client
                thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                thread.daemon = True
                thread.start()
                
                # Print active connections count
                print(f"[Server] Active connections: {len(self.clients)}")
                
        except Exception as e:
            print(f"[Server Error] {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            print("[Server] Shut down")

if __name__ == "__main__":
    server = ChatServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down by user request...")