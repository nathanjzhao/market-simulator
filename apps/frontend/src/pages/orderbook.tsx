import { DataTable } from '@/components/data-table';
import { useManualServerSentEventsForRecent } from '@/hook/useManualServerSentEventsForRecent';
import fetchData from '@/utils/fetchData';
import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';
import { orderbookColumns, OrderBookSymbol } from '@/components/columns';

export default function OrderBook() {
    const router = useRouter();
    const [symbols, setSymbols] = useState([]);
    const [symbolsForDropdown, setSymbolsForDropdown] = useState([]);

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
  
        const data = await response.json()
        const symbolsForDropdown = data.symbols.map((symbol: string) => ({
          value: symbol,
          label: symbol.toUpperCase(),
        }));
        setSymbols(data.symbols);
        setSymbolsForDropdown(symbolsForDropdown);
      };
    
      fetchDataOrRedirect();
    }, []);
  
    const {
      messages,
      startFetching,
      stopFetching
    } = useManualServerSentEventsForRecent(`${process.env.NEXT_PUBLIC_BACKEND_URL}/orderbook_stream`, {symbols: symbols}, access_token ?? undefined);

    // Render the order book data
    return (
      <div className="m-6">
        <div>
            <button 
              id="start-fetching-orderbook"
              onClick={startFetching} 
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Fetch Stream
            </button>
            <button 
              id="stop-fetching-orderbook"
              onClick={stopFetching} 
              className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded ml-4"
            >
              Stop Fetching Stream
            </button>
          </div>

          <div className="container mx-auto py-10 -full">
            {Object.entries(messages).map(([symbol, data ]) => (
              <div key={symbol}>
                <h1 className="text-4xl font-bold">{symbol}</h1>
                <div className="flex space-x-4 h-full">
                  <div className="w-1/2">
                    <h3>Asks</h3>
                    <DataTable columns={orderbookColumns} data={(data as any).Asks as unknown as OrderBookSymbol[]} />
                  </div>
                  <div className="w-1/2">
                    <h3>Bids</h3>
                    <DataTable columns={orderbookColumns} data={(data as any).Bids as unknown as OrderBookSymbol[]} />
                  </div>
                </div>
              </div>
            ))}
          </div>

      </div>
        
    );
};