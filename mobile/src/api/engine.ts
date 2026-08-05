import { apiClient } from './client';
import { EngineType, HistoryItem, ResizeResult } from '../types/models';

export interface ResizeParams {
  engineType: EngineType;
  aspectRatio: string;
  prompt?: string;
  imageUri?: string | null;
}

export async function resizeImage({
  engineType,
  aspectRatio,
  prompt,
  imageUri,
}: ResizeParams): Promise<ResizeResult> {
  const formData = new FormData();
  formData.append('engine_type', engineType);
  formData.append('aspect_ratio', aspectRatio);
  if (prompt && prompt.trim()) {
    formData.append('prompt', prompt.trim());
  }
  if (imageUri) {
    const filename = imageUri.split('/').pop() || 'upload.jpg';
    const match = /\.(\w+)$/.exec(filename);
    const ext = match ? match[1].toLowerCase() : 'jpg';
    const mime = ext === 'png' ? 'image/png' : 'image/jpeg';
    // React Native FormData file shape — not a real Blob/File on native.
    formData.append('file', {
      uri: imageUri,
      name: filename,
      type: mime,
    } as unknown as Blob);
  }

  const { data } = await apiClient.post<ResizeResult>('/resize', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function fetchHistory(): Promise<HistoryItem[]> {
  const { data } = await apiClient.get<{ history: HistoryItem[] }>('/history');
  return data.history;
}
