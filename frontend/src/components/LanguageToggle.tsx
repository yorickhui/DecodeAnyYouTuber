'use client';

import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { Globe } from 'lucide-react';

export default function LanguageToggle() {
    const { language, setLanguage } = useLanguage();

    return (
        <button
            onClick={() => setLanguage(language === 'zh' ? 'en' : 'zh')}
            className="fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-gray-300 hover:bg-white/10 transition-all animate-in fade-in slide-in-from-top-4 duration-700"
            title={language === 'zh' ? "Switch to English" : "切换到中文"}
        >
            <Globe size={16} />
            <span className="font-medium">{language === 'zh' ? 'EN' : '中'}</span>
        </button>
    );
}
