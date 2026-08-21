import { EngineType, User } from '../types/models';

export function hasEngineActiveSubscription(user: User, engineType: EngineType): boolean {
  const engineData = user.engine_data?.[engineType];
  if (engineData?.credits) return true;
  return user.engineType === engineType && !!user.credits;
}

export function getRemainingCredits(user: User, engineType: EngineType): number {
  const selectedCredits =
    user.engine_data?.[engineType]?.credits ||
    (user.engineType === engineType ? (user.credits as any)?.[engineType] || user.credits : null);

  const credits = selectedCredits || {};
  const monthlyRemaining = Math.max(
    0,
    (credits.monthly_units_max || 0) - (credits.monthly_units_used || 0)
  );
  const addonRemaining = Math.max(
    0,
    (credits.addon_units_max || 0) - (credits.addon_units_used || 0)
  );
  return monthlyRemaining + addonRemaining;
}

export function isEngineAllocated(user: User, engineType: EngineType): boolean {
  const engines =
    user.available_engines && user.available_engines.length > 0
      ? user.available_engines
      : ['transformation', 'creation'];
  return engines.includes(engineType);
}
