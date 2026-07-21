import { apiClient } from "../../api/client";
import { type components } from "../../api/schema.gen";

export type StatisticsRead = components["schemas"]["StatisticsRead"];
export type ProfileStats = components["schemas"]["ProfileStats"];
export type PostStats = components["schemas"]["PostStats"];
export type MarkStats = components["schemas"]["MarkStats"];
export type NutritionStats = components["schemas"]["NutritionStats"];
export type MacroRatio = components["schemas"]["MacroRatio"];
export type MealStats = components["schemas"]["MealStats"];
export type DailyPoint = components["schemas"]["DailyPoint"];

export const statisticsApi = {
  async getUserStatistics(id: number): Promise<StatisticsRead> {
    const { data: result } = await apiClient.GET("/api/users/{id}/statistics", {
      params: { path: { id } },
    });
    return result!;
  },
};
