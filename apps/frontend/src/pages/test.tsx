import fetchData from '@/utils/fetchData';
import Select from 'react-select';
import React, { useEffect, useMemo, useState } from 'react';
import makeAnimated from 'react-select/animated';

import { useRouter } from 'next/router';
import { useManualServerSentEvents } from '@/hook/useManualServerSentEvents';
import { Input } from '@/components/ui/input';

const animatedComponents = makeAnimated();


const dirOptions = [
  { value: 'BUY', label: 'BUY' },
  { value: 'SELL', label: 'SELL' },
];

export default function Test() {
  const router = useRouter();

  // Request making
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setselectedSymbol] = useState([]);
  const [direction, setDirection] = useState(dirOptions[0].value);
  const [price, setPrice] = useState('');

  // Market viewing
  const [selectedViewSymbols, setSelectedViewSymbols] = useState([]);

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
      const symbols = data.symbols.map((symbol: string) => ({
        value: symbol,
        label: symbol.toUpperCase(),
      }));
      setSymbols(symbols);
      
    };
  
    fetchDataOrRedirect();
  }, []);

  const makeRequest = async () => {

    const body = {
      symbol: selectedSymbol,
      dir: direction,
      price: parseFloat(price).toFixed(2)
      // Include other parameters as needed
    }
    console.log(`Formatted price type: ${typeof body['price']}`);

    const response = await fetchData(`${process.env.NEXT_PUBLIC_BACKEND_URL}/market_request`,'POST', body, access_token, 'application/json');
  
    if (!response.ok) {
      // Handle error
      console.error('Error:', response.statusText);
      return;
    }
  
    const data = await response.json();
    // Handle the response data
    console.log(data);
  };
  
  const {
    messages,
    startFetching,
    stopFetching
  } = useManualServerSentEvents(`${process.env.NEXT_PUBLIC_BACKEND_URL}/stream`, {topics: ['etc', 'market']}, access_token ?? undefined);

  // Combine messages and replace '\n\n' with HTML line break '<br /><br />'
  const combinedMessages = useMemo(() => {
    return messages.join('').replace(/\n\n/g, '<br /><br />');
  }, [messages]);

  return (
    <div>
      <div className="my-6">
        <Select
          components={animatedComponents}
          name="topics"
          options={symbols}
          className="basic-multi-select my-4"
          classNamePrefix="select"
          onChange={(newValue: any) => setselectedSymbol(newValue.value)}
        />
        
        <Select
          name="direction"
          options={dirOptions}
          className="basic-single"
          classNamePrefix="select"
          onChange={(selectedOption) => setDirection(selectedOption!.value)}
        />

        <Input 
          type="text" 
          placeholder="Price" 
          className='my-4'
          value={price}
          onChange={(event) => {
            const newPrice = event.target.value;
            if (newPrice === '' || /^[0-9]*(\.[0-9]{0,2})?$/.test(newPrice)) {
              setPrice(newPrice);
            }
          }}
        />

        <button 
          onClick={makeRequest} 
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Make Request
        </button>

      </div>

      <Select
        // closeMenuOnSelect={false}
        components={animatedComponents}
        isMulti
        name="topics"
        options={symbols}
        className="basic-multi-select2 my-4"
        classNamePrefix="select"
        onChange={(newValue: any) => {
          const values = newValue.map((item: any) => item.value);
          setSelectedViewSymbols(values);
        }}
      />

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
      <div className="mt-4 p-2 bg-gray-100 rounded shadow" dangerouslySetInnerHTML={{__html: combinedMessages}}/>
    </div>
  );
};