import { apiClient } from './client';
import { User } from '../types/models';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/users/login', { email, password });
  return data;
}

export async function register(
  email: string,
  password: string,
  fullName?: string
): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/users/register', {
    email,
    password,
    fullName,
  });
  return data;
}

export async function requestPasswordReset(email: string): Promise<void> {
  await apiClient.post('/users/request-password-reset', { email });
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  await apiClient.post('/users/reset-password', { token, newPassword });
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>('/users/me');
  return data;
}
