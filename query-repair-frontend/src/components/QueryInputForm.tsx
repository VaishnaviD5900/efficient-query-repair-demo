import React from 'react';
import Editor from '@monaco-editor/react';

interface Props {
  query: string;
  setQuery: (query: string) => void;
}

export default function QueryInputForm({ query, setQuery }: Props) {
  return (
    <div className="border rounded shadow">
      <Editor
        height="200px"
        defaultLanguage="sql"
        value={query}
        onChange={(val) => setQuery(val || '')}
        theme="vs-dark"
        options={{ fontSize: 14, minimap: { enabled: false } }}
      />
    </div>
  );
}
