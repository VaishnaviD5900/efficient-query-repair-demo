// src/pages/QueryEditor.tsx
import React, { useState } from 'react';
import DatasetUploader from '../components/DatasetUploader';
import DatasetPreview from '../components/DatasetPreview';
import QueryInputForm from '../components/QueryInputForm';
import ConstraintForm from '../components/ConstraintForm';
import RepairRunButton from '../components/RepairRunButton';

export default function QueryEditor() {
  const [query, setQuery] = useState('SELECT * FROM uploaded;');
  const [constraint, setConstraint] = useState('');
  const [csvData, setCsvData] = useState<string[][] | null>(null);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Upload Dataset & Write Query</h1>

      <DatasetUploader onUpload={setCsvData} />
      {csvData && <DatasetPreview data={csvData} />}

      <QueryInputForm query={query} setQuery={setQuery} />
      <ConstraintForm constraint={constraint} setConstraint={setConstraint} />

      <RepairRunButton query={query} constraint={constraint} csvData={csvData} />
    </div>
  );
}
