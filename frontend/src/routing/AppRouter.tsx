import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ForgotPasswordPage } from "../pages/ForgotPasswordPage";
import { ForkPage } from "../pages/ForkPage";
import { LandingPage } from "../pages/LandingPage";
import { LoginPage } from "../pages/LoginPage";
import { PendingPage } from "../pages/PendingPage";
import { ProfilePage } from "../pages/ProfilePage";
import { SignupPage } from "../pages/SignupPage";

import {
  RequireActive,
  RequireGuest,
  RequireNoProfile,
  RequirePending,
} from "./guards";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route path="/app">
          <Route element={<RequireGuest />}>
            <Route path="signup" element={<SignupPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="reset" element={<ForgotPasswordPage />} />
          </Route>

          <Route element={<RequireNoProfile />}>
            <Route path="fork" element={<ForkPage />} />
          </Route>

          <Route element={<RequirePending />}>
            <Route path="pending" element={<PendingPage />} />
          </Route>

          <Route element={<RequireActive />}>
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
