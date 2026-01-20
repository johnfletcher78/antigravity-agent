"use client";

import React, { useState } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { motion } from 'framer-motion';

interface VoiceInputProps {
    onSpeechResult: (text: string) => void;
    isProcessing: boolean;
}

export default function VoiceInput({ onSpeechResult, isProcessing }: VoiceInputProps) {
    const [isListening, setIsListening] = useState(false);

    const startListening = () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert("Browser does not support speech recognition.");
            return;
        }

        // @ts-ignore
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            onSpeechResult(transcript);
        };

        recognition.start();
    };

    return (
        <button
            onClick={startListening}
            disabled={isListening || isProcessing}
            className={`relative p-3 rounded-full transition-all duration-300 ${isListening
                    ? 'bg-red-500/20 text-red-400 border border-red-500/50'
                    : 'bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white border border-white/10'
                }`}
        >
            {isListening ? (
                <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                >
                    <Mic className="w-5 h-5" />
                </motion.div>
            ) : (
                <Mic className="w-5 h-5" />
            )}

            {isListening && (
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping" />
            )}
        </button>
    );
}
