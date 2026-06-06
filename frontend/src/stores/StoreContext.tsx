import { createContext, useContext } from "react";
import type { ReactNode } from "react";

import { rootStore } from "./RootStore";
import type { RootStore } from "./RootStore";

const StoreContext = createContext<RootStore>(rootStore);

export function StoreProvider({ children }: { children: ReactNode }) {
  return (
    <StoreContext.Provider value={rootStore}>{children}</StoreContext.Provider>
  );
}

export function useStore(): RootStore {
  return useContext(StoreContext);
}
