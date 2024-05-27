async function fetchData(url: string, method: string, data: Record<string, unknown> | FormData, token?: string | null, contentType: string = 'application/x-www-form-urlencoded') {
  const headers: Record<string, string> = {
    'Content-Type': contentType
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let body;
  let finalUrl = url;

  if (method === 'GET') {
    
  } else {
    if (headers['Content-Type'] === 'application/json') {
      body = JSON.stringify(data);
    } else {
      body = new URLSearchParams(data as Record<string, string>).toString();
    }
  }

  const response = await fetch(finalUrl, {
    method: method,
    headers: headers,
    body: body
  });

  return response;
}

export default fetchData;