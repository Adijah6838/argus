import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { fetchApi } from '../api/client';

export default function Compare() {
  const [docA, setDocA] = useState('');
  const [docB, setDocB] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Fetch documents for the dropdowns
  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: () => fetchApi('/documents/'),
  });

  const handleCompare = async () => {
    if (!docA || !docB) return alert('Please select two documents.');
    if (docA === docB) return alert('Please select two different documents.');
    
    setLoading(true);
    setResult(null);
    try {
      const res = await fetchApi(`/documents/compare/${docA}/${docB}`);
      setResult(res);
    } catch (err: any) {
      alert(`Comparison failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      <nav className="bg-slate-800 border-b border-slate-700 p-4 flex items-center gap-4">
        <button onClick={() => navigate('/dashboard')} className="text-blue-400 hover:text-blue-300 font-bold">
          ← Back to Dashboard
        </button>
        <h1 className="text-xl font-bold text-slate-300">Compare Documents</h1>
      </nav>

      <div className="p-8 max-w-5xl mx-auto">
        {/* Selection Panel */}
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 flex gap-4 items-end mb-8">
          <div className="flex-1">
            <label className="block text-sm text-slate-400 mb-2">Document A</label>
            <select 
              onChange={(e) => setDocA(e.target.value)}
              className="w-full p-3 bg-slate-900 border border-slate-600 rounded text-white"
            >
              <option value="">Select Document A...</option>
              {documents?.map((d: any) => (
                <option key={d.id} value={d.id}>{d.original_filename}</option>
              ))}
            </select>
          </div>
          
          <div className="pb-3 text-slate-500 font-bold">VS</div>

          <div className="flex-1">
            <label className="block text-sm text-slate-400 mb-2">Document B</label>
            <select 
              onChange={(e) => setDocB(e.target.value)}
              className="w-full p-3 bg-slate-900 border border-slate-600 rounded text-white"
            >
              <option value="">Select Document B...</option>
              {documents?.map((d: any) => (
                <option key={d.id} value={d.id}>{d.original_filename}</option>
              ))}
            </select>
          </div>

          <button 
            onClick={handleCompare}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded h-[50px]"
          >
            {loading ? 'Comparing...' : 'Compare'}
          </button>
        </div>

        {/* Results Panel */}
        {result && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Comparison Results</h2>
              <div className={`px-4 py-2 rounded font-bold ${result.similarity_score > 80 ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                Similarity Score: {result.similarity_score}%
              </div>
            </div>

            {result.discrepancies_found === 0 ? (
              <p className="text-green-400">✅ No discrepancies found. The documents match.</p>
            ) : (
              <div className="space-y-4">
                <p className="text-red-400 font-semibold mb-4">⚠️ {result.discrepancies_found} Discrepanc(ies) Detected:</p>
                {result.details.map((disc: any, i: number) => (
                  <div key={i} className="bg-slate-900 p-4 rounded border border-red-900/50">
                    <div className="font-bold text-red-300 mb-2">{disc.field} Mismatch</div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-500 block">Document A</span>
                        <span className="text-white">{disc.doc_a_value}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Document B</span>
                        <span className="text-white">{disc.doc_b_value}</span>
                      </div>
                    </div>
                    <div className="mt-3 text-slate-400 text-sm border-t border-slate-700 pt-2">
                      <strong>Difference:</strong> {disc.difference} <br/>
                      <span className="text-slate-500">{disc.note}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}