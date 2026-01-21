"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import VoiceInput from './VoiceInput';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: "Hey Bull! I'm NAT (Not A Terminator), your personal marketing AI. Ready to crush some campaigns together? What's on your mind?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Configuration
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

    // Audio State
    const audioQueue = useRef<string[]>([]);
    const isPlaying = useRef(false);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initialize Audio Element once
    useEffect(() => {
        audioRef.current = new Audio();
        audioRef.current.onended = () => {
            isPlaying.current = false;
            playNextChunk();
        };
    }, []);

    const playNextChunk = () => {
        if (isPlaying.current || audioQueue.current.length === 0) return;

        const nextUrl = audioQueue.current.shift();
        if (nextUrl && audioRef.current) {
            isPlaying.current = true;
            audioRef.current.src = nextUrl;
            audioRef.current.play().catch(e => {
                console.error("Audio playback error:", e);
                isPlaying.current = false;
                playNextChunk();
            });
        }
    };

    const queueAudioChunk = (url: string) => {
        audioQueue.current.push(url);
        // Try to play immediately if nothing is playing
        playNextChunk();
    };

    const fetchTTSChunk = async (text: string) => {
        try {
            const ttsResponse = await fetch(`${API_URL}/chat/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });

            if (ttsResponse.ok) {
                const blob = await ttsResponse.blob();
                const url = URL.createObjectURL(blob);
                queueAudioChunk(url);
            }
        } catch (e) {
            console.error("TTS Chunk Error:", e);
        }
    };

    const handleSend = async (text: string = input) => {
        if (!text.trim()) return;

        // Stop any current playback
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
        }
        audioQueue.current = [];
        isPlaying.current = false;

        const newMessage: Message = { role: 'user', content: text };
        setMessages(prev => [...prev, newMessage]);
        setInput('');
        setIsLoading(true);

        try {
            setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

            const response = await fetch(`${API_URL}/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const reader = response.body?.getReader();
            if (!reader) throw new Error("No reader");

            const decoder = new TextDecoder();

            let buffer = "";
            const sentenceEndings = /[.!?]+/;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;

                // Update UI
                setMessages(prev => {
                    const lastMsg = prev[prev.length - 1];
                    if (lastMsg.role === 'assistant') {
                        return [
                            ...prev.slice(0, -1),
                            { ...lastMsg, content: lastMsg.content + chunk }
                        ];
                    }
                    return prev;
                });

                // Check for sentence completion
                const match = buffer.match(sentenceEndings);
                if (match) {
                    const endIdx = match.index! + match[0].length;
                    const sentence = buffer.substring(0, endIdx);
                    // Only speak if it's substantial (filters out "Mr.", "No.")
                    if (sentence.length > 5) {
                        fetchTTSChunk(sentence.trim());
                        buffer = buffer.substring(endIdx);
                    }
                }
            }

            // Speak remaining
            if (buffer.trim().length > 0) {
                fetchTTSChunk(buffer.trim());
            }

        } catch (error: any) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `I'm having trouble connecting. \n\nError details: ${error.message || "Unknown error"}`
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleVoiceResult = (text: string) => {
        setInput(text);
        handleSend(text);
    };

    return (
        <div className="flex flex-col h-[calc(100vh-100px)] w-full max-w-4xl mx-auto rounded-3xl bg-black/40 backdrop-blur-xl border border-white/10 overflow-hidden shadow-2xl">

            <div className="p-4 border-b border-white/10 bg-white/5 flex items-center gap-3">
                <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500">
                    <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h2 className="text-white font-semibold">NAT (Not A Terminator)</h2>
                    <p className="text-xs text-gray-400">Bull's Personal Marketing AI</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`flex items-start gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user'
                            ? 'bg-white text-black'
                            : 'bg-indigo-600 text-white'
                            }`}>
                            {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                        </div>

                        <div className={`p-4 rounded-2xl max-w-[80%] ${msg.role === 'user'
                            ? 'bg-white text-black rounded-tr-none'
                            : 'bg-white/10 text-gray-100 rounded-tl-none border border-white/5'
                            }`}>
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex items-start gap-4">
                        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div className="p-4 rounded-2xl bg-white/10 border border-white/5 rounded-tl-none">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
                                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white/5 border-t border-white/10">
                <div className="relative flex items-center gap-2">
                    <VoiceInput onSpeechResult={handleVoiceResult} isProcessing={isLoading} />

                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about your campaigns..."
                        className="flex-1 bg-black/20 text-white placeholder-gray-500 rounded-full px-6 py-3 border border-white/10 focus:outline-none focus:border-indigo-500/50 focus:bg-black/40 transition-all font-light"
                        disabled={isLoading}
                    />

                    <button
                        onClick={() => handleSend()}
                        disabled={!input.trim() || isLoading}
                        className="p-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
