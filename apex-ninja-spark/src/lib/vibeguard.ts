export const secureFetch = async (url: string, options?: RequestInit): Promise<Response> => {
  const secureOptions = {
    ...options,
    headers: {
      ...options?.headers,
      'X-VibeGuard': '1'
    }
  };

  return fetch(url, secureOptions);
};
