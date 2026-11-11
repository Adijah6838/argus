import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, Link } from 'react-router-dom';
import { fetchApi, removeToken } from '../api/client';

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => fetchApi('/documents/'),
    refetchInterval: 3000,
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return fetchApi('/documents/upload', { method: 'POST', body: formData });
    },
    onSuccess: () => {
      setFile(null);
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      alert('✅ File uploaded and queued for processing!');
    },
    onError: (err: any) => alert(`❌ Upload failed: ${err.message}`)
  });

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      <nav className="bg-slate-800 border-b border-slate-700 p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-blue-500">ARGUS</h1>
        <div className="flex gap-4">
          <Link to="/compare" className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded text-sm font-bold text-white">
            Compare Documents
          </Link>
          <button onClick={() => { removeToken(); navigate('/'); }} className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-sm font-bold text-white">
            Logout
          </button>
        </div>
      </nav>

      <div className="p-8 max-w-7xl mx-auto">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-8 flex items-center gap-4">
          <div className="flex-1">
            <h2 className="text-lg font-semibold mb-2">Upload Document</h2>
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700" />
          </div>
          <button onClick={() => file && uploadMutation.mutate(file)} disabled={!file || uploadMutation.isPending} className={`px-6 py-3 rounded font-bold ${!file ? 'bg-slate-600 text-slate-400' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}>
            {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
          </button>
        </div>

        <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900 text-slate-400 text-sm">
                <th className="p-4 font-medium">Filename</th>
                <th className="p-4 font-medium">Status</th>
                <th className="p-4 font-medium">Size</th>
                <th className="p-4 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {documents?.map((doc: any) => (
                <tr key={doc.id} className="hover:bg-slate-750">
                  <td className="p-4 text-sm">{doc.original_filename}</td>
                  <td className="p-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${doc.status === 'COMPLETED' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="p-4 text-sm">{(doc.file_size / 1024).toFixed(1)} KB</td>
                  <td className="p-4 text-sm">
                    <Link to={`/document/${doc.id}`} className="text-blue-400 hover:text-blue-300 font-medium">View Data</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}