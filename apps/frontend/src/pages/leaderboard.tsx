import { DataTable } from '@/components/data-table';
import { useManualServerSentEventsForRecent } from '@/hook/useManualServerSentEventsForRecent';
import fetchData from '@/utils/fetchData';
import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';
import { leaderboardColumns, LeaderboardRow } from '@/components/columns';

export default function Leaderboard() {
    const router = useRouter();
    const [symbolsForDropdown, setSymbolsForDropdown] = useState([]);
    const [tableMessage, setTableMessage] = useState([]);

    let access_token: string | null | undefined;
    if (typeof window !== 'undefined') {
        access_token = window.localStorage.getItem('access_token');
    }

    useEffect(() => {
      const fetchDataOrRedirect = async () => {
    
        const response = await fetchData(`${process.env.NEXT_PUBLIC_BACKEND_URL}/symbols`, 'GET', {}, access_token);
  
        if (!response.ok) {
          router.push('/');
        }

      };
    
      fetchDataOrRedirect();
    }, []);
  
    const {
      messages,
      startFetching,
      stopFetching
    } = useManualServerSentEventsForRecent(`${process.env.NEXT_PUBLIC_BACKEND_URL}/leaderboard_stream`, {}, access_token ?? undefined);

    useEffect(() => {
      console.log(messages);
    }, [messages]);

    // Render the order book data
    return (
      <div className="m-6">
        <div>
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
          </div>

          <div className="container mx-auto py-10 -full justify-center items-center">
            <div className="w-1/2">
              <DataTable 
                columns={leaderboardColumns} 
                data={messages as unknown as LeaderboardRow[]} 
              />
            </div>
          </div>

      </div>
        
    );
};