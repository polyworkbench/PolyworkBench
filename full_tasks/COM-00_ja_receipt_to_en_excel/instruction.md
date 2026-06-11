# 日文票据处理 → 英文报销包

`/workspace/inputs/` 里有 3 张日文票据的 OCR 文本、图像描述和 JPY→CNY 汇率。帮我做成 SAP Concur 的英文报销材料。

具体来说：
- 从票据里提取日期、金额、税率（8% 軽減 / 10% 標準）、宛名等信息
- 注意「上様」抬头的规则：≥30,000 JPY 不可入账
- 算好汇率转换，写个 Python 脚本自动验算一遍确保数字对得上
- 生成 Concur CSV（含 BOM）、异常报告、验算结果

结果放 `/workspace/output/`，最后汇总成 `/workspace/answer.json`。

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash/shell 命令创建目录、写文件、执行脚本。**
