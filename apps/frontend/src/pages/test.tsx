import fetchData from '@/utils/fetchData';
import React, { useEffect, useMemo } from 'react';
import { useRouter } from 'next/router';
import { useManualServerSentEvents } from '@/hook/useManualServerSentEvents';

export default function Test() {
  const router = useRouter();

  let access_token: string | null | undefined;
  if (typeof window !== 'undefined') {
      access_token = window.localStorage.getItem('access_token');
  }

  useEffect(() => {
    const fetchDataAndRedirect = async () => {
  
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


  const {
    messages,
    startFetching,
    stopFetching
  } = useManualServerSentEvents('http://localhost:8000/stream', {topics: ['etc', 'market']}, access_token ?? undefined);

  const fetchTopics = async () => {
    const response = await fetchData('http://localhost:8000/topics', 'GET', {}, access_token ?? undefined);
    const data = await response.json();
    console.log(data);
  };


  // Combine messages and replace '\n\n' with HTML line break '<br /><br />'
  const combinedMessages = useMemo(() => {
    return messages.join('').replace(/\n\n/g, '<br /><br />');
  }, [messages]);


  useEffect(() => {
    console.log("msgs", messages);
  }, [messages]);
  
  useEffect(() => {
    console.log("combined", combinedMessages);
}, [combinedMessages]);

  return (
    <div>
      <h1>This is a Test Page</h1>
      <button 
        onClick={startFetching} 
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Fetch Stream
      </button>
      <button 
        onClick={stopFetching} 
        className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded ml-4"
      >
        Stop Fetching Stream
      </button>
      <button 
        onClick={fetchTopics} 
        className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded ml-4"
      >
        Fetch Topics
      </button>
      <div className="mt-4 p-2 bg-gray-100 rounded shadow" dangerouslySetInnerHTML={{__html: combinedMessages}}/>
    </div>
  );
};