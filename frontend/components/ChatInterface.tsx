"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Mic, MicOff, Cpu, Activity, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import VoiceInput from './VoiceInput';
import WakeWordDetector from './WakeWordDetector';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: "Hey Bull! What can I help you with?" }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [wakeWordEnabled, setWakeWordEnabled] = useState(false);
    const [time, setTime] = useState(new Date());

    // Configuration
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

    // Audio State
    const audioQueue = useRef<string[]>([]);
    const isPlaying = useRef(false);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Update time every second
    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initialize Audio Element
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

            const conversationHistory = messages.map(msg => ({
                role: msg.role,
                content: msg.content
            }));

            const response = await fetch(`${API_URL}/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    history: conversationHistory
                }),
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

                const match = buffer.match(sentenceEndings);
                if (match) {
                    const endIdx = match.index! + match[0].length;
                    const sentence = buffer.substring(0, endIdx);
                    if (sentence.length > 5) {
                        fetchTTSChunk(sentence.trim());
                        buffer = buffer.substring(endIdx);
                    }
                }
            }

            if (buffer.trim().length > 0) {
                fetchTTSChunk(buffer.trim());
            }

        } catch (error: any) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Connection error: ${error.message || "Unknown error"}`
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
        <div className="min-h-screen bg-[#0a0e1a] text-cyan-100 flex items-center justify-center p-6 overflow-hidden relative">
            {/* Animated background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px]">
                    <div className="absolute inset-0 rounded-full border border-cyan-500/20 animate-pulse-slow"></div>
                    <div className="absolute inset-8 rounded-full border border-cyan-500/15 animate-pulse-slower"></div>
                    <div className="absolute inset-16 rounded-full border border-cyan-500/10 animate-pulse-slowest"></div>
                </div>
            </div>

            <WakeWordDetector
                isActive={wakeWordEnabled}
                onWakeWordDetected={() => { }}
            />

            {/* Main Container - Wider and Less Tall */}
            <div className="w-full max-w-7xl h-[85vh] bg-[#0a0e1a]/80 backdrop-blur-xl border border-cyan-500/30 rounded-2xl shadow-2xl shadow-cyan-500/10 flex overflow-hidden relative z-10">
                {/* Left Sidebar - System Stats */}
                <div className="w-64 border-r border-cyan-500/20 p-4 space-y-4 relative z-10">
                    <div className="bg-cyan-950/30 backdrop-blur-sm border border-cyan-500/30 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Activity className="w-4 h-4 text-cyan-400" />
                            <h3 className="text-sm font-semibold text-cyan-300">System Stats</h3>
                        </div>
                        <div className="space-y-2 text-xs">
                            <div className="flex justify-between">
                                <span className="text-cyan-400/70">CPU Usage</span>
                                <span className="text-cyan-300">8%</span>
                            </div>
                            <div className="w-full bg-cyan-950/50 rounded-full h-1.5">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '8%' }}></div>
                            </div>
                            <div className="flex justify-between mt-3">
                                <span className="text-cyan-400/70">RAM Usage</span>
                                <span className="text-cyan-300">2.1 GB</span>
                            </div>
                            <div className="w-full bg-cyan-950/50 rounded-full h-1.5">
                                <div className="bg-cyan-400 h-1.5 rounded-full" style={{ width: '26%' }}></div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-cyan-950/30 backdrop-blur-sm border border-cyan-500/30 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Database className="w-4 h-4 text-cyan-400" />
                            <h3 className="text-sm font-semibold text-cyan-300">Status</h3>
                        </div>
                        <div className="space-y-2 text-xs">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                                <span className="text-cyan-300">Online</span>
                            </div>
                            <div className="text-cyan-400/70">
                                Uptime: {Math.floor(Date.now() / 1000 % 86400 / 3600)}h {Math.floor(Date.now() / 1000 % 3600 / 60)}m
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1 flex flex-col relative z-10">
                    {/* Header */}
                    <div className="border-b border-cyan-500/20 p-4 backdrop-blur-sm bg-cyan-950/20">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="relative">
                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
                                        <Cpu className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-[#0a0e1a]"></div>
                                </div>
                                <div>
                                    <h1 className="text-xl font-bold text-cyan-300">N.A.T.</h1>
                                    <p className="text-xs text-cyan-400/70">Not A Terminator</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="text-right text-xs">
                                    <div className="text-cyan-300">{time.toLocaleTimeString()}</div>
                                    <div className="text-cyan-400/70">{time.toLocaleDateString()}</div>
                                </div>
                                <button
                                    onClick={() => setWakeWordEnabled(!wakeWordEnabled)}
                                    className={`p-2 rounded-lg transition-all ${wakeWordEnabled
                                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                                        : 'bg-cyan-950/30 text-cyan-400/50 hover:bg-cyan-950/50 border border-cyan-500/20'
                                        }`}
                                >
                                    {wakeWordEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`flex items-start gap-3 animate-fade-in ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user'
                                    ? 'bg-gradient-to-br from-blue-400 to-cyan-400'
                                    : 'bg-gradient-to-br from-cyan-500 to-blue-600'
                                    }`}>
                                    {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
                                </div>

                                <div className={`max-w-[70%] ${msg.role === 'user'
                                    ? 'bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border-blue-400/30'
                                    : 'bg-cyan-950/40 border-cyan-500/30'
                                    } border backdrop-blur-sm rounded-2xl p-4 ${msg.role === 'user' ? 'rounded-tr-none' : 'rounded-tl-none'}`}>
                                    <div className="text-sm leading-relaxed">
                                        <ReactMarkdown
                                            components={{
                                                a: ({ node, ...props }) => (
                                                    <a {...props} className="text-cyan-400 hover:text-cyan-300 underline" target="_blank" rel="noopener noreferrer" />
                                                ),
                                                p: ({ node, ...props }) => <span {...props} className="whitespace-pre-wrap" />
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex items-start gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                                    <Bot className="w-4 h-4 text-white" />
                                </div>
                                <div className="bg-cyan-950/40 border border-cyan-500/30 backdrop-blur-sm rounded-2xl rounded-tl-none p-4">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></span>
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                                        <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="border-t border-cyan-500/20 p-4 backdrop-blur-sm bg-cyan-950/20">
                        <div className="flex items-center gap-2">
                            <VoiceInput onSpeechResult={handleVoiceResult} isProcessing={isLoading} />

                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSend();
                                    }
                                }}
                                placeholder="Type a message... (Shift+Enter for new line)"
                                className="flex-1 bg-cyan-950/30 text-cyan-100 placeholder-cyan-400/50 rounded-2xl px-6 py-3 border border-cyan-500/30 focus:outline-none focus:border-cyan-400/50 focus:bg-cyan-950/40 transition-all resize-none min-h-[48px] max-h-[200px] overflow-y-auto"
                                disabled={isLoading}
                                rows={1}
                                style={{
                                    height: 'auto',
                                    minHeight: '48px'
                                }}
                                onInput={(e) => {
                                    const target = e.target as HTMLTextAreaElement;
                                    target.style.height = 'auto';
                                    target.style.height = Math.min(target.scrollHeight, 200) + 'px';
                                }}
                            />

                            <button
                                onClick={() => handleSend()}
                                disabled={!input.trim() || isLoading}
                                className="p-3 bg-gradient-to-br from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyan-500/20"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
