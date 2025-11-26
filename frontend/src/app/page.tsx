'use client';

import { useState } from 'react';
import Image from 'next/image';
import { ArrowRight, Youtube, Loader2, Sparkles } from 'lucide-react';
import { BilibiliIcon } from '@/components/BilibiliIcon';
import ReportViewer from '@/components/ReportViewer';
import { useLanguage } from '@/contexts/LanguageContext';

export default function Home() {
  const { t, language } = useLanguage();
  const [platform, setPlatform] = useState<'youtube' | 'bilibili'>('youtube');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState(t.status.ready);

  const handleAnalyze = async () => {
    if (!url) return;

    setLoading(true);
    setError(null);
    setReport(null);
    setStatus(t.status.initializing);

    try {
      // Simulate steps for better UX since backend is synchronous for now
      // In a real app, we'd use SSE or WebSockets
      const steps = [
        t.status.fetching,
        t.status.extracting,
        t.status.downloading,
        t.status.analyzing_visual,
        t.status.generating
      ];

      let stepIndex = 0;
      const interval = setInterval(() => {
        if (stepIndex < steps.length) {
          setStatus(steps[stepIndex]);
          stepIndex++;
        }
      }, 3000);

      const apiEndpoint = platform === 'youtube'
        ? '/analyze_channel'
        : '/analyze_bilibili_creator';

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${apiEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel_url: url, video_limit: 3, language, platform }),
      });

      clearInterval(interval);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || t.status.error);
      }

      const data = await response.json();
      setReport(data.report);
      setStatus(t.status.complete);
    } catch (err: any) {
      setError(err.message);
      setStatus(t.status.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-8 md:p-24 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-900/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/20 rounded-full blur-[120px]" />
      </div>

      {/* Hero Section */}
      <div className="z-10 w-full max-w-3xl text-center mb-16 space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm text-purple-300 mb-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <Sparkles size={16} />
          <span>{t.title}</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-400 animate-in fade-in slide-in-from-bottom-8 duration-1000">
          {t.heroTitle} <br />
          <span className={`text-transparent bg-clip-text bg-gradient-to-r ${platform === 'youtube'
            ? 'from-red-500 to-purple-600'
            : 'from-[#01AEEC] to-[#FB7299]'
            }`}>
            {typeof t.heroSubtitle === 'string' ? t.heroSubtitle : t.heroSubtitle[platform]}
          </span>
        </h1>

        <p className="text-lg text-gray-400 max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200">
          {typeof t.heroDesc === 'string' ? t.heroDesc : t.heroDesc[platform]}
        </p>
      </div>

      {/* Platform Selector */}
      <div className="w-full max-w-2xl mb-6 flex justify-center gap-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-150">
        <button
          onClick={() => setPlatform('youtube')}
          className={`w-36 px-6 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${platform === 'youtube'
            ? 'bg-white text-black shadow-lg'
            : 'glass text-gray-400 hover:text-white'
            }`}
        >
          <Youtube size={20} />
          YouTube
        </button>
        <button
          onClick={() => setPlatform('bilibili')}
          className={`w-36 px-6 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${platform === 'bilibili'
            ? 'bg-white text-black shadow-lg'
            : 'glass text-gray-400 hover:text-white'
            }`}
        >
          <BilibiliIcon size={20} />
          Bilibili
        </button>
      </div>

      {/* Input Section */}
      <div className="w-full max-w-2xl mb-12 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-300">
        <div className="flex gap-2 p-2 glass-card rounded-xl transition-all focus-within:ring-2 focus-within:ring-purple-500/50">
          <div className="flex items-center pl-4 text-gray-500">
            {platform === 'youtube' ? (
              <Youtube size={24} />
            ) : (
              <BilibiliIcon size={24} />
            )}
          </div>
          <input
            type="text"
            placeholder={typeof t.inputPlaceholder === 'string' ? t.inputPlaceholder : t.inputPlaceholder[platform]}
            className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500 p-4"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading || !url}
            className="bg-white text-black px-8 py-4 rounded-lg font-medium hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <span>{loading ? <Loader2 className="animate-spin" /> : <ArrowRight />}</span>
            {loading ? t.analyzingBtn : t.analyzeBtn}
          </button>
        </div>

        {/* Status Indicator */}
        {loading && (
          <div className="mt-6 text-center space-y-2">
            <div className="text-purple-400 font-medium animate-pulse">{status}</div>
            <p className="text-xs text-gray-500">{t.waitMessage}</p>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-200 text-center">
            {error}
          </div>
        )}
      </div>

      {/* Report Section */}
      {report && (
        <div className="w-full animate-in fade-in slide-in-from-bottom-20 duration-1000">
          <ReportViewer report={report} />
        </div>
      )}
    </main>
  );
}
