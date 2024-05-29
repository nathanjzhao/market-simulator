async function fetchData(url: string, method: string, data: Record<string, unknown> | FormData, token?: string | null, contentType: string = 'application/x-www-form-urlencoded') {
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let body;
  let finalUrl = url;

  if (method !== 'GET') {
    if (data instanceof FormData) {
      body = data;
    } else if (contentType === 'application/json') {
      headers['Content-Type'] = contentType;
      body = JSON.stringify(data);
    } else {
      headers['Content-Type'] = contentType;
      body = new URLSearchParams(data as Record<string, string>).toString();
    }
  }
  console.log(headers);

  const response = await fetch(finalUrl, {
    method: method,
    headers: headers,
    body: body
  });

  return response;
}

export default fetchData;