import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setToken } from '../api/client';

export default function Login() {
  const [email, setEmail] = useState('admin@argus.com');
  const [password, setPassword] = useState('securepassword123');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isRegistering) {
        const res = await fetch('http://localhost:8000/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: 'ARGUS User' }),
        });
        if (!res.ok) throw new Error('Registration failed. Email might exist.');
      }

      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });
      
      const data = await res.json();
      if (res.ok) {
        setToken(data.access_token);
        navigate('/dashboard');
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="bg-slate-800 p-8 rounded-lg shadow-xl w-full max-w-md border border-slate-700">
        <h1 className="text-3xl font-bold text-blue-500 mb-2 text-center">ARGUS</h1>
        <p className="text-slate-400 text-center mb-6">Document Intelligence Platform</p>
        
        {error && <div className="bg-red-900 text-red-200 p-3 rounded mb-4 text-sm">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-200"
          >
            {isRegistering ? 'Register & Login' : 'Sign In'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button 
            type="button" 
            onClick={() => setIsRegistering(!isRegistering)} 
            className="text-sm text-blue-400 hover:underline"
          >
            {isRegistering ? 'Already have an account? Sign in' : 'Need an account? Register here'}
          </button>
        </div>
      </div>
    </div>
  );
}