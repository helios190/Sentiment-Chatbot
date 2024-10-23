import React, { useState } from 'react';
import './Chatbox.css';

const Chatbox = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');

    const toggleChatbox = () => {
        setIsOpen(!isOpen);
    };

    const onSendMessage = async () => {
        if (inputMessage.trim() === '') return;

        const userMessage = { name: 'Sam', message: inputMessage }; // Change name to 'Sam'
        setMessages((prevMessages) => [...prevMessages, userMessage]);

        try {
            const response = await fetch('http://127.0.0.1:5000/get_rag_chain', {
                method: 'POST',
                body: JSON.stringify({ query: inputMessage }),
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();
            const botMessage = { name: 'Mari Belajar Chatbot', message: data.response };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = { name: 'Mari Belajar Chatbot', message: 'Oops, something went wrong!' };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        }

        setInputMessage('');
    };

    const handleKeyUp = (event) => {
        if (event.key === 'Enter') {
            onSendMessage();
        }
    };

    return (
        <div className="chatbox">
            <div className="chatbox__button">
                <button onClick={toggleChatbox}>
                    <img src="https://img.icons8.com/color/48/000000/circled-user-female-skin-type-5--v1.png" alt="Chatbox" />
                </button>
            </div>

            {isOpen && (
                <div className={`chatbox__support ${isOpen ? 'chatbox--active' : ''}`}>
                    <div className="chatbox__header">
                        <div className="chatbox__image--header">
                            <img
                                src="https://img.icons8.com/color/48/000000/circled-user-female-skin-type-5--v1.png"
                                alt="Mari Belajar"
                            />
                        </div>
                        <div className="chatbox__content--header">
                            <h4 className="chatbox__heading--header">Chat Support</h4>
                            <p className="chatbox__description--header">
                                Halo! Aku Mari Belajar Chatbot. Ada yang bisa saya bantu?
                            </p>
                        </div>
                    </div>

                    <div className="chatbox__messages">
                        {messages.slice().reverse().map((msg, index) => (
                            <div
                                key={index}
                                className={`messages__item ${
                                    msg.name === 'Sam'
                                        ? 'messages__item--visitor'
                                        : 'messages__item--operator'
                                }`}
                            >
                                {msg.message}
                            </div>
                        ))}
                    </div>

                    <div className="chatbox__footer">
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyUp={handleKeyUp}
                            placeholder="Write a message..."
                        />
                        <button onClick={onSendMessage} className="chatbox__send--footer">
                            Send
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chatbox;
