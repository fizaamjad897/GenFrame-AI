/**
 * Centralized API client for backend communication
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

export interface ApiError {
    message: string;
    status: number;
    detail?: string;
}

export class ApiException extends Error {
    status: number;
    detail?: string;

    constructor(message: string, status: number, detail?: string) {
        super(message);
        this.status = status;
        this.detail = detail;
        this.name = 'ApiException';
    }
}

export async function apiFetch<T>(
    path: string,
    opts: RequestInit & { token?: string } = {}
): Promise<T> {
    const { token, headers, ...rest } = opts;

    const finalHeaders: Record<string, string> = {
        ...(headers as Record<string, string> || {}),
    };

    // Add Authorization header if token is provided
    if (token) {
        finalHeaders['Authorization'] = `Bearer ${token}`;
    }

    // Add Content-Type for JSON requests (unless it's FormData)
    if (rest.body && !(rest.body instanceof FormData)) {
        finalHeaders['Content-Type'] = 'application/json';
    }

    try {
        const res = await fetch(`${API_BASE}${path}`, {
            ...rest,
            headers: finalHeaders,
        });

        // Handle non-OK responses
        if (!res.ok) {
            let errorMessage = `Request failed (${res.status})`;
            let errorDetail: string | undefined;

            try {
                const data = await res.json();
                errorDetail = data?.detail || data?.message;
                errorMessage = errorDetail || errorMessage;
            } catch {
                // If response is not JSON, use status text
                errorMessage = res.statusText || errorMessage;
            }

            throw new ApiException(errorMessage, res.status, errorDetail);
        }

        // Handle empty responses
        const contentType = res.headers.get('content-type');
        if (!contentType || res.status === 204) {
            return {} as T;
        }

        // Parse JSON response
        if (contentType.includes('application/json')) {
            return (await res.json()) as T;
        }

        // Return text for non-JSON responses
        return (await res.text()) as unknown as T;
    } catch (error) {
        if (error instanceof ApiException) {
            throw error;
        }

        // Network errors or other exceptions
        throw new ApiException(
            error instanceof Error ? error.message : 'Network error',
            0
        );
    }
}

/**
 * Get authentication token from localStorage
 */
export function getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
}

/**
 * Authenticated API fetch - automatically includes token
 */
export async function authFetch<T>(
    path: string,
    opts: RequestInit = {}
): Promise<T> {
    const token = getAuthToken();
    if (!token) {
        throw new ApiException('Not authenticated', 401);
    }

    return apiFetch<T>(path, { ...opts, token });
}
