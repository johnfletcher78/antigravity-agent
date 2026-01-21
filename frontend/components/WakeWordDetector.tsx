"use client";

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Volume2 } from 'lucide-react';

interface WakeWordDetectorProps {
    onWakeWordDetected: () => void;
    isActive: boolean;
}

export default function WakeWordDetector({ onWakeWordDetected, isActive }: WakeWordDetectorProps) {
    const [isListening, setIsListening] = useState(false);
    const [lastHeard, setLastHeard] = useState<string>('');
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        // Check if browser supports speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.log("Browser does not support speech recognition.");
            return;
        }

        // @ts-ignore
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = true; // Keep listening
        recognition.interimResults = true; // Get interim results
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            console.log('Wake word detection started');
            setIsListening(true);
        };

        recognition.onend = () => {
            console.log('Wake word detection ended, restarting...');
            setIsListening(false);
            // Automatically restart if still active
            if (isActive && recognitionRef.current) {
                setTimeout(() => {
                    try {
                        recognition.start();
                    } catch (e) {
                        console.log('Recognition already started');
                    }
                }, 100);
            }
        };

        recognition.onerror = (event: any) => {
            console.log('Speech recognition error:', event.error);
            if (event.error === 'no-speech') {
                // Restart on no-speech error
                recognition.stop();
            }
        };

        recognition.onresult = (event: any) => {
            const last = event.results.length - 1;
            const transcript = event.results[last][0].transcript.toLowerCase().trim();

            setLastHeard(transcript);
            console.log('Heard:', transcript);

            // Check for wake words (multiple variations)
            const wakeWords = [
                'hey nat i need you',
                'hey nat i need',
                'hey nat',
                'nat i need you',
                'hey not i need you', // Common misheard variation
                'hey not i need',
                'hey not',
            ];

            if (wakeWords.some(phrase => transcript.includes(phrase))) {
                console.log('Wake word detected!');
                onWakeWordDetected();
                // Brief pause after detection
                recognition.stop();
                setTimeout(() => {
                    if (isActive) {
                        try {
                            recognition.start();
                        } catch (e) {
                            console.log('Recognition already started');
                        }
                    }
                }, 2000);
            }
        };

        recognitionRef.current = recognition;

        // Start listening if active
        if (isActive) {
            try {
                recognition.start();
            } catch (e) {
                console.log('Recognition already started');
            }
        }

        // Cleanup
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
                recognitionRef.current = null;
            }
        };
    }, [isActive, onWakeWordDetected]);

    if (!isActive) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="fixed bottom-8 right-8 z-50"
            >
                <div className="relative">
                    {/* Listening indicator */}
                    <motion.div
                        className="flex items-center gap-3 px-4 py-3 rounded-full bg-gradient-to-r from-purple-500/20 to-blue-500/20 backdrop-blur-lg border border-white/10 shadow-2xl"
                        animate={{
                            boxShadow: isListening
                                ? ['0 0 20px rgba(168, 85, 247, 0.4)', '0 0 40px rgba(168, 85, 247, 0.6)', '0 0 20px rgba(168, 85, 247, 0.4)']
                                : '0 0 20px rgba(168, 85, 247, 0.2)',
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        {/* Animated microphone icon */}
                        <motion.div
                            animate={{
                                scale: isListening ? [1, 1.1, 1] : 1,
                            }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                        >
                            <Volume2 className="w-5 h-5 text-purple-400" />
                        </motion.div>

                        {/* Status text */}
                        <div className="flex flex-col">
                            <span className="text-sm font-medium text-white">
                                Listening for "Hey NAT"
                            </span>
                            {lastHeard && (
                                <span className="text-xs text-gray-400 truncate max-w-[200px]">
                                    {lastHeard}
                                </span>
                            )}
                        </div>

                        {/* Pulsing indicator */}
                        {isListening && (
                            <motion.div
                                className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full"
                                animate={{
                                    scale: [1, 1.5, 1],
                                    opacity: [1, 0.5, 1],
                                }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            />
                        )}
                    </motion.div>

                    {/* Audio wave visualization */}
                    {isListening && (
                        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 flex gap-1">
                            {[...Array(5)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    className="w-1 bg-purple-400 rounded-full"
                                    animate={{
                                        height: ['4px', '12px', '4px'],
                                    }}
                                    transition={{
                                        duration: 0.8,
                                        repeat: Infinity,
                                        delay: i * 0.1,
                                    }}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </motion.div>
        </AnimatePresence>
    );
}
