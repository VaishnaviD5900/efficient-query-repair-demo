import React from 'react';

interface Props {
  data: string[][];
}

export default function DatasetPreview({ data }: Props) {
  return (
    <div className="overflow-x-auto border rounded">
      <table className="table-auto text-sm border-collapse w-full">
        <thead>
          <tr>
            {data[0].map((header, i) => (
              <th key={i} className="border px-2 py-1 bg-gray-100">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(1, 6).map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, colIndex) => (
                <td key={colIndex} className="border px-2 py-1">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-gray-500 mt-1">Showing first 5 rows</p>
    </div>
  );
}
