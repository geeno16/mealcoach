import { useEffect, useState } from "react";

const BREAKPOINTS: [number, 2 | 3 | 4][] = [
  [1440, 4],
  [1100, 3],
  [640, 2],
];

function computeColumns(width: number): 1 | 2 | 3 | 4 {
  for (const [minWidth, columns] of BREAKPOINTS) {
    if (width >= minWidth) return columns;
  }
  return 1;
}

export function usePostColumns(): 1 | 2 | 3 | 4 {
  const [columns, setColumns] = useState(() =>
    computeColumns(window.innerWidth),
  );

  useEffect(() => {
    const onResize = () => setColumns(computeColumns(window.innerWidth));
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return columns;
}
