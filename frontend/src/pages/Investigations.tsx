import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { fetchApi, getToken } from '../api/client';

export default function Investigations() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: investigations, isLoading } = useQuery({
    queryKey: ['investigations'],
    queryFn: () => fetchApi('/investigations/'),
  });

  const createMutation = useMutation({
    mutationFn: (newInv: any) => fetchApi('/investigations/', { method: 'POST', body: JSON.stringify(newInv) }),
    onSuccess: () => {
      setTitle('');
      setDescription('');
      queryClient.invalidateQueries({ queryKey: ['investigations'] });
      alert('✅ Investigation created successfully!');
    },
    onError: (err: any) => alert(`❌ Failed: ${err.message}`)
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) return;
    createMutation.mutate({ title, description });
  };

  const downloadReport = async (invId: string, format: 'pdf' | 'json') => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/investigations/${invId}/report/${format}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      if (!res.ok) throw new Error('Failed to generate report');
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${invId}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      <nav className="bg-slate-800 border-b border-slate-700 p-4 flex justify-between items-center">
        <div className="flex gap-6 items-center">
          <h1 className="text-2xl font-bold text-blue-500">ARGUS</h1>
          <button onClick={() => navigate('/dashboard')} className="text-sm text-slate-400 hover:text-white">Dashboard</button>
          <button onClick={() => navigate('/compare')} className="text-sm text-slate-400 hover:text-white">Compare</button>
          <span className="text-sm font-bold text-blue-400 border-b-2 border-blue-400 pb-1">Investigations</span>
        </div>
        <button onClick={() => { localStorage.removeItem('token'); navigate('/'); }} className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-sm font-bold text-white">
          Logout
        </button>
      </nav>

      <div className="p-8 max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 sticky top-8">
            <h2 className="text-xl font-bold mb-4 text-white">New Investigation</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Title</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full p-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:border-blue-500" placeholder="e.g., Q4 Invoice Audit" required />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Description</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="w-full p-2 bg-slate-900 border border-slate-600 rounded text-white h-24 focus:outline-none focus:border-blue-500" placeholder="What are you investigating?" />
              </div>
              <button type="submit" disabled={createMutation.isPending} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded">
                {createMutation.isPending ? 'Creating...' : 'Create Investigation'}
              </button>
            </form>
          </div>
        </div>

        <div className="md:col-span-2 space-y-4">
          <h2 className="text-xl font-bold mb-4 text-white">Active Investigations</h2>
          {isLoading ? (
            <p className="text-slate-400">Loading...</p>
          ) : investigations && investigations.length > 0 ? (
            investigations.map((inv: any) => (
              <div key={inv.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700 hover:border-blue-500 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-bold text-white">{inv.title}</h3>
                  <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-xs font-bold">{inv.status}</span>
                </div>
                <p className="text-slate-400 mb-4">{inv.description || 'No description provided.'}</p>
                
                <div className="flex justify-between items-center mt-4 border-t border-slate-700 pt-4">
                  <div className="text-xs text-slate-500">Created {new Date(inv.created_at).toLocaleDateString()}</div>
                  <div className="flex gap-2">
                    <button onClick={() => downloadReport(inv.id, 'json')} className="bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded text-xs font-bold text-white">JSON</button>
                    <button onClick={() => downloadReport(inv.id, 'pdf')} className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs font-bold text-white">PDF Report</button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-slate-800 p-8 rounded-lg border border-slate-700 text-center text-slate-500">
              No investigations yet. Create one to get started.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}