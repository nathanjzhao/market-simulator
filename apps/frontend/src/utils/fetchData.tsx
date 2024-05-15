async function fetchData(url: string, method: string, data: Record<string, unknown>, token?: string | null, contentType: string = 'application/x-www-form-urlencoded') {
  const headers: Record<string, string> = {
    'Content-Type': contentType
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let body;
  let finalUrl = url;

  if (method === 'GET') {
    // Create a new URLSearchParams object
    const params = new URLSearchParams();

    // Iterate over data
    for (const key in data) {
      const value = data[key];

      // If value is an array, append each item as a separate key-value pair
      if (Array.isArray(value)) {
        for (const item of value) {
          params.append(key, item.toString());
        }
      } else {
        params.append(key, (value as string).toString());
      }
    }

    finalUrl = `${url}?${params.toString()}`;
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