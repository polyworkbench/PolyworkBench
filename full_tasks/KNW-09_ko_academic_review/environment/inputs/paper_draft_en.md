# Multimodal Learning for Cross-lingual Transfer: A Unified Framework

**Authors:** Anonymous (double-blind review)  
**Submission ID:** ACML-2025-0847  
**Track:** Main Conference

## Abstract

Cross-lingual transfer learning has shown remarkable progress in recent years, primarily driven by multilingual language models. However, existing approaches largely focus on textual modality alone, limiting their effectiveness for tasks involving visual, auditory, or structured data inputs. We propose MultiX-Transfer, a unified framework that leverages multimodal pre-training to enhance cross-lingual transfer across 47 languages. Our approach introduces a novel modality-bridging mechanism that aligns visual and textual representations across languages without requiring parallel multimodal corpora. Experiments on 5 downstream tasks demonstrate that MultiX-Transfer achieves an average improvement of 4.7% over state-of-the-art multilingual models, with particularly strong gains for low-resource languages (+8.2% average).

## 1. Introduction

The ability to transfer knowledge across languages is fundamental to building inclusive NLP systems. While multilingual pre-trained models such as mBERT, XLM-R, and BLOOM have achieved impressive cross-lingual transfer, they operate exclusively on textual inputs. Real-world applications increasingly require processing of multimodal information — images, audio, video — in multilingual contexts.

Recent work on vision-language models (CLIP, ALIGN, PaLI) has demonstrated the power of multimodal pre-training but primarily targets high-resource languages. The challenge of extending multimodal capabilities to low-resource languages remains largely unaddressed.

In this paper, we present MultiX-Transfer, which bridges this gap through:
1. A modality-bridging attention mechanism that enables visual grounding for cross-lingual transfer
2. A language-agnostic visual encoder that provides shared semantic anchors across languages  
3. A progressive training curriculum that gradually extends multimodal alignment from high-resource to low-resource languages

## 2. Related Work

**Multilingual Models:** XLM-R (Conneau et al., 2020) remains a strong baseline for cross-lingual transfer. More recent models including mT5 (Xue et al., 2021) and BLOOM (BigScience, 2022) have expanded language coverage but remain text-only.

**Vision-Language Models:** CLIP (Radford et al., 2021), ALIGN (Jia et al., 2021), and PaLI (Chen et al., 2023) demonstrate powerful multimodal representations but focus on English and a few high-resource languages.

**Cross-lingual Multimodal:** UC2 (Zhou et al., 2021) and xGQA (Pfeiffer et al., 2022) explore multilingual visual question answering. Our work differs by providing a general-purpose transfer framework rather than task-specific solutions.

## 3. Method

### 3.1 Architecture

MultiX-Transfer consists of three components:
- **Visual Encoder:** ViT-L/14 with 307M parameters, frozen during cross-lingual training
- **Text Encoder:** XLM-R-Large (560M parameters) with additional modality-bridging layers
- **Bridging Module:** 12-layer transformer (180M parameters) with cross-attention between visual and textual representations

Total parameter count: approximately 1.05 billion.

### 3.2 Modality-Bridging Mechanism

We introduce Modality-Bridging Attention (MBA), which computes cross-attention between visual tokens V and textual tokens T:

MBA(T, V) = softmax(T * W_q * (V * W_k)^T / sqrt(d)) * V * W_v

where W_q, W_k, W_v are learned projection matrices.

### 3.3 Training Procedure

Training proceeds in three stages:
1. **Stage 1 (Visual-English Alignment):** 2M English image-text pairs from CC3M
2. **Stage 2 (High-Resource Extension):** 800K pairs across 12 high-resource languages
3. **Stage 3 (Low-Resource Transfer):** Progressive distillation to 35 additional languages using translated captions

Total training compute: 256 A100 GPUs for 14 days (approximately 86,000 GPU-hours).

## 4. Experiments

### 4.1 Datasets and Tasks

We evaluate on 5 tasks:
- **XNLI:** Cross-lingual natural language inference (15 languages)
- **XQuAD:** Cross-lingual question answering (11 languages)
- **MARC:** Multilingual Amazon reviews classification (6 languages)
- **xGQA:** Cross-lingual visual question answering (7 languages)
- **MaRVL:** Multicultural visual reasoning (5 languages)

### 4.2 Main Results

| Model | XNLI | XQuAD | MARC | xGQA | MaRVL | Avg |
|-------|------|-------|------|------|-------|-----|
| XLM-R-Large | 79.2 | 76.4 | 68.3 | - | - | - |
| mBLIP | 78.8 | 75.1 | 67.9 | 58.4 | 62.1 | 68.5 |
| CCLM | 80.1 | 77.2 | 69.1 | 59.7 | 63.4 | 69.9 |
| MultiX-Transfer | **82.4** | **79.8** | **72.1** | **63.2** | **67.8** | **73.1** |

Average improvement over best baseline: +4.7%

### 4.3 Low-Resource Language Results

For the 10 lowest-resource languages in our evaluation:

| Model | Average Score | Improvement over XLM-R |
|-------|--------------|----------------------|
| XLM-R-Large | 61.4 | - |
| MultiX-Transfer | 69.6 | +8.2 |

### 4.4 Ablation Study

| Configuration | Avg Score |
|---------------|-----------|
| Full model | 73.1 |
| w/o MBA | 70.3 (-2.8) |
| w/o Stage 3 | 70.8 (-2.3) |
| w/o Visual Encoder | 69.2 (-3.9) |

## 5. Analysis

The modality-bridging mechanism proves most effective for languages with limited text-only training data. We hypothesize that visual grounding provides a universal semantic anchor that partially compensates for the lack of textual training signal.

Limitations:
- Training cost is substantial (86K GPU-hours)
- Performance gains for high-resource languages are modest (+2.1% average)
- Current framework does not incorporate audio modality

## 6. Conclusion

We present MultiX-Transfer, a framework for multimodal cross-lingual transfer that achieves state-of-the-art results across 5 tasks and 47 languages. Our modality-bridging mechanism demonstrates that visual grounding can significantly enhance cross-lingual transfer, particularly for low-resource languages.

## References

[1] Conneau et al. (2020). Unsupervised Cross-lingual Representation Learning at Scale. ACL.
[2] Xue et al. (2021). mT5: A Massively Multilingual Pre-trained Text-to-Text Transformer. NAACL.
[3] Radford et al. (2021). Learning Transferable Visual Models From Natural Language Supervision. ICML.
[4] Chen et al. (2023). PaLI: A Jointly-Scaled Multilingual Language-Image Model. ICLR.
[5] Zhou et al. (2021). UC2: Universal Cross-lingual Cross-modal Vision-and-Language Pre-training. CVPR.
[6] Pfeiffer et al. (2022). xGQA: Cross-Lingual Visual Question Answering. ACL Findings.
