import fetchData from '@/utils/fetchData';
import Select from 'react-select';
import React, { useEffect, useMemo, useState } from 'react';
import makeAnimated from 'react-select/animated';

import { useRouter } from 'next/router';
import { useManualServerSentEvents } from '@/hook/useManualServerSentEvents';
import { Input } from '@/components/ui/input';
import { DataTable } from '@/components/data-table';
import { Transaction, transactionColumns } from '@/components/columns';

const animatedComponents = makeAnimated();


const dirOptions = [
  { value: 'BUY', label: 'BUY' },
  { value: 'SELL', label: 'SELL' },
];

export default function MainPage() {
  const router = useRouter();
  const [symbols, setSymbols] = useState([]);
  const [symbolsForDropdown, setSymbolsForDropdown] = useState([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Request making
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [direction, setDirection] = useState(dirOptions[0].value);
  const [price, setPrice] = useState('');
  const [shares, setShares] = useState('');

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
      const symbolsForDropdown = data.symbols.map((symbol: string) => ({
        value: symbol,
        label: symbol.toUpperCase(),
      }));
      setSymbols(data.symbols);
      setSymbolsForDropdown(symbolsForDropdown);
    };
  
    fetchDataOrRedirect();
  }, []);

  const makeRequest = async () => {

    const body = {
      symbol: selectedSymbol,
      dir: direction,
      price: parseFloat(price).toFixed(2),
      shares: parseInt(shares)
      // Include other parameters as needed
    }

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

  async function handleFileUpload(event:  React.ChangeEvent<HTMLInputElement> ) {
    const file = event.target.files && event.target.files[0];
    setSelectedFile(file);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
  
    if (selectedFile) {
      const formData = new FormData();
      formData.append('file', selectedFile);

      console.log(`File: ${selectedFile.name}`);

      const response = await fetchData(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/run_code`,
        'POST',
        formData,
        access_token,
        'multipart/form-data'
      );

      console.log(response);

      if (!response.ok) {
        console.error('Error:', response.statusText);
        return;
      }
  
      const data = await response.json();
      console.log(data);
    }
  }
  
  const {
    messages,
    startFetching,
    stopFetching
  } = useManualServerSentEvents(`${process.env.NEXT_PUBLIC_BACKEND_URL}/kafka_stream`, {symbols: symbols}, access_token ?? undefined);

  // DEBUG
  const handleButtonClick = () => {
    setSelectedSymbol('AAPL');
  };

  const handleDirectionButtonClick = () => {
    setDirection(prevDirection => prevDirection === 'BUY' ? 'SELL' : 'BUY');
  };

  return (
    <div className='m-6'>
      <div className="my-6">

        {/* FOR TESTING */}
        <button 
          id="set-symbol-aapl"
          onClick={handleButtonClick} 
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
        >
          Set Symbol to AAPL
        </button>

        <button 
          id="toggle-direction"
          onClick={handleDirectionButtonClick} 
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded ml-4"
        >
          Toggle Direction from {direction}
        </button>

        {/* MAKE REQUEST */}
        <Select
          id="symbols-selector"
          components={animatedComponents}
          name="symbols"
          options={symbolsForDropdown}
          className="basic-multi-select my-4"
          classNamePrefix="select"
          onChange={(newValue: any) => setSelectedSymbol(newValue.value)}
        />
        
        <Select
          id="direction-selector"
          components={animatedComponents}
          name="direction"
          options={dirOptions}
          className="basic-single"
          classNamePrefix="select"
          onChange={(selectedOption: any) => setDirection(selectedOption!.value)}
        />

        <Input 
          id="price"
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
        
        <Input 
          id="shares"
          type="text" 
          placeholder="# of Shares" 
          className='my-4'
          value={shares}
          onChange={(event) => {
            const newShares = event.target.value;
            if (newShares === '' || /^[0-9]+$/.test(newShares)) {
              setShares(newShares);
            }
          }}
        />

        <button 
          id="make-request"
          onClick={makeRequest} 
          className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Make Request
        </button>

      </div>

      {/* CODE UPLOAD */}
      <form onSubmit={handleSubmit}>
        <div className="my-4">
          <label 
            htmlFor="python-file"
            className="block text-sm font-medium text-gray-700"
          >
            Upload Python File
          </label>
          
          <div className="mt-1 flex rounded-md shadow-sm">
            <input 
              id="python-file"
              type="file" 
              accept=".py"
              onChange={handleFileUpload}
              className="hidden" // Hide the default file input
            />
            <label 
              htmlFor="python-file" 
              className="focus:ring-indigo-500 focus:border-indigo-500 flex-grow sm:text-sm sm:leading-5 py-2 px-3 rounded-md shadow-sm cursor-pointer"
            >
              Choose File
            </label>
          </div>
        </div>

        <button type="submit">Upload</button>
      </form>

      {/* MARKET VIEW */}
      <Select
        // closeMenuOnSelect={false}
        components={animatedComponents}
        isMulti
        name="topics"
        options={symbolsForDropdown}
        className="basic-multi-select2 my-4"
        classNamePrefix="select"
        onChange={(newValue: any) => {
          const values = newValue.map((item: any) => item.value);
          setSelectedViewSymbols(values);
        }}
      />

      <button 
        id="start-fetching-kafka"
        onClick={startFetching} 
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Fetch Stream
      </button>
      <button 
        id="stop-fetching-kafka"
        onClick={stopFetching} 
        className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded ml-4"
      >
        Stop Fetching Stream
      </button>

      <div className="container mx-auto py-10">
        <DataTable columns={transactionColumns} data={messages as unknown as Transaction[]} />
      </div>

      {/* <div className="mt-4 p-2 bg-gray-100 rounded shadow" dangerouslySetInnerHTML={{__html: combinedMessages}}/> */}
    </div>
  );
};