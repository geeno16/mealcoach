export const POST_NAME_MAX = 50;
export const POST_DESCRIPTION_MAX = 200;
export const MEAL_NAME_MAX = 50;
export const MIN_POST_MEALS = 1;
export const MAX_POST_MEALS = 3;

export const USER_NAME_MAX = 50;
export const USER_SURNAME_MAX = 50;

function lengthError(
  value: string,
  bounds: { min?: number; max?: number },
  label: string,
): string | null {
  if (bounds.min !== undefined && value.length < bounds.min) {
    return `${label}: не короче ${bounds.min} симв.`;
  }
  if (bounds.max !== undefined && value.length > bounds.max) {
    return `${label}: не длиннее ${bounds.max} симв.`;
  }
  return null;
}

function intRangeError(
  raw: string,
  bounds: { gt?: number; ge?: number; lt?: number; le?: number },
  label: string,
): string | null {
  if (raw.trim() === "") return null;
  const value = Number(raw);
  if (!Number.isInteger(value)) return `${label}: введите целое число`;

  const min =
    bounds.ge ?? (bounds.gt !== undefined ? bounds.gt + 1 : undefined);
  const max =
    bounds.le ?? (bounds.lt !== undefined ? bounds.lt - 1 : undefined);

  if (min !== undefined && value < min) return `${label}: не меньше ${min}`;
  if (max !== undefined && value > max) return `${label}: не больше ${max}`;
  return null;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(value: string, label = "Email"): string | null {
  return EMAIL_RE.test(value) ? null : `${label}: некорректный формат`;
}

export function validatePostName(value: string): string | null {
  return lengthError(value, { min: 1, max: POST_NAME_MAX }, "Название");
}

export function validatePostDescription(value: string): string | null {
  if (value === "") return null;
  return lengthError(value, { min: 1, max: POST_DESCRIPTION_MAX }, "Описание");
}

export function validateMealName(value: string): string | null {
  if (value === "") return null;
  return lengthError(value, { min: 1, max: MEAL_NAME_MAX }, "Название мила");
}

export function validateMealMacro(raw: string, label: string): string | null {
  return intRangeError(raw, { ge: 0 }, label);
}

export function validateUserName(value: string): string | null {
  return lengthError(value, { min: 1, max: USER_NAME_MAX }, "Имя");
}

export function validateUserSurname(value: string): string | null {
  if (value === "") return null;
  return lengthError(value, { min: 1, max: USER_SURNAME_MAX }, "Фамилия");
}

export function validateAge(raw: string): string | null {
  return intRangeError(raw, { gt: 1, lt: 120 }, "Возраст");
}

export function validateWeight(raw: string): string | null {
  return intRangeError(raw, { gt: 1, lt: 200 }, "Вес");
}

export function validateHeight(raw: string): string | null {
  return intRangeError(raw, { gt: 1, lt: 300 }, "Рост");
}
