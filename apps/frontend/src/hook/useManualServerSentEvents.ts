import { useCallback, useEffect, useState } from 'react';

export const useManualServerSentEvents = (url: string, body: any, token?: string) => {
    const [messages, setMessages] = useState<string[]>([]);
    const [controller, setController] = useState<AbortController | null>(null);

    const startFetching = useCallback(() => {
        const newController = new AbortController();
        setController(newController);
        const signal = newController.signal;

        const fetchData = async () => {
            try {
                const headers: Record<string, string> = {
                  'Content-Type': 'application/json'
                };
              
                if (token) {
                  headers['Authorization'] = `Bearer ${token}`;
                }
            
                const response = await fetch(url, {
                    method: 'POST',
                    headers: headers,
                    signal,
                });

                if (response.body) {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) {
                            break;
                        }
                        const str = decoder.decode(value);
                        try {
                            // Adjusting for SSE format by stripping 'data: ' prefix and trimming any remaining whitespace
                            const jsonStr = str.replace(/^data: /, '').trim();
                            const newMessage = JSON.parse(jsonStr);
                            console.log(newMessage);  // Log the new message
                            setMessages((prevMessages) => [...prevMessages, newMessage]);
                            console.log("inside messages", messages);  // Log the new message
                        } catch (error) {
                            console.error("Error parsing message:", error);
                        }
                    }
                }
            } catch (error) {
              if ((error as Error).name === 'AbortError') {
                // Fetch was aborted
                console.log('Fetch aborted');
              } else {
                console.error("Fetch error:", error);
              }
            }
        };

        fetchData();
    }, [url, body, token]);

    const stopFetching = useCallback(() => {
        if (controller) {
            controller.abort();
            setController(null);
        }
    }, [controller]);

    // Cleanup on component unmount
    useEffect(() => {
        return () => {
            if (controller) {
                controller.abort();
            }
        };
    }, [controller]);

    return { messages, startFetching, stopFetching };
};