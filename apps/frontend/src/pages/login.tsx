import fetchData from '@/utils/fetchData';
import { useRouter } from 'next/router';
import { useState } from 'react';

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const login = async (event: { preventDefault: () => void; }) => {
    event.preventDefault();

    const body = {
      username: username,
      password: password
    };

    const response = await fetchData(`${process.env.NEXT_PUBLIC_BACKEND_URL}/login`, 'POST', body);

    const data = await response.json();

    if (response.ok && data.access_token) {
      // Store the access token in local storage
      localStorage.setItem('access_token', data.access_token);

      console.log('Login successful', data);
      router.push('/test');
    } else {
      // Registration failed
      console.log('Login failed', data);
    }
  };

  return (
    <main>
      <form onSubmit={login}>
        <label>
          Username:
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          Password:
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit">Login</button>
      </form>
    </main>
  );
}