# エッジAI向けモデル圧縮技術の研究ノート

## 研究者：田中優一（東京大学 情報理工学研究科）
## 日付：2024年3月-6月

---

## 1. 量子化実験メモ

### 1.1 INT8量子化の精度影響

ResNet-50をINT8量子化した結果：
- PTQ（Post-Training Quantization）: Top-1精度 75.8% → 75.1% (△-0.7%)
- QAT（Quantization-Aware Training）: Top-1精度 75.8% → 75.6% (△-0.2%)
- キャリブレーションデータセット: ImageNet validation 1000枚で十分

### 1.2 INT4量子化の限界

INT4まで量子化すると精度劣化が顕著：
- Vision Transformer (ViT-B/16): 精度3.2%低下
- CNN系モデルは比較的堅牢（1.5%以内の低下）
- 混合精度（attention層はINT8、FC層はINT4）で妥協点を見出す

### 1.3 実験環境
- ハードウェア: NVIDIA Jetson AGX Orin (64GB)
- フレームワーク: TensorRT 8.6, PyTorch 2.1
- 測定条件: バッチサイズ1、ウォームアップ100回、測定1000回の平均

---

## 2. 構造的枝刈り（Structured Pruning）

### 2.1 チャネル枝刈りの効果

MobileNetV3-Largeに対するチャネル枝刈り実験：

| 枝刈り率 | FLOPs削減 | 精度変化 | 推論時間 (Jetson) |
|---------|----------|---------|-----------------|
| 20% | 35% | -0.3% | 2.8ms → 2.1ms |
| 40% | 55% | -1.2% | 2.8ms → 1.6ms |
| 60% | 72% | -3.8% | 2.8ms → 1.1ms |

### 2.2 N:M スパース性

2:4スパース性（4要素中2つをゼロ化）の実装：
- NVIDIA Ampere以降のGPUでハードウェアサポート
- 実効スループット約2倍
- 精度劣化は0.5%未満（ファインチューニング後）
- **課題**: エッジデバイスでのスパース推論サポートが限定的

---

## 3. 知識蒸留実験

### 3.1 教師-生徒モデル構成

実験設定：
- 教師モデル: EfficientNet-B7 (66M params, 84.3% Top-1)
- 生徒モデル: EfficientNet-B0 (5.3M params)
- 蒸留後精度: 77.1% → 79.4% (+2.3%)
- 蒸留損失: KLダイバージェンス + Hard Label Loss (α=0.7)

### 3.2 特徴マップ蒸留

中間層の特徴マップも蒸留対象にすると効果向上：
- FitNets方式: +1.1%
- Attention Transfer方式: +0.8%
- 計算コスト: 蒸留訓練に通常の3倍の時間が必要

---

## 4. Neural Architecture Search (NAS) 結果

### 4.1 ターゲットデバイス別最適アーキテクチャ

Jetson Orin NX向けNAS実験（探索空間: MobileNetV3ベース）：
- 探索時間: 8 GPU-days（NVIDIA A100 x8）
- 発見アーキテクチャ: 4.8ms推論、76.3% Top-1精度
- 手動設計モデル比: 推論速度22%改善、精度同等

### 4.2 省電力制約付きNAS

消費電力2W以下の制約でNAS実行：
- 最適モデル: 1.2M params, 68.5% Top-1, 1.8W, 8.2ms
- IoTデバイスでの展開に適する
- 精度と電力のトレードオフが明確に可視化できた

---

## 5. 実用化に向けた課題

### 5.1 量産デバイスでの検証

ラボ環境と量産デバイスの性能差：
- 熱スロットリングにより、持続推論で15-30%の性能低下
- バッテリー駆動時はさらに電力制約が厳しい
- デバイス個体差も考慮が必要（特にFPGA実装時）

### 5.2 モデル更新・バージョン管理

- OTA（Over-the-Air）でのモデル差分配信技術が必要
- A/Bテスト相当の機能をエッジでも実現すべき
- ロールバック機能は必須

### 5.3 今後の研究方向

1. **超低ビット量子化**: 2bit/1bit量子化の実用化
2. **デバイス適応的NAS**: デバイスの動的状態に応じたモデル切り替え
3. **連合学習との統合**: エッジでの推論+学習の同時実行
4. **大規模言語モデルのエッジ展開**: LLMの7Bパラメータクラスをスマートフォンで実行

---

## 6. 参考文献（メモ）

- Jacob et al., "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", CVPR 2018
- Liu et al., "Rethinking the Value of Network Pruning", ICLR 2019
- Hinton et al., "Distilling the Knowledge in a Neural Network", NeurIPS Workshop 2015
- Wu et al., "FBNet: Hardware-Aware Efficient ConvNet Design via Differentiable NAS", CVPR 2019
