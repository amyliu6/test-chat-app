import React, { useState } from 'react';
import { io } from 'socket.io-client';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import './App.css';

const socket = io('ws://localhost:50000');

// Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.


const App = () => {
  const [serverMessage, setServerMessage] = useState(null);
  const [initialPrompt, setInitialPrompt] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([
    // {
    //   role: 'system',
    //   content: "Your role is to help user with product management."
    // //   content: 'As an AI assistant, your aim is to be both helpful and friendly while assisting users with product creation. Follow these steps: Please first evaluate whether the user has provided all required parameters for a function call, then check if any optional fields need to be specified. Remember all parameters provided by users throughout the conversation. Confirm that users have provided all necessary parameters for a function call before proceeding. If a user\'s request is unclear, ask for clarification. Always maintain a friendly and polite tone in your interactions. If a parameter is forgotten, apologize and ask the user to repeat it.'
    // }
  ]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyUp = (e) => {
    if (e.key === 'Enter') {
        sendToServer(inputValue);
        setInputValue(''); // Resetting the input field
    }
  };

  const handleInitialPromptChange = (e) => {
    setInitialPrompt(e.target.value);
  };

  const handleInitialPromptSubmit = () => {
    if (initialPrompt.trim() !== '') {
        const updatedMessages = [...messages, { role: 'system', content: initialPrompt }];
        setMessages(updatedMessages);
    }
  };

  socket.on('from-server', (model_message) => {
    // console.log('model_message: ', model_message)
    if (model_message.content) {
        const updatedMessages = [...messages, { role: model_message.role, content: model_message.content }];
        setMessages(updatedMessages);
    } else {
        const secondRes = model_message.choices[0].message
        const updatedMessages = [...messages, { role: secondRes.role, content: secondRes.content }];
        setMessages(updatedMessages);
    }
    
  });

  const sendToServer = (msg) => {
    const updatedMessages = [...messages, { role: 'user', content: msg }];
    setMessages(updatedMessages);
    // console.log('updatedMessages', updatedMessages)
    socket.emit('to-server', updatedMessages);
  };

  const clearHistory = () => {
    setMessages([]);
  }

  return (
    <div className="App">
        <div className="initial-prompt">
            <Typography variant="h6">Initial Prompt:</Typography>
            <div className="input-container">
                <TextField
                    type="text"
                    value={initialPrompt}
                    onChange={handleInitialPromptChange}
                    variant="outlined"
                    fullWidth
                    multiline
                />
                <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={handleInitialPromptSubmit}>
                Set
                </Button>
            </div>
        </div>

        <div className="chat-history">
            <Typography variant="h6">Chat History:</Typography>
            <div className="message-container">
                {messages.map((message, index) => (
                <Typography key={index} variant="body1" className={`message ${message.role}`}>
                    <span className="role">{message.role}:</span>
                    <span className="content">{message.content}</span>
                </Typography>
                ))}
            </div>
        </div>
        <Button variant="contained" color="primary" style={{marginTop: 20}} onClick={() => clearHistory()}>
            Clear history
        </Button>

        <div className="user-input" style={{textAlign: 'left'}}>
            <Typography variant="h6">User input:</Typography>
            <TextField
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyUp={handleKeyUp} // Added event handler for key press
            variant="outlined"
            fullWidth
            />
            
        </div>
    </div>
  );
};

export default App;
