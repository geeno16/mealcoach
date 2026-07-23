import { type PostRead } from "../../api";

export function PostMark({ mark }: { mark: number | null | undefined }) {
  if (mark === null || mark === undefined) {
    return <span className="post-unrated">Не оценено</span>;
  }
  return (
    <div className="post-stars">
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= mark ? "star star-filled" : "star"}>
          ★
        </span>
      ))}
    </div>
  );
}

export function mealsLabel(count: number): string {
  const word = count === 1 ? "мил" : "мила";
  return `${count} ${word}`;
}

export function formatPostDate(iso: string): string {
  const date = new Date(iso);
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${day}.${month} ${hours}:${minutes}`;
}

export function dateKeyOf(iso: string): string {
  const date = new Date(iso);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

const MONTHS_GENITIVE = [
  "января",
  "февраля",
  "марта",
  "апреля",
  "мая",
  "июня",
  "июля",
  "августа",
  "сентября",
  "октября",
  "ноября",
  "декабря",
];

export function formatDayLabel(dateKey: string): string {
  const [, month, day] = dateKey.split("-");
  return `${Number(day)} ${MONTHS_GENITIVE[Number(month) - 1]}`;
}

export interface PostDateTotals {
  cal: number;
  protein: number;
  fat: number;
  carbohydrate: number;
}

export interface PostDateGroup {
  dateKey: string;
  label: string;
  posts: PostRead[];
  totals: PostDateTotals;
}

function sumDayTotals(groupPosts: PostRead[]): PostDateTotals {
  const totals: PostDateTotals = {
    cal: 0,
    protein: 0,
    fat: 0,
    carbohydrate: 0,
  };
  for (const post of groupPosts) {
    for (const meal of post.meals ?? []) {
      totals.cal += meal.cal ?? 0;
      totals.protein += meal.protein ?? 0;
      totals.fat += meal.fat ?? 0;
      totals.carbohydrate += meal.carbohydrate ?? 0;
    }
  }
  return totals;
}

export function groupPostsByDate(posts: PostRead[]): PostDateGroup[] {
  const buckets = new Map<string, PostRead[]>();
  for (const post of posts) {
    const key = dateKeyOf(post.created_at);
    const bucket = buckets.get(key);
    if (bucket) bucket.push(post);
    else buckets.set(key, [post]);
  }
  return [...buckets.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([dateKey, groupPosts]) => ({
      dateKey,
      label: formatDayLabel(dateKey),
      posts: groupPosts,
      totals: sumDayTotals(groupPosts),
    }));
}

export function formatDayTotals(totals: PostDateTotals): string {
  return (
    `${Math.round(totals.cal)} ккал · ` +
    `Б ${Math.round(totals.protein)} г · ` +
    `Ж ${Math.round(totals.fat)} г · ` +
    `У ${Math.round(totals.carbohydrate)} г`
  );
}
