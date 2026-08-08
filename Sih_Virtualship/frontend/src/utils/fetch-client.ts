const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export interface FetchOptions extends RequestInit {
  timeout?: number;
}

export class FetchError extends Error {
  status: number;
  statusText: string;
  data: any;
  url: string;

  constructor(status: number, statusText: string, data: any, url: string, message?: string) {
    super(message || `HTTP Error ${status}: ${statusText} on request to ${url}`);
    this.name = 'FetchError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
    this.url = url;
  }
}

async function request<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { timeout = 10000, headers, ...restOptions } = options;

  // Setup AbortController for timeouts
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  const defaultHeaders = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...restOptions,
      headers: {
        ...defaultHeaders,
        ...headers,
      },
      signal: controller.signal,
    });
  } catch (error: any) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error(`[Timeout] Request to ${url} timed out after ${timeout}ms`);
    }
    
    // Enhance standard fetch TypeError ("Failed to fetch")
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new Error(
        `[Network Error] Failed to connect to ${url}. This indicates that the backend server is not running (ECONNREFUSED) or the request was blocked by CORS policies.`
      );
    }
    
    throw new Error(`[Request Error] Failed request to ${url}: ${error.message}`);
  }

  clearTimeout(timeoutId);

  let data: any = null;
  try {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch (parseError: any) {
    throw new Error(`[JSON Parsing Error] Failed to parse response from ${url}: ${parseError.message}`);
  }

  if (!response.ok) {
    throw new FetchError(
      response.status,
      response.statusText,
      data,
      url,
      data?.detail || `[HTTP ${response.status}] Request to ${url} failed: ${response.statusText}`
    );
  }

  return data as T;
}

export const fetchClient = {
  get: <T>(path: string, options?: FetchOptions) =>
    request<T>(path, { ...options, method: 'GET' }),
    
  post: <T>(path: string, body?: any, options?: FetchOptions) =>
    request<T>(path, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
    
  delete: <T>(path: string, body?: any, options?: FetchOptions) =>
    request<T>(path, {
      ...options,
      method: 'DELETE',
      body: body ? JSON.stringify(body) : undefined,
    }),
};
