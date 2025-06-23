import React from 'react';

interface Props {
  constraint: string;
  setConstraint: (value: string) => void;
}

export default function ConstraintForm({ constraint, setConstraint }: Props) {
  return (
    <div>
      <label className="block mb-2 text-sm font-medium text-gray-700">Aggregate Constraint</label>
      <input
        type="text"
        value={constraint}
        onChange={(e) => setConstraint(e.target.value)}
        placeholder="e.g., sum(salary) <= 100000"
        className="w-full border rounded px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
    </div>
  );
}
