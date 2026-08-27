import ReactMarkdown from "react-markdown";

export default function Markdown({ children, className = "" }) {
  if (!children) return null;

  return (
    <ReactMarkdown
      className={className}
      components={{
        p: ({ children: c }) => <p className="mb-3 last:mb-0 leading-relaxed">{c}</p>,
        ul: ({ children: c }) => <ul className="list-disc pl-5 mb-3 space-y-1">{c}</ul>,
        ol: ({ children: c }) => <ol className="list-decimal pl-5 mb-3 space-y-1">{c}</ol>,
        li: ({ children: c }) => <li className="leading-relaxed">{c}</li>,
        strong: ({ children: c }) => <strong className="font-semibold text-foreground">{c}</strong>,
        h1: ({ children: c }) => <h1 className="text-lg font-semibold mt-4 mb-2">{c}</h1>,
        h2: ({ children: c }) => <h2 className="text-base font-semibold mt-4 mb-2">{c}</h2>,
        h3: ({ children: c }) => <h3 className="text-sm font-semibold mt-3 mb-1">{c}</h3>,
      }}
    >
      {String(children)}
    </ReactMarkdown>
  );
}
