import fetchData from '@/utils/fetchData';
import React, { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Test() {
  const router = useRouter();

  useEffect(() => {
    const fetchDataAndRedirect = async () => {
      const access_token = localStorage.getItem('access_token');
  
      if (!access_token) {
        router.push('/');
      } else {
        const response = await fetchData('http://localhost:8000/users/me', 'GET', {}, access_token);
        const data = await response.json();

        console.log(data);
      }
    };
  
    fetchDataAndRedirect();
  }, []);
  
  const fetchStream = async () => {
    const body = {
      topics: ['etc', 'market']
    }

    const access_token = localStorage.getItem('access_token');

    const response = await fetchData('http://localhost:8000/stream', 'GET', body, access_token ?? undefined);
    
    const reader = response?.body?.getReader();
    const decoder = new TextDecoder('utf-8');

    reader?.read().then(function processStream({ done, value }): Promise<void> | void {
      if (done) {
        console.log('Stream complete');
        return;
      }

      console.log(decoder.decode(value));

      return reader.read().then(processStream);
    });
  };

  const fetchTopics = async () => {
    const access_token = localStorage.getItem('access_token');

    const response = await fetchData('http://localhost:8000/topics', 'GET', {}, access_token ?? undefined);
    const data = await response.json();
    console.log(data);
  };

  return (
    <div>
      <h1>This is a Test Page</h1>
      <button 
        onClick={fetchStream} 
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Fetch Stream
      </button>
      <button 
        onClick={fetchTopics} 
        className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded ml-4"
      >
        Fetch Topics
      </button>
    </div>
  );
};