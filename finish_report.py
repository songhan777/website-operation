from pathlib import Path
import re

root=Path(__file__).resolve().parent
p=root/'AI网站完整成本分析.md'
s=p.read_text(encoding='utf-8')
infra='''| 服务 | 公开价格参照 | 主要附加条件 |
|---|---|---|
| Cloudflare Workers Paid | 最低$5／账户／月 | 含1,000万请求及3,000万CPU毫秒；超额分别$0.30／百万请求、$0.02／百万CPU毫秒 [S11] |
| Cloudflare R2 标准存储 | $0.015／GB月 | 每月10GB月免费；A类$4.50／百万次、B类$0.36／百万次，分别有100万和1,000万次免费；互联网出网免费 [S12] |
| Supabase Pro | 从$25／组织／月 | 含$10计算抵扣，可覆盖一个Micro；更多项目、计算、容量和出网另计 [S13] |
| Vercel Pro | $20／月平台费 | 含一个部署席位及$20用量抵扣，额外部署席位$20／人／月，用量超额另计 [S14] |
| Stripe美国国内卡线上支付 | 2.9%＋$0.30／成功交易 | 国际卡额外1.5%，需币种转换再加1%；此为美国账户示例 [S15] |

Workers的CPU时间与等待模型API返回的墙钟时间不同，且它不替代GPU推理服务器。[S11] R2的免费出网不代表读取请求或所有相关产品免费。[S12] Vercel的$20抵扣不是再从$20平台费中扣掉一次；商业用途还应确认套餐条款。[S14]

Stripe的固定每笔费会放大小额收款成本：$5订单基础手续费$0.445，占8.9%；$20订单为$0.88，占4.4%。订阅账单、税务服务、退款与争议等按产品和账号另算，不能把上述费率套用到中国大陆主体或所有地区。[S15]'''
regional='''### 13.1 先按市场选择部署

| 服务市场 | 主要成本变化 | 优先控制点 |
|---|---|---|
| 中国大陆为主 | 境内云与模型、域名和接入资料、短信支付、内容治理 | 同区域数据路径、人民币计费、适用备案登记和标识 |
| 海外为主 | 海外API与SaaS、国际收款、税费汇兑、本地化支持 | 用户地区时延、结算费率、出网、数据导出能力 |
| 境内外同时经营 | 两套部署、支付、发布、监控和数据管理 | 收益能覆盖重复运维时再扩展，减少不必要跨区同步 |

服务器放在境外不能直接推出面向境内公众服务的其他义务全部消失。使用海外API前，应确认服务商的支持地区、主体资格、网络质量及数据处理条件；选择架构时同时比较成功率和维护成本。

### 13.2 境内上线的适用事项

ICP备案与经营许可需要分开判断。境内互联网信息服务的许可或备案制度与实际业务有关，不宜仅凭“AI网站”或“接入支付”得出证照结论。预算包括资料、接入、展示和变更维护工时；外包代理费与行政事项不是同一费用。[S16]

生成式AI暂行办法针对向境内公众提供相关服务；未面向境内公众的内部研发应用不按该办法直接套算。具有舆论属性或社会动员能力的服务，还需关注相应安全评估与算法备案条件。[S17] 对调用已备案模型的应用，官方公告给出了地方登记路径；使用已备案模型不代表应用方工作自动完成。[S18]

AI生成合成内容标识办法及配套标准已自2025年9月1日实施。应按业务适用性规划界面标识、文件导出、元数据和测试成本，文本、图片、音视频要求不能混同，也不应默认购买所有数字水印产品。[S19]

### 13.3 数据保护和跨境

需要梳理提示词、上传文件、账户、日志、客服和分析SDK的数据流。数据类型、数量、主体和法定例外会影响跨境程序，不是使用任何海外API都一律需要安全评估，也不是小网站就没有数据保护义务。程序豁免与告知、必要性、权限、删除等义务应分别确认。[S20][S21]

相关成本包括数据清单、条款复核、适用的影响评估、敏感字段处理、权限与删除流程、安全测试及投诉处理。按实际工时和外部报价列专项费用；若已计入研发或支持人力，避免再记一遍。企业或敏感数据场景应在签约前专项确认适用要求。

### 13.4 境内常被低估的费用

对象存储除容量外，还需计算请求、公网下行、CDN回源、跨区复制和处理服务；支持的内网路径与外网下载不能按同一费率计算。[S22] 短信按目的地区、类型、计费条数和合同价计量，长短信、失败重发及刷注册可能增加费用。支付和发信按实际主体与渠道报价，不设虚构的全国统一费率。'''
sources=[
('S1','OpenAI GPT 5.6 Luna 模型及定价','https://developers.openai.com/api/docs/models/gpt-5.6-luna'),
('S2','OpenAI GPT 5.6 Terra 模型及定价','https://developers.openai.com/api/docs/models/gpt-5.6-terra'),
('S3','DeepSeek 中文模型定价与峰谷规则','https://api-docs.deepseek.com/zh-cn/quick_start/pricing/'),
('S4','Anthropic Claude API 定价','https://platform.claude.com/docs/en/about-claude/pricing'),
('S5','OpenAI API 完整定价及处理档位','https://developers.openai.com/api/docs/pricing'),
('S6','OpenAI 提示词缓存与读写计量','https://developers.openai.com/api/docs/guides/prompt-caching'),
('S7','AWS EC2 按需计费与数据传输','https://aws.amazon.com/ec2/pricing/on-demand/'),
('S8','OpenAI GPT Image 1 Mini 图像计费','https://developers.openai.com/api/docs/models/gpt-image-1-mini'),
('S9','OpenAI Sora 2 视频计费','https://developers.openai.com/api/docs/models/sora-2'),
('S10','Vercel Spend Management 预算动作','https://vercel.com/docs/spend-management'),
('S11','Cloudflare Workers 官方计费','https://developers.cloudflare.com/workers/platform/pricing/'),
('S12','Cloudflare R2 官方计费','https://developers.cloudflare.com/r2/pricing/'),
('S13','Supabase 官方定价','https://supabase.com/pricing'),
('S14','Vercel 官方定价','https://vercel.com/pricing'),
('S15','Stripe 美国标准定价','https://stripe.com/pricing'),
('S16','工信部 互联网信息服务管理办法','https://wap.miit.gov.cn/jgsj/zfs/xzfg/art/2020/art_0bf50f171cbf4e5aaca30553d8762d64.html'),
('S17','国家网信办 生成式人工智能服务管理暂行办法','https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm'),
('S18','国家网信办 2026年生成式人工智能服务备案信息公告','https://www.cac.gov.cn/2026-05/13/c_1780413225190669.htm'),
('S19','国家网信办 人工智能生成合成内容标识办法','https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm'),
('S20','国家网信办 促进和规范数据跨境流动规定','https://www.cac.gov.cn/2024-03/22/c_1712776611775634.htm'),
('S21','网络数据安全管理条例','https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm'),
('S22','阿里云 OSS 计费项目','https://help.aliyun.com/zh/oss/billable-item-overview'),
('S23','OpenAI Batch API 异步批处理','https://developers.openai.com/api/docs/guides/batch'),
]
s=s.replace('{{INFRA_PRICING}}',infra).replace('{{REGIONAL}}',regional)
s=s.replace('{{SOURCES}}','\n\n'.join(f'[{k}] [{title}]({url})' for k,title,url in sources))
s=s.replace('### 9.6 基础设施与工程效率','''### 9.6 异步批处理和错峰

允许延迟的分类、评估、索引和批量内容任务可以使用批处理。OpenAI官方Batch文档列出相对同步API的50%费用折扣和24小时处理窗口，需确认具体模型与端点支持。[S23] 如果只有20%的模型费用适合该折扣，总模型费用的理论降幅约10%，不是全部成本减半。

实时聊天不宜直接改成长时间等待。批任务需有进度、失败恢复、结果有效期和重复提交控制；供应商峰谷价和批处理优惠也不能在没有明文支持时假定可以叠加。

### 9.7 基础设施与工程效率''')
s=s.replace('### 6.4 首年和六个月资金','### 6.4 上线后首年和六个月资金')
s=s.replace('不是用户增长预测，也不是净现金消耗预测。','不是用户增长预测，也不是净现金消耗预测。这里的首年指上线后的12个月，不是自立项起的自然年度。')
s=s.replace('基准均按0演算；实际写入或命中需替换计费量','基准均按0演算且不使用可缓存前缀；实际自动写入或命中需替换计费量')
s=s.replace('单次生成费用约5,600元','单次生成费用约5,600元')
s=re.sub(r'^(###) \d+\.\d+ ',r'\1 ',s,flags=re.M)
assert '{{' not in s
p.write_text(s,encoding='utf-8')
print('Report assembled:',len(s),'characters')
