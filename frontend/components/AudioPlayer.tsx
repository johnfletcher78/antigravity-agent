"use client";

import React, { useEffect, useRef } from 'react';

interface AudioPlayerProps {
    audioUrl: string | null;
    onEnded: () => void;
}

export default function AudioPlayer({ audioUrl, onEnded }: AudioPlayerProps) {
    const audioRef = useRef<HTMLAudioElement>(null);

    useEffect(() => {
        if (audioUrl && audioRef.current) {
            audioRef.current.src = audioUrl;
            audioRef.current.play().catch(e => console.error("Audio playback failed:", e));
        }
    }, [audioUrl]);

    return (
        <audio
            ref={audioRef}
            onEnded={onEnded}
            className="hidden"
        />
    );
}
