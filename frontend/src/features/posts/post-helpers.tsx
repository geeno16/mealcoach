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
