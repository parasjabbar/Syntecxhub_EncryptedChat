import socket
import threading
from encryption import Encryptor
import sys
import os

class ChatClient:
    def __init__(self, host='127.0.0.1', port=5555):
        """
        Initialize the chat client
        """
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.encryptor = Encryptor("server_shared_key")  # Same pre-shared key as server
        self.running = True
        
        print("[Client] Encryptor initialized")
    
    def receive_messages(self):
        """
        Receive and display messages from server
        """
        while self.running:
            try:
                # Receive encrypted message
                encrypted_data = self.socket.recv(1024).decode('utf-8')
                
                if not encrypted_data:
                    break
                
                # Check if it's a special server command
                if encrypted_data == "USERNAME_REQUEST":
                    # Send username (plain for handshake)
                    self.socket.send(self.username.encode('utf-8'))
                    continue
                
                # Decrypt the message
                decrypted_msg = self.encryptor.decrypt_message(encrypted_data)
                
                if decrypted_msg:
                    # Clear the current input line, print message, then re-prompt
                    sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
                    print(decrypted_msg)
                    print(f"You: ", end='', flush=True)
                
            except ConnectionResetError:
                print("\n[Error] Connection to server lost.")
                break
            except Exception as e:
                if self.running:  # Only show error if still running
                    print(f"\n[Error] {e}")
                break
        
        print("\n[Client] Disconnected from server.")
        self.running = False
    
    def start(self):
        """
        Connect to server and start chat
        """
        try:
            # Get username
            self.username = input("Enter your username: ").strip()
            if not self.username:
                self.username = "Anonymous"
            
            # Connect to server
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            print(f"[Client] Connected to {self.host}:{self.port}")
            print(f"[Client] Logged in as: {self.username}")
            print("-" * 50)
            print("Type your messages and press Enter to send.")
            print("Type '/quit' to exit.")
            print("-" * 50)
            
            # Start receive thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Main send loop
            while self.running:
                try:
                    message = input("You: ")
                    
                    if message.lower() == '/quit':
                        break
                    
                    if message.strip() == '':
                        continue
                    
                    # Encrypt the message
                    encrypted_msg = self.encryptor.encrypt_message(message)
                    
                    if encrypted_msg:
                        # Send encrypted message
                        self.socket.send(encrypted_msg.encode('utf-8'))
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"[Send Error] {e}")
                    break
            
        except ConnectionRefusedError:
            print("[Error] Could not connect to server. Make sure the server is running.")
        except Exception as e:
            print(f"[Error] {e}")
        finally:
            self.running = False
            if self.socket:
                self.socket.close()
            print("[Client] Shut down")

if __name__ == "__main__":
    # Clear screen for better experience
    os.system('cls' if os.name == 'nt' else 'clear')
    
    client = ChatClient()
    client.start()