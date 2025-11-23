'use client';

import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

interface CodeBlockProps {
    children?: React.ReactNode;
    className?: string;
}

/**
 * 自定义代码块组件，为JSON代码块添加一键复制功能
 * 当用户点击复制按钮时，会复制代码内容并显示"JSON已复制"提示
 */
export default function CodeBlock({ children, className }: CodeBlockProps) {
    const { t } = useLanguage();
    const [copied, setCopied] = useState(false);

    // 从 className 中提取语言类型（例如 "language-json"）
    const language = className?.replace('language-', '') || '';
    const isJson = language.toLowerCase() === 'json';

    // 获取代码文本内容
    const getCodeText = () => {
        if (typeof children === 'string') {
            return children;
        }
        if (React.isValidElement(children) && (children.props as any).children) {
            return String((children.props as any).children);
        }
        return String(children);
    };

    /**
     * 复制代码到剪贴板
     * 复制成功后显示"JSON已复制"提示，2秒后恢复原状
     */
    const handleCopy = async () => {
        const codeText = getCodeText();
        try {
            await navigator.clipboard.writeText(codeText);
            setCopied(true);
            // 2秒后恢复复制按钮状态
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('复制失败:', err);
        }
    };

    return (
        <div className="relative group">
            <pre className={`${className} relative`}>
                <code className={className}>{children}</code>
            </pre>
            {/* 只为JSON代码块显示复制按钮 */}
            {isJson && (
                <button
                    onClick={handleCopy}
                    className="absolute top-3 right-3 p-2 rounded-lg bg-gray-800/80 hover:bg-gray-700/90 border border-gray-600/50 transition-all opacity-0 group-hover:opacity-100 flex items-center gap-2 text-sm"
                    title={t.copy}
                >
                    {copied ? (
                        <>
                            <Check size={16} className="text-green-400" />
                            <span className="text-green-400 font-medium">{t.copied}</span>
                        </>
                    ) : (
                        <>
                            <Copy size={16} className="text-gray-300" />
                            <span className="text-gray-300">{t.copy}</span>
                        </>
                    )}
                </button>
            )}
        </div>
    );
}
