'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import CodeBlock from './CodeBlock';

interface ReportViewerProps {
    report: string;
}

/**
 * 报告查看器组件
 * 使用ReactMarkdown渲染Markdown内容，并为代码块提供自定义渲染
 */
export default function ReportViewer({ report }: ReportViewerProps) {
    return (
        <div className="w-full max-w-4xl mx-auto p-8 glass-card rounded-2xl shadow-2xl animate-in fade-in duration-700">
            <div className="markdown-body">
                <ReactMarkdown
                    components={{
                        // 自定义代码块渲染，使用CodeBlock组件支持JSON复制功能
                        code: ({ className, children, ...props }: any) => {
                            const inline = !className;
                            return inline ? (
                                <code className={className} {...props}>
                                    {children}
                                </code>
                            ) : (
                                <CodeBlock className={className}>
                                    {children}
                                </CodeBlock>
                            );
                        },
                    }}
                >
                    {report}
                </ReactMarkdown>
            </div>
        </div>
    );
}
