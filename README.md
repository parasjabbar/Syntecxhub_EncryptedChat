# 🔐 Encrypted Chat Application

<div align="center">
  <h3>AES-256 Encrypted Client-Server Chat Application</h3>
  <p>Built for Syntecxhub Cybersecurity Internship - Week 2 Task</p>
</div>

## 📋 Project Overview

This is a secure client-server chat application that implements AES-256 encryption for all messages. The project demonstrates practical implementation of cryptography, socket programming, and multi-threading in Python.

## ✨ Features

- ✅ **End-to-end AES-256 encryption** for all messages
- ✅ **Multi-client support** with concurrent connections
- ✅ **Secure key derivation** using SHA-256
- ✅ **Random Initialization Vector (IV)** for each message
- ✅ **Message logging** on server side
- ✅ **Username system** for user identification
- ✅ **Clean console interface** with emoji indicators
- ✅ **Graceful disconnection** handling

## 🛠️ Technologies Used

- **Python 3.x** - Core programming language
- **PyCryptodome** - AES encryption library
- **Socket Programming** - TCP network communication
- **Threading** - Concurrent client handling

## 📁 Project Structure
Syntecxhub_EncryptedChat/
│
├── server.py # Chat server with client management
├── client.py # Chat client with encryption
├── encryption.py # AES encryption/decryption module
├── .gitignore # Git ignore file
└── README.md # Project documentation


## 🔐 How Encryption Works

1. **Key Generation**: Both server and client use a pre-shared key to generate a 256-bit AES key using SHA-256
2. **Message Encryption**: 
   - Random 16-byte IV generated per message
   - Message padded to AES block size
   - AES-256-CBC encryption applied
   - IV + ciphertext combined and base64 encoded
3. **Message Decryption**: 
   - Base64 decode to extract IV and ciphertext
   - Decrypt using same key and IV
   - Remove padding to get original message
