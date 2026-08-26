# FundOS 基金引擎审计报告
> 审计时间: 2026-08-26T13:34:38.792875+08:00

## 数据来源
- 持仓来源: daily_check_result.json
- 持仓时间: 2026-08-26T13:15:16.027877+08:00
- 新闻文件: 存在
- 新闻条数: 15

## 新闻来源状态
- 快讯: ok，15条，耗时 0ms
- 政策: empty，0条，耗时 0ms
- 公告: empty，0条，耗时 0ms
- 宏观: empty，0条，耗时 0ms
- 资金: empty，0条，耗时 0ms
- 海外: empty，0条，耗时 0ms
- wallstreetcn_live: ok，345条，耗时 11763ms
- tiantian_announce: error，0条，耗时 1022ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- pbc_gov: empty，0条，耗时 9611ms
- investing_global: error，0条，耗时 1051ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- miit_gov: empty，0条，耗时 10839ms
- cls_telegram: error，0条，耗时 11286ms，错误: HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E5%85%89%E4%BC%8F&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%BE%8E%E8%81%94%E5%82%A8&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=CPI&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E5%85%89%E5%88%BB%E6%9C%BA&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E6%99%B6%E5%9C%86&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E6%A0%87%E6%99%AE500&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E8%8A%AF%E7%89%87&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=DeepSeek&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E5%A4%A7%E6%A8%A1%E5%9E%8B&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E5%8D%8A%E5%AF%BC%E4%BD%93&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%BA%B3%E6%96%AF%E8%BE%BE%E5%85%8B&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=ChatGPT&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E5%85%88%E8%BF%9B%E5%B0%81%E8%A3%85&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%A2%B3%E4%B8%AD%E5%92%8C&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%A7%91%E5%88%9B50&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%AE%97%E5%8A%9B&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%A1%AC%E7%A7%91%E6%8A%80&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E9%9D%9E%E5%86%9C&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=HBM&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E7%A7%91%E5%88%9B%E6%9D%BF&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E6%96%B0%E5%9E%8B%E7%94%B5%E5%8A%9B%E7%B3%BB%E7%BB%9F&type=telegram&page=0&rn=15; HTTPError: 405 Client Error: Method Not Allowed for url: https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=8.4.6&keyword=%E9%A3%8E%E7%94%B5&type=telegram&page=0&rn=15
- eastmoney_news: error，0条，耗时 9912ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- 10jqka_capital: error，0条，耗时 1061ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- eastmoney_fund_announce: error，0条，耗时 1040ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- cninfo_announce: empty，0条，耗时 4959ms
- eastmoney_macro: error，0条，耗时 1064ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- eastmoney_global: error，0条，耗时 1053ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- xueqiu_hot: error，0条，耗时 1057ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- investing_macro: error，0条，耗时 1058ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- nea_gov: empty，0条，耗时 13076ms
- eastmoney_capital: error，0条，耗时 22980ms，错误: ProxyError: HTTPSConnectionPool(host='push2.eastmoney.com', port=443): Max retries exceeded with url: /api/qt/clist/get?pn=1&pz=5&fs=m%3A90%2Bt2&fields=f2%2Cf3%2Cf4%2Cf12%2Cf14%2Cf62%2Cf184&fid=f62&po=1 (Caused by ProxyError('Unable to connect to proxy', RemoteDisconnected('Remote end closed connect; AttributeError: 'NoneType' object has no attribute 'get'
- eastmoney_policy: error，0条，耗时 1022ms，错误: JSONDecodeError: Expecting value: line 1 column 1 (char 0)

## 风险提示
- 预测和新闻情绪不得单独触发交易。
- 本审计只读，不修改交易日志，不自动下单。
- 失败或滞后数据不得标记为实时确认。

> 本报告不构成投资建议。