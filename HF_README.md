---
title: Turkish Extended NER
emoji: ⭐
colorFrom: blue
colorTo: red
sdk: docker
app_file: Demo.py
pinned: false
license: mit
tags:
  - ner
  - turkish
  - nlp
  - crf
  - named-entity-recognition
short_description: Turkish Named Entity Recognition with 6 categories
---

# 🇹🇷 Extended Turkish NER (Genişletilmiş Türkçe Varlık İsim Tanıma)

This is a high-performance **Named Entity Recognition (NER)** model for Turkish, using a hybrid approach of **Conditional Random Fields (CRF)**, deep morphological analysis, and comprehensive gazetteers.

## Features
- **6 Extended Categories:** `PER` (Person), `LOC` (Location), `ORG` (Organization), `COMPANY`, `GROUP`, `MOVIE`
- **Hybrid Features:** Combines linguistic morphology with gazetteer-based features
- **High Performance:** 86.66% F1-Score on Gold Test Set

## Performance
| Metric | Value |
| :--- | :--- |
| **Best F1-Score** | **86.66%** |
| Precision | 87.42% |
| Recall | 85.91% |

## Usage
Enter any Turkish text and the model will identify and highlight named entities with their categories.

## Citation
If you use this model, please cite:
- [Academic Paper](https://github.com/WildGenie/nerextended/blob/master/docs/Akademik_Makale.md)
- [GitHub Repository](https://github.com/WildGenie/nerextended)
