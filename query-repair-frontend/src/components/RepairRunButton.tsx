import React from 'react';

interface Props {
  query: string;
  constraint: string;
  csvData: string[][] | null;
}

export default function RepairRunButton({ query, constraint, csvData }: Props) {
  const handleRun = () => {
    console.log('Query:', query);
    console.log('Constraint:', constraint);
    console.log('CSV Preview (first row):', csvData?.[0]);
    alert('Will send query + constraint + dataset to backend');
  };

  return (
    <button
      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow"
      onClick={handleRun}
    >
      Run Repair
    </button>
  );
}
