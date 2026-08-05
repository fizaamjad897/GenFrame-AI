// Base URL for the GenFrame-AI FastAPI backend.
//
// - iOS simulator: http://localhost:8000/api works.
// - Android emulator: use http://10.0.2.2:8000/api (localhost on the host machine).
// - Physical device (Expo Go): use your machine's LAN IP, e.g. http://192.168.1.23:8000/api.
//
// Set EXPO_PUBLIC_API_BASE_URL in mobile/.env to override without touching code.
export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL || 'http://10.0.2.2:8000/api';
