import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { fetchApi } from '../api/client';

export default function DocumentView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Fetch Extracted Text
  const { data: textData, isLoading: textLoading } = useQuery({
    queryKey: ['text', id],
    queryFn: () => fetchApi(`/documents/${id}/extracted-text`),
    retry: false,
  });

  // Fetch Entities
  const { data: entities, isLoading: entitiesLoading } = useQuery({
    queryKey: ['entities', id],
    queryFn: () => fetchApi(`/documents/${id}/entities`),
    retry: false,
  });

  const getEntityColor = (type: string) => {
    switch(type) {
      case 'organization': return 'bg-blue-900 text-blue-300 border-blue-700';
      case 'amount': return 'bg-green-900 text-green-300 border-green-700';
      case 'date': return 'bg-purple-900 text-purple-300 border-purple-700';
      case 'email': return 'bg-yellow-900 text-yellow-300 border-yellow-700';
      default: return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      <nav className="bg-slate-800 border-b border-slate-700 p-4 flex items-center gap-4">
        <button onClick={() => navigate('/dashboard')} className="text-blue-400 hover:text-blue-300 font-bold">
          ← Back to Dashboard
        </button>
        <h1 className="text-xl font-bold text-slate-300">Document Analysis</h1>
      </nav>

      <div className="p-8 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Extracted Text */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold text-white">Extracted Text</h2>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 h-[600px] overflow-y-auto">
            {textLoading ? (
              <p className="text-slate-400">Loading text...</p>
            ) : textData ? (
              <pre className="whitespace-pre-wrap font-mono text-sm text-slate-300">
                {textData.content}
              </pre>
            ) : (
              <p className="text-red-400">Text not extracted yet or extraction failed.</p>
            )}
          </div>
        </div>

        {/* Right Column: Extracted Entities */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Extracted Entities</h2>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
            {entitiesLoading ? (
              <p className="text-slate-400">Loading entities...</p>
            ) : entities && entities.length > 0 ? (
              <ul className="space-y-4">
                {entities.map((entity: any) => (
                  <li key={entity.id} className={`p-3 rounded border ${getEntityColor(entity.type)}`}>
                    <div className="text-xs uppercase tracking-wider font-bold opacity-75 mb-1">
                      {entity.type}
                    </div>
                    <div className="text-lg font-medium">{entity.value}</div>
                    <div className="text-xs opacity-50 mt-1">
                      Confidence: {(entity.confidence * 100).toFixed(0)}%
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-slate-400">No entities found.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}