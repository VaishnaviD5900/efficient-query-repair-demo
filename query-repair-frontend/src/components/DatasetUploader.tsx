import React from 'react';

interface Props {
  onUpload: (data: string[][]) => void;
}

export default function DatasetUploader({ onUpload }: Props) {
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const rows = text.trim().split('\n').map((row) => row.split(','));
      onUpload(rows);
    };
    reader.readAsText(file);
  };

  return (
    <div className="space-y-2">
      <label className="block font-medium">Upload CSV Dataset</label>
      <input type="file" accept=".csv" onChange={handleFileUpload} />
    </div>
  );
}
