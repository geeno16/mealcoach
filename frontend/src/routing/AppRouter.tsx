import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../pages/AppLayout";
import { ForgotPasswordPage } from "../pages/ForgotPasswordPage";
import { ForkPage } from "../pages/ForkPage";
import { LandingPage } from "../pages/LandingPage";
import { LoginPage } from "../pages/LoginPage";
import { NotificationsPage } from "../pages/NotificationsPage";
import { PendingPage } from "../pages/PendingPage";
import { PostsPage } from "../pages/PostsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { SignupPage } from "../pages/SignupPage";
import { StatsPage } from "../pages/StatsPage";
import { TraineesPage } from "../pages/TraineesPage";

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
            <Route element={<AppLayout />}>
              <Route path="profile" element={<ProfilePage />} />
              <Route path="notifications" element={<NotificationsPage />} />
              <Route path="posts" element={<PostsPage />} />
              <Route path="stats" element={<StatsPage />} />
              <Route path="trainees" element={<TraineesPage />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
