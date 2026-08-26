# API Contracts — gRPC Protobuf 定义

## 通用类型

```protobuf
syntax = "proto3";
package fundos.common.v1;

// 分页
message Pagination {
  int32 page = 1;
  int32 page_size = 2;
  int32 total = 3;
}

// 时间范围
message DateRange {
  string start = 1;  // "2024-01-01"
  string end = 2;    // "2024-12-31"
}

// 排序
message SortOption {
  string field = 1;
  bool descending = 2;
}
```

## 基金服务 (Data Hub)

```protobuf
syntax = "proto3";
package fundos.data.v1;
import "common/v1/common.proto";

service FundService {
  rpc GetNavHistory(GetNavHistoryRequest) returns (stream FundNavPoint);
  rpc GetEstimate(GetEstimateRequest) returns (FundEstimateResponse);
  rpc GetHoldings(GetHoldingsRequest) returns (FundHoldingsResponse);
  rpc GetProfile(GetProfileRequest) returns (FundProfileResponse);
  rpc GetManager(GetManagerRequest) returns (FundManagerResponse);
  rpc SearchFund(SearchFundRequest) returns (SearchFundResponse);
  rpc StreamRealtime(stream FundCodeRequest) returns (stream FundRealtimeResponse);
  rpc BatchGetEstimate(BatchEstimateRequest) returns (BatchEstimateResponse);
}

message GetNavHistoryRequest {
  string fund_code = 1;
  common.v1.DateRange date_range = 2;
  string provider = 3;  // "eastmoney" | "tiantian" (留空=auto)
}

message FundNavPoint {
  string date = 1;          // "2026-01-15"
  double nav = 2;           // 单位净值
  double acc_nav = 3;       // 累计净值
  double daily_return = 4;  // 日涨跌幅
  string source = 5;
}

message GetEstimateRequest {
  string fund_code = 1;
  string provider = 2;
}

message FundEstimateResponse {
  string fund_code = 1;
  string fund_name = 2;
  double estimate_nav = 3;
  double estimate_return = 4;
  double last_nav = 5;
  string estimate_time = 6;
  string source = 7;
}

message GetHoldingsRequest {
  string fund_code = 1;
  string report_date = 2;  // "2025Q4" (留空=最新)
}

message Holding {
  string stock_code = 1;
  string stock_name = 2;
  double ratio = 3;        // 持仓占比
  double market_value = 4; // 持仓市值
}

message FundHoldingsResponse {
  string fund_code = 1;
  string report_date = 2;
  repeated Holding holdings = 3;
}

message FundProfileResponse {
  string fund_code = 1;
  string fund_name = 2;
  string fund_type = 3;     // 股票型/混合型/债券型/货币型/指数型
  string manager = 4;
  string company = 5;
  double total_assets = 6;   // 基金规模(亿)
  string inception_date = 7;
  double management_fee = 8;
  string benchmark = 9;
  string source = 10;
}

message SearchFundRequest {
  string keyword = 1;
  string fund_type = 2;
  common.v1.Pagination pagination = 3;
}

message FundSearchItem {
  string fund_code = 1;
  string fund_name = 2;
  string fund_type = 3;
  double nav = 4;
  double daily_return = 5;
}

message SearchFundResponse {
  repeated FundSearchItem items = 1;
  common.v1.Pagination pagination = 2;
}

message FundCodeRequest {
  repeated string fund_codes = 1;
}

message FundRealtimeResponse {
  string fund_code = 1;
  double estimate_nav = 2;
  double estimate_return = 3;
  string update_time = 4;
}

message BatchEstimateRequest {
  repeated string fund_codes = 1;
}

message BatchEstimateResponse {
  repeated FundEstimateResponse estimates = 1;
}
```

## 股票服务 (Data Hub)

```protobuf
package fundos.data.v1;

service StockService {
  rpc GetQuote(GetQuoteRequest) returns (StockQuoteResponse);
  rpc GetKline(GetKlineRequest) returns (stream StockKlinePoint);
  rpc GetBaseInfo(GetBaseInfoRequest) returns (StockBaseInfoResponse);
  rpc SearchStock(SearchStockRequest) returns (SearchStockResponse);
  rpc StreamQuote(stream StockCodeRequest) returns (stream StockQuoteResponse);
}

message GetQuoteRequest {
  string stock_code = 1;
  string market = 2;  // sh/sz/hk/us
}

message StockQuoteResponse {
  string stock_code = 1;
  string stock_name = 2;
  string market = 3;
  double open = 4;
  double high = 5;
  double low = 6;
  double price = 7;
  double change_pct = 8;
  int64 volume = 9;
  double amount = 10;
}

message GetKlineRequest {
  string stock_code = 1;
  string market = 2;
  common.v1.DateRange date_range = 3;
  string period = 4;  // day/week/month
  string adjust = 5;  // qfq/hfq/none (前复权/后复权/不复权)
}

message StockKlinePoint {
  string date = 1;
  double open = 2;
  double high = 3;
  double low = 4;
  double close = 5;
  int64 volume = 6;
  double amount = 7;
  double change_pct = 8;
}

message StockBaseInfoResponse {
  string stock_code = 1;
  string stock_name = 2;
  string industry = 3;
  string concept = 4;
  double total_market_cap = 5;  // 总市值(亿)
  double pe_ratio = 6;
  double pb_ratio = 7;
  double dividend_yield = 8;
}
```

## 回测服务 (Quant Engine)

```protobuf
package fundos.quant.v1;

service BacktestService {
  rpc RunBacktest(RunBacktestRequest) returns (RunBacktestResponse);
  rpc GetBacktestResult(GetBacktestResultRequest) returns (BacktestResultResponse);
  rpc ListStrategies(ListStrategiesRequest) returns (ListStrategiesResponse);
  rpc GetIndicators(GetIndicatorsRequest) returns (IndicatorsResponse);
}

message RunBacktestRequest {
  string strategy_id = 1;
  repeated string fund_codes = 2;
  string start_date = 3;
  string end_date = 4;
  double initial_capital = 5;  // 初始资金
  map<string, string> params = 6;  // 策略参数
}

message RunBacktestResponse {
  string job_id = 1;
  string status = 2;  // "running" | "completed" | "failed"
}

message BacktestResultResponse {
  string job_id = 1;
  string status = 2;
  double total_return = 3;
  double annual_return = 4;
  double sharpe_ratio = 5;
  double max_drawdown = 6;
  double win_rate = 7;
  double benchmark_return = 8;
  double excess_return = 9;
  repeated DailySnapshot daily_snapshots = 10;
  string ai_interpretation = 11;  // AI解读
}

message DailySnapshot {
  string date = 1;
  double nav = 2;
  double return_pct = 3;
  int32 position_count = 4;
  repeated TradeRecord trades = 5;
}

message TradeRecord {
  string date = 1;
  string fund_code = 2;
  string action = 3;    // buy/sell
  double amount = 4;
  double price = 5;
}

message IndicatorsRequest {
  repeated string fund_codes = 1;
  common.v1.DateRange date_range = 2;
  repeated string indicator_names = 3;  // ["sharpe", "drawdown", "volatility"]
}

message IndicatorsResponse {
  map<string, FundIndicators> results = 1;  // fund_code → indicators
}

message FundIndicators {
  double sharpe_ratio = 1;
  double max_drawdown = 2;
  double annual_volatility = 3;
  double annual_return = 4;
  double calmar_ratio = 5;
  double sortino_ratio = 6;
  double information_ratio = 7;
  double alpha = 8;
  double beta = 9;
}
```

## AI服务 (AI Brain)

```protobuf
package fundos.ai.v1;

service AgentService {
  rpc Chat(stream ChatRequest) returns (stream ChatResponse);
  rpc AnalyzeFund(AnalyzeFundRequest) returns (AnalyzeFundResponse);
  rpc AnalyzePortfolio(AnalyzePortfolioRequest) returns (AnalyzePortfolioResponse);
  rpc GenerateReport(GenerateReportRequest) returns (GenerateReportResponse);
}

message ChatRequest {
  string session_id = 1;
  string message = 2;
  string model = 3;  // openai/deepseek/ollama (留空=default)
}

message ChatResponse {
  string session_id = 1;
  string content = 2;
  repeated ToolCall tool_calls = 3;
  bool is_final = 4;
}

message ToolCall {
  string tool_name = 1;
  string arguments = 2;  // JSON
  string result = 3;
}

message AnalyzeFundRequest {
  string fund_code = 1;
  repeated string analysis_types = 2;  // ["nav", "risk", "holdings", "manager", "all"]
}

message AnalyzeFundResponse {
  string fund_code = 1;
  string summary = 2;
  map<string, string> sections = 3;  // type → content
  repeated string suggestions = 4;
}

message AnalyzePortfolioRequest {
  repeated FundPosition positions = 1;
  string analysis_focus = 2;  // risk/diversification/optimization
}

message FundPosition {
  string fund_code = 1;
  double amount = 2;
  double cost = 3;
}

message AnalyzePortfolioResponse {
  double total_value = 1;
  double total_return = 2;
  string risk_assessment = 3;
  repeated string diversification_issues = 4;
  repeated string optimization_suggestions = 5;
  map<string, double> risk_metrics = 6;
}

message GenerateReportRequest {
  string report_type = 1;  // daily/weekly/monthly/backtest_summary
  repeated string fund_codes = 2;
  common.v1.DateRange date_range = 3;
  string format = 4;  // markdown/html/image
}

message GenerateReportResponse {
  string report_id = 1;
  string content = 2;
  string format = 3;
  string generated_at = 4;
}
```
