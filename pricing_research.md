# AI 网站供应商公开定价核查

核查日期：2026-09-13（Asia/Shanghai）。本文件为主文档研究底稿，所有价格应标注币种、单位、适用地区与附加条件，不等于供应商最终报价。模型页面已直接打开，基础设施部分基于工具返回的官方页面索引正文；部分直接打开请求超时，不将搜索摘要中的旧版模型价格作为现价。

## 1. DeepSeek：人民币原币价可直接用于国内预算

[官方中文定价](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)；[官方英文美元定价](https://api-docs.deepseek.com/quick_start/pricing/)。直接打开，两页均标记今日抓取；官网未显示定价页发布日期。

单位：人民币元 / 100 万 tokens。

| API 模型名及版本 | 时段 | 输入缓存命中 | 输入缓存未命中 | 输出 |
|---|---|---:|---:|---:|
| deepseek-flash / DeepSeek-V4.1-Flash | 空闲 | 0.02 | 1 | 4 |
| deepseek-flash / DeepSeek-V4.1-Flash | 高峰 | 0.04 | 2 | 8 |
| deepseek-v4-pro / DeepSeek-V4-Pro-0813 | 空闲 | 0.15 | 4.5 | 13.5 |
| deepseek-v4-pro / DeepSeek-V4-Pro-0813 | 高峰 | 0.30 | 9 | 27 |

高峰时段：北京时间周一至周五 09:00–12:00、14:00–18:00；其余均为空闲时段。Flash 与 Pro 均支持思考 / 非思考、上下文 1M，最大输出 384K；API 并发限制分别为 2500 / 500，不能据此假定每个客户都有无限吞吐或 SLA。Flash 支持图像理解，Pro 该页列为不支持。旧名 deepseek-v4-flash 已由 V4.1-Flash 服务并按 Flash 新价收费。官网说明 2026-09-14 后 Pro API 继续提供且现计费方式不变。

美元页对应每百万 tokens，Flash 空闲/高峰输入缓存命中 $0.003/$0.006、未命中 $0.15/$0.30、输出 $0.60/$1.20；Pro 对应 $0.022/$0.044、$0.66/$1.32、$1.98/$3.96。中英文原币价格不能用一个精确汇率相互推导；按账户实际计费币种建模。

研究风险：搜索索引曾返回 V4-Flash 输出 2 元、Pro 未命中 3 元等旧价，也有“每日峰谷”旧规则。已剔除，以今日直接打开页面为准。主文档应使用高峰调用占比 q 加权：P均 = (1-q)×P空闲 + q×P高峰。异步任务迁移到空闲时段只节省这些迁移任务的模型费用，不是全站成本直接减半。

## 2. Anthropic：海外 API 比较基准

[官方定价详情](https://platform.claude.com/docs/en/about-claude/pricing)；[官方型号与限制](https://platform.claude.com/docs/en/models/overview)；[定价首页](https://claude.com/pricing)。直接打开，今日抓取。全部为美元 / 100 万 tokens，全球路由标准模式。

| 型号 | 标准输入 | 5 分钟缓存写 | 1 小时缓存写 | 缓存读 | 输出 |
|---|---:|---:|---:|---:|---:|
| Claude Haiku 4.5 | 1 | 1.25 | 2 | 0.10 | 5 |
| Claude Sonnet 5 | 2 | 2.50 | 4 | 0.20 | 10 |
| Claude Opus 5 | 5 | 6.25 | 10 | 0.50 | 25 |
| Claude Fable 5.1 | 10 | 12.50 | 20 | 0.25 | 50 |

API IDs：claude-haiku-4-5-20251001、claude-sonnet-5、claude-opus-5、claude-fable-5-1。Haiku 上下文 / 最大输出为 200K / 64K，其余为 1M / 128K。Sonnet 5 原定 2026-09-01 涨价已被官网取消，$2/$10 成为标准价。Claude 4.7 及以后 tokenizer 对相同文本可能产生约 30% 更多 tokens，不能假定所有模型处理同文 token 数完全相同。

优化约束：Batch 异步输入与输出均 50% 折扣；缓存写会收费，5 分钟写入 1.25 倍普通输入，1 小时 2 倍。美国限定推理适用模型为全部 token 价格乘 1.1；Opus 5 Fast 模式为标准价 2 倍，不能与 Batch 并用。Web search $10 / 1000 次搜索，且检索内容仍计入模型 tokens。不要把 Claude Pro/Max 订阅当作网站生产 API 额度。

## 3. Cloudflare Workers 与 R2

[Workers 官方定价](https://developers.cloudflare.com/workers/platform/pricing/)：页面 Last updated Aug 28, 2026，索引昨日抓取。

Workers Paid 最低 $5 / 账户 / 月；每月含 1000 万请求与 3000 万 CPU 毫秒。超额请求 $0.30 / 100 万，CPU $0.02 / 100 万毫秒。普通 Workers 不按等待时长收费，外部 API 等待不等于 CPU；静态资源请求免费无限，但启用 Workers Caching 时，经其缓存处理的请求仍按请求计费。免费层 10 万请求 / 日、每次 10ms CPU；生产容量需检查运行时限制。Workers 不是通用 GPU 推理服务器，不能用 $5 对比自托管大模型总成本。Containers 另有 CPU、内存与出口费用，不能把 Workers 无出口收费泛化到全部 Cloudflare 产品。

[R2 官方定价](https://developers.cloudflare.com/r2/pricing/)：页面 Last updated Aug 7, 2026，索引 2 日前抓取。

| R2 项目 | 标准存储 | 低频存储 |
|---|---:|---:|
| 存储 | $0.015 / GB-month | $0.01 / GB-month |
| A 类操作 | $4.50 / 100 万次 | $9 / 100 万次 |
| B 类操作 | $0.36 / 100 万次 | $0.90 / 100 万次 |
| 数据取回 | 无 | $0.01 / GB |
| 出口到互联网 | 免费 | 免费 |

标准存储免费额度每月：10 GB-month、100 万次 A 类、1000 万次 B 类；低频不享受此免费额度，最低存储 30 日。操作量、存储、取回量按账单单位向上取整。A 类通常包含上传/列举，B 类包含读取；分片上传会产生多次操作。生命周期删除、CDN 缓存与直接下载链接的省钱效果来自具体字节和操作量，不应只看存储容量。

## 4. Supabase 与 Vercel

[Supabase 官方价格](https://supabase.com/pricing)，索引 2 日前抓取；[官方计费问答](https://supabase.com/docs/guides/platform/billing-faq)，页面更新 / 索引均 2 日前。

Pro 从 $25 / 组织 / 月，含 $10 compute credit，足以覆盖一个 Micro 实例（约 $10 / 月）。额外 Micro 项目各约 $10 / 月；例：三个 Micro 项目总价 $25+$30-$10=$45 / 月。更大规格另算：Small $15、Medium $60、Large $110 / 月左右，实际计算按小时。不要重复计算首个 Micro，也不要遗漏预发 / 测试项目。

Pro 包含 10 万 MAU（超额 $0.00325 / MAU）、每项目 8GB 数据库磁盘（超额 $0.125 / GB）、250GB 普通出口（$0.09 / GB 超额）、250GB 缓存出口（$0.03 / GB 超额）、100GB 文件存储（$0.0213 / GB 超额）、7 日每日备份与 7 日日志。PITR 从 $100 / 月、每 7 日保留期；自定义域名 $10 / 月。Pro 默认有 Spend Cap，但不能视为所有账单项目的硬总额上限，预算仍需核对具体受控项目。

[Vercel Pro 官方方案](https://vercel.com/docs/plans/pro-plan)，页面最后更新 2026-02-03，索引 6 个月前；[Vercel 官方价格](https://vercel.com/pricing)，索引 2 日前；[Pro 用量改版公告](https://vercel.com/changelog/included-pro-usage-is-now-credit-based)，发布 2025-09-09。

Pro 平台费 $20 / 月，含 1 个可部署席位和 $20 / 月基础设施用量抵扣；额外可部署席位 $20 / 人 / 月，Viewer 免费。方案文档列每月包含 1TB Fast Data Transfer、1000 万 Edge Requests；各计费维度超过赠额后先抵扣 $20，再按需收费。不能把“$20 抵扣”重复当作折扣减去平台费，也不能把所有超额费用想成只有带宽。Hobby 限个人非商业用途；商业站应按 Pro 或另选合适托管方案。实时页面仍需在采购时复核，因为方案文档抓取较旧。

## 5. Stripe 收款费用示例

[Stripe 官方定价](https://stripe.com/pricing)，索引昨日抓取；以下为美国标准定价、美国国内卡成功线上交易示例，并非中国大陆主体通用费率。

成功交易费：2.9% × 成交额 + $0.30 / 笔；国际卡额外 +1.5%，需要币种转换再 +1%。最低月费和设置费为零不代表没有其它产品附加费用；Billing、Tax、拒付、退款损失、跨境 / 汇兑等应单独估算或查实际账户价。建模应明确交易笔数而非仅 GMV：$5 订单基础手续费 $0.445（8.9%），$20 订单 $0.88（4.4%），$100 订单 $3.20（3.2%）。小额高频付费可通过最低充值包和集中结算降低固定每笔费用占比，同时关注退款与现金流义务。

## 交付主文档时建议保留的边界

上述基础设施组合属于可比较参考组件，Cloudflare、Vercel 不应无条件重复购买与累计。国内可用性、数据处理地域、供应商准入和采购账户币种需按目标用户市场选型；国内自建实例价格取决于地区、规格、带宽、续费与优惠，未查得准确配置报价时应使用明确“预算假设区间”。2026-09-13 为核查日期；网页列出的未来服务持续通知（如 DeepSeek 9 月 14 日后继续服务）不与核查日期矛盾，但不能当作已发生的运行结果。
