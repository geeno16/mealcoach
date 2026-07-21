import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ForgotPasswordPage } from "../features/auth/ForgotPasswordPage";
import { ForkPage } from "../features/auth/ForkPage";
import { LandingPage } from "../features/auth/LandingPage";
import { LoginPage } from "../features/auth/LoginPage";
import { PendingPage } from "../features/auth/PendingPage";
import { SignupPage } from "../features/auth/SignupPage";
import { NotificationsPage } from "../features/notifications/NotificationsPage";
import { PostsPage } from "../features/posts/PostsPage";
import { ProfilePage } from "../features/profile/ProfilePage";
import { StatsPage } from "../features/stats/StatsPage";
import { TraineesPage } from "../features/trainees/TraineesPage";
import { AppLayout } from "../shared/AppLayout";

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
