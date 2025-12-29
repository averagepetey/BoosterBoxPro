/**
 * UI Component Type Definitions
 * 
 * TypeScript interfaces and types for all UI components used in BoosterBoxPro.
 * These types match the API response schemas defined in openapi.yaml
 */

// ============================================================================
// Core Data Types
// ============================================================================

export type RankChangeDirection = "up" | "down" | "same";

export type ReprintRisk = "LOW" | "MEDIUM" | "HIGH";

export type GameType = "One Piece" | "MTG" | "Pokemon" | "Yu-Gi-Oh" | string;

export type SortField = "volume" | "market_cap" | "floor_price" | "floor_change_1d" | "sales" | "listed";

export type SortOrder = "asc" | "desc";

// ============================================================================
// API Response Types
// ============================================================================

export interface SparklineDataPoint {
  timestamp: string; // ISO 8601 date-time
  price: number;
}

export interface BoxMetrics {
  floor_price_usd: number | null;
  floor_price_1d_change_pct: number | null;
  daily_volume_usd: number | null;
  unified_volume_7d_ema: number | null;
  units_sold_count: number | null;
  active_listings_count: number | null;
  listed_percentage: number | null;
  estimated_total_supply: number | null;
  liquidity_score: number | null;
  price_sparkline_1d: SparklineDataPoint[] | null;
}

export interface DetailedBoxMetrics extends BoxMetrics {
  visible_market_cap_usd: number | null;
  expected_days_to_sell: number | null;
  days_to_20_percent: number | null;
  absorption_rate: number | null;
}

export interface LeaderboardBox {
  id: string; // UUID
  rank: number;
  rank_change_direction: RankChangeDirection;
  rank_change_amount: number | null;
  product_name: string;
  set_name: string | null;
  game_type: GameType;
  image_url: string | null;
  metrics: BoxMetrics;
  reprint_risk: ReprintRisk;
  metric_date: string; // ISO 8601 date
}

export interface BoxDetail extends LeaderboardBox {
  release_date: string | null; // ISO 8601 date
  metrics: DetailedBoxMetrics;
  time_series_data: TimeSeriesDataPoint[];
  rank_history: RankHistoryPoint[];
}

export interface TimeSeriesDataPoint {
  date: string; // ISO 8601 date
  floor_price_usd: number | null;
  volume: number | null;
  listings_count: number | null;
  sales_count?: number | null;
  market_cap?: number | null;
}

export interface RankHistoryPoint {
  date: string; // ISO 8601 date
  rank: number;
  rank_change: number | null;
}

export interface ResponseMeta {
  total: number;
  sort: SortField;
  sort_direction: SortOrder;
  date: string; // ISO 8601 date
}

export interface LeaderboardResponse {
  data: LeaderboardBox[];
  meta: ResponseMeta;
}

export interface ErrorResponse {
  error: string;
  detail?: string | null;
}

// ============================================================================
// Component Props Types
// ============================================================================

/**
 * BoxCard Component
 * Displays a single booster box row in the leaderboard table
 */
export interface BoxCardProps {
  box: LeaderboardBox;
  onPress?: (boxId: string) => void;
  isFavorite?: boolean;
  onFavoriteToggle?: (boxId: string) => void;
}

/**
 * MetricCard Component
 * Displays a key metric value with label and optional change indicator
 */
export interface MetricCardProps {
  label: string;
  value: number | string | null;
  change?: number | null; // Percentage change
  changeLabel?: string;
  format?: "currency" | "number" | "percentage" | "days";
  size?: "small" | "medium" | "large";
  highlight?: boolean;
}

/**
 * PriceChart Component
 * Interactive line chart for price trends
 */
export interface PriceChartProps {
  data: TimeSeriesDataPoint[];
  height?: number;
  showTooltip?: boolean;
  dateRange?: {
    start: string;
    end: string;
  };
}

/**
 * RankIndicator Component
 * Shows rank change direction with arrow and amount
 */
export interface RankIndicatorProps {
  direction: RankChangeDirection;
  amount: number | null;
  size?: "small" | "medium" | "large";
}

/**
 * SparklineChart Component
 * Mini chart for 24-hour price trend
 */
export interface SparklineChartProps {
  data: SparklineDataPoint[];
  width?: number;
  height?: number;
  color?: string;
}

/**
 * LeaderboardTable Component
 * Main leaderboard table view
 */
export interface LeaderboardTableProps {
  boxes: LeaderboardBox[];
  sortBy?: SortField;
  sortOrder?: SortOrder;
  onSortChange?: (field: SortField, order: SortOrder) => void;
  onBoxPress?: (boxId: string) => void;
  loading?: boolean;
  error?: string | null;
}

/**
 * BoxDetailView Component
 * Advanced analytics detail page
 */
export interface BoxDetailViewProps {
  box: BoxDetail;
  loading?: boolean;
  error?: string | null;
  onBack?: () => void;
  onFavoriteToggle?: (boxId: string) => void;
  isFavorite?: boolean;
}

/**
 * RankHistoryChart Component
 * Chart showing rank position over time
 */
export interface RankHistoryChartProps {
  data: RankHistoryPoint[];
  height?: number;
}

/**
 * TimeSeriesTable Component
 * Table displaying historical metrics
 */
export interface TimeSeriesTableProps {
  data: TimeSeriesDataPoint[];
  sortBy?: keyof TimeSeriesDataPoint;
  sortOrder?: SortOrder;
  onSortChange?: (field: keyof TimeSeriesDataPoint, order: SortOrder) => void;
  onExport?: () => void;
}

// ============================================================================
// Component State Types
// ============================================================================

export type LoadingState = "idle" | "loading" | "success" | "error";

export interface ComponentState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface LeaderboardState extends ComponentState<LeaderboardBox[]> {
  sortBy: SortField;
  sortOrder: SortOrder;
  limit: number;
  date: string | null;
}

export interface BoxDetailState extends ComponentState<BoxDetail> {
  boxId: string | null;
}

// ============================================================================
// Navigation Types
// ============================================================================

export type ScreenName = "Leaderboard" | "BoxDetail" | "Favorites";

export interface NavigationParams {
  Leaderboard: undefined;
  BoxDetail: { boxId: string };
  Favorites: undefined;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Format a number as currency
 */
export type CurrencyFormatter = (value: number) => string;

/**
 * Format a number as percentage
 */
export type PercentageFormatter = (value: number) => string;

/**
 * Format a number as days
 */
export type DaysFormatter = (value: number) => string;

