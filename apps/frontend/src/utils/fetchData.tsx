async function fetchData(url: string, method: string, data: Record<string, unknown>) {
  const response = await fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams(data as Record<string, string>).toString()
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export default fetchData;