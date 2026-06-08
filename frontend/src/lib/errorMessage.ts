export function extractApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong.",
): string {
  if (!error) return fallback;

  const err = error as any;

  const candidates = [
    err?.detail,
    err?.message,
    err?.error,
    err?.data?.detail,
    err?.data?.message,
    err?.response?.data?.detail,
    err?.response?.data?.message,
    err?.response?.statusText,
  ];

  for (const value of candidates) {
    if (!value) continue;

    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }

    if (Array.isArray(value) && value.length > 0) {
      const first = value[0];
      if (typeof first === "string" && first.trim()) {
        return first.trim();
      }
      if (typeof first?.msg === "string" && first.msg.trim()) {
        return first.msg.trim();
      }
      if (typeof first?.message === "string" && first.message.trim()) {
        return first.message.trim();
      }
    }
  }

  if (typeof err?.toString === "function") {
    const text = err.toString();
    if (typeof text === "string" && text !== "[object Object]") {
      return text;
    }
  }

  return fallback;
}
